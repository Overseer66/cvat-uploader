
import os
import time
import argparse
from tqdm import tqdm
from utils.parser import parse_yolo
from utils.cvat_api import get_project_id, get_task_id, get_label_map
from cvat_sdk.api_client import Configuration, ApiClient, models


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host')
    parser.add_argument('--port')
    parser.add_argument('--token')
    parser.add_argument('--project_name')
    parser.add_argument('--task_name')
    parser.add_argument('--dataset_dir')
    parser.add_argument('--image_quality', default=70, type=int)
    parser.add_argument('--upload_image', action='store_true')
    parser.add_argument('--allow_create', action='store_true')
    args = parser.parse_args()

    # CVAT configuration
    configuration = Configuration(
        host='{host}:{port}'.format(host=args.host, port=args.port),
        api_key={'tokenAuth': args.token}
    )

    # CVAT API client
    with ApiClient(configuration) as api_client:
        # parsing
        dataset, names = parse_yolo(args.dataset_dir)

        # get project id
        project_id = get_project_id(api_client, args.project_name, args.allow_create)
        assert project_id is not None, 'Project not found'

        # check labels
        label2id = get_label_map(api_client)
        project_labels = get_label_map(api_client, project_id)
        labels = []
        for _, name in names.items():
            name = name.lower()
            if name not in project_labels:
                if name not in label2id:
                    labels.append(models.PatchedLabelRequest(
                        name=name,
                        type='rectangle',
                    ))
                else:
                    labels.append(models.PatchedLabelRequest(
                        id=label2id[name],
                        name=name,
                        type='rectangle',
                    ))

        # update labels
        api_client.projects_api.partial_update(
            project_id,
            patched_project_write_request=models.PatchedProjectWriteRequest(
                labels=labels
            )
        )

        # reload labels
        label2id = get_label_map(api_client, project_id)

        # get task id
        task_id = get_task_id(api_client, args.task_name, project_id, args.allow_create)

        # initialize upload
        if args.upload_image:
            # upload images
            bulk_size = 10
            idx = 0
            with tqdm(total=len(dataset), desc='Uploading images') as pbar:
                _, response = api_client.tasks_api.create_data(
                    task_id,
                    data_request=models.DataRequest(image_quality=args.image_quality),
                    upload_start=True
                )

                while idx < len(dataset):
                    bulk = list(dataset.keys())[idx:idx + bulk_size]
                    client_files = [open(dataset[key]['filepath'], 'rb') for key in bulk]

                    data_request = models.DataRequest(
                        image_quality=args.image_quality,
                        client_files=client_files,
                    )

                    _, response = api_client.tasks_api.create_data(
                        task_id,
                        data_request=data_request,
                        upload_multiple=True,
                        _content_type='multipart/form-data'
                    )
                    idx += bulk_size
                    pbar.update(bulk_size)

                _, response = api_client.tasks_api.create_data(
                    task_id,
                    data_request=models.DataRequest(image_quality=args.image_quality),
                    upload_finish=True
                )

        # waiting for CVAT task is ready
        tiktok = 0
        metadata, response = api_client.tasks_api.retrieve_data_meta(task_id)
        while len(metadata['frames']) == 0:
            print('\rWaiting for CVAT task is ready' + '.' * (tiktok % 5 + 1), end='')
            tiktok += 1
            # sleep 1 second
            time.sleep(5)
            metadata, response = api_client.tasks_api.retrieve_data_meta(task_id)
        print()

        # upload annotations
        with tqdm(total=len(metadata['frames']), desc='Uploading annotations') as pbar:
            for frame_idx, info in enumerate(metadata['frames']):
                file_name = os.path.splitext(info['name'])[0]
                data_info = dataset[file_name]
                annotation = models.PatchedLabeledDataRequest(
                    tags=[],
                    shapes=[
                        models.LabeledShapeRequest(
                            type=models.ShapeType('rectangle'),
                            points=data['xyxy'],
                            frame=frame_idx,
                            label_id=label2id[data['class'].lower()],
                        ) for data in data_info['labels']
                    ],
                    tracks=[]
                )
                api_client.tasks_api.partial_update_annotations(
                    'create',
                    task_id,
                    patched_labeled_data_request=annotation
                )
                pbar.update(1)


