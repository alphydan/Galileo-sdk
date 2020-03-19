from datetime import datetime
from unittest import mock

from galileo_sdk.business.objects import Job
from galileo_sdk.business.objects.jobs import EJobStatus
from galileo_sdk.business.utils.generate_query_str import generate_query_str
from galileo_sdk.data.repositories.projects import ProjectsRepository
from galileo_sdk.mock_response import MockResponse

BACKEND = "http://BACKEND"
NAMESPACE = "/galileo/user_interface/v1"
PROJECT_ID = "project_id"
STATION_ID = "station_id"
MACHINE_ID = "machine_id"
QUERY_STR = generate_query_str(
    {"ids": ["id"], "names": ["name"], "user_ids": ["user_id"], "page": 1, "items": 25,}
)

# Arrange
settings_repo = mock.Mock()
settings_repo.get_settings().backend = f"{BACKEND}"
auth_provider = mock.Mock()
auth_provider.get_access_token.return_value = "ACCESS_TOKEN"
projects_repo = ProjectsRepository(settings_repo, auth_provider)


def mocked_requests_get(*args, **kwargs):
    if args[0] == f"{BACKEND}{NAMESPACE}/projects?{QUERY_STR}":
        return MockResponse(
            {
                "projects": [
                    {
                        "id": "id",
                        "name": "name",
                        "description": "description",
                        "source_storage_id": "source_storage_id",
                        "source_path": "source_path",
                        "destination_storage_id": "destination_storage_id",
                        "destination_path": "destination_path",
                        "user_id": "user_id",
                        "creation_timestamp": "creation_timestamp",
                    }
                ]
            },
            200,
        )

    return MockResponse(None, 404)


def mocked_requests_post(*args, **kwargs):
    if args[0] == f"{BACKEND}{NAMESPACE}/projects":
        return MockResponse(
            {
                "project": {
                    "id": "id",
                    "name": "name",
                    "description": "description",
                    "source_storage_id": "source_storage_id",
                    "source_path": "source_path",
                    "destination_storage_id": "destination_storage_id",
                    "destination_path": "destination_path",
                    "user_id": "user_id",
                    "creation_timestamp": "creation_timestamp",
                }
            },
            200,
        )
    elif args[0] == f"{BACKEND}{NAMESPACE}/projects/{PROJECT_ID}/files":
        return MockResponse(True, 200)
    elif args[0] == f"{BACKEND}{NAMESPACE}/projects/{PROJECT_ID}/jobs":
        return MockResponse(
            {
                "job": {
                    "jobid": "jobid",
                    "receiverid": "receiverid",
                    "project_id": "project_id",
                    "time_created": int(datetime.now().timestamp()),
                    "last_updated": int(datetime.now().timestamp()),
                    "status": "uploaded",
                    "container": "container",
                    "name": "name",
                    "stationid": "stationid",
                    "userid": "userid",
                    "state": "state",
                    "oaid": "oaid",
                    "pay_status": "pay_status",
                    "pay_interval": 1,
                    "total_runtime": 10000,
                    "archived": False,
                    "status_history": [
                        {
                            "timestamp": int(datetime.now().timestamp()),
                            "status": "uploaded",
                        }
                    ],
                }
            },
            200,
        )

    return MockResponse(None, 404)


@mock.patch("requests.get", side_effect=mocked_requests_get)
def test_list_projects(mocked_requests):
    r = projects_repo.list_projects(QUERY_STR)

    # Act
    mocked_requests.assert_called_once_with(
        f"{BACKEND}{NAMESPACE}/projects?{QUERY_STR}",
        headers={"Authorization": f"Bearer ACCESS_TOKEN"},
        json=None,
    )

    assert len(r) == 1
    assert r[0].project_id == "id"
    assert r[0].user_id == "user_id"
    assert r[0].name == "name"


@mock.patch("requests.post", side_effect=mocked_requests_post)
def tests_create_project(mocked_requests):
    r = projects_repo.create_project("name", "description")

    # Act
    mocked_requests.assert_called_once_with(
        f"{BACKEND}{NAMESPACE}/projects",
        headers={"Authorization": f"Bearer ACCESS_TOKEN"},
        json={"name": "name", "description": "description"},
    )

    assert r.project_id == "id"
    assert r.name == "name"
    assert r.description == "description"


@mock.patch("requests.post", side_effect=mocked_requests_post)
def tests_upload_file(mocked_requests):
    open("test_upload_file.txt", "wb")
    filename = "test_upload_file.txt"
    file = {"upload_file": open(filename, "rb")}
    r = projects_repo.upload_single_file(PROJECT_ID, file, filename)

    assert r is True


@mock.patch("requests.post", side_effect=mocked_requests_post)
def test_run_job_on_station(mocked_requests):
    r = projects_repo.run_job_on_station(PROJECT_ID, STATION_ID)

    # Act
    mocked_requests.assert_called_once_with(
        f"{BACKEND}{NAMESPACE}/projects/{PROJECT_ID}/jobs",
        headers={"Authorization": f"Bearer ACCESS_TOKEN"},
        json={"station_id": STATION_ID},
    )

    assert isinstance(r, Job)


@mock.patch("requests.post", side_effect=mocked_requests_post)
def test_run_job_on_machine(mocked_requests):
    r = projects_repo.run_job_on_machine(PROJECT_ID, STATION_ID, MACHINE_ID)

    # Act
    mocked_requests.assert_called_once_with(
        f"{BACKEND}{NAMESPACE}/projects/{PROJECT_ID}/jobs",
        headers={"Authorization": f"Bearer ACCESS_TOKEN"},
        json={"station_id": STATION_ID, "machine_id": MACHINE_ID},
    )

    assert isinstance(r, Job)
    assert r.project_id == "project_id"
    assert r.job_id == "jobid"
    assert len(r.status_history) == 1
    assert r.status_history[0].status == EJobStatus.uploaded
