# CVAT에 YOLO 데이터를 업로드하는 코드

### with docker
```bash
docker build . -t cvat_uploader:latest
docker run -v ${RESOURCE_DIR}:/workspace/resources --rm cvat_uploader:latest python yolo2cvat.py --host ${CVAT_HOST} --port ${CVAT_PORT} --token ${CVAT_TOKEN} --project_name ${PROJECT_NAME} --task_name ${TASK_NAME} --dataset_dir ${YOLO_DATASET_DIR} --allow_create --upload_image
```

### run
```bash
python yolo2cvat.py --host ${CVAT_HOST} --port ${CVAT_PORT} --token ${CVAT_TOKEN} --project_name ${PROJECT_NAME} --task_name ${TASK_NAME} --dataset_dir ${YOLO_DATASET_DIR} --allow_create --upload_image
```
example
```bash
docker run -v ./sample:/workspace/resources --rm cvat_uploader:latest python yolo2cvat.py --host {{HOST}} --port {{PORT}} --token {{TOKEN}} --project_name "Project Name 1" --task_name "Task Name 1" --dataset_dir "/workspace/resources/yolo" --allow_create --upload_image
```
