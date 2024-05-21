
from cvat_sdk.api_client import models


def get_project_id(api_client, project_name, create=False):
    projects, response = api_client.projects_api.list()
    project_id = None
    for project in projects['results']:
        if project['name'] == project_name:
            project_id = project['id']
            break
    project_id = create_project(api_client, project_name) if create and project_id is None else project_id
    
    return project_id


def get_task_id(api_client, task_name, project_id, create=False):
    tasks, response = api_client.tasks_api.list()
    task_id = None
    for task in tasks['results']:
        if task['name'] == task_name:
            task_id = task['id']
            break
    task_id = create_task(api_client, task_name, project_id) if create and task_id is None else task_id

    return task_id


def get_label_map(api_client, project_id=None):
    labels, response = api_client.labels_api.list(page_size=100_000)
    label2id = {label['name'].lower(): label['id'] for label in labels['results'] if project_id == None or label['project_id'] == project_id}

    return label2id


def create_project(api_client, project_name):
    project_spec = models.ProjectWriteRequest(name=project_name)
    project_api, response = api_client.projects_api.create(project_spec)
    project_id = project_api.id

    return project_id


def create_task(api_client, task_name, project_id):
    task_spec = models.TaskWriteRequest(name=task_name, project_id=project_id)
    task_api, response = api_client.tasks_api.create(task_spec)
    task_id = task_api.id

    return task_id

