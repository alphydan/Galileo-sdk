from typing import Any, List, Optional

from ...data.repositories.projects import ProjectsRepository
from ..utils.generate_query_str import generate_query_str


class ProjectsService:
    def __init__(self, projects_repo: ProjectsRepository):
        self._projects_repo = projects_repo

    def list_projects(
        self,
        ids: Optional[List[str]] = None,
        names: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        page: Optional[int] = 1,
        items: Optional[int] = 25,
    ):
        query = generate_query_str(
            {
                "ids": ids,
                "names": names,
                "user_ids": user_ids,
                "page": page,
                "items": items,
            }
        )

        r = self._projects_repo.list_projects(query)
        return r.json()

    def create_project(self, name: str, description: str):
        r = self._projects_repo.create_project(name, description)
        return r.json()

    def upload_single_file(self, project_id: str, file: Any):
        r = self._projects_repo.upload_single_file(project_id, file)
        return r.json()

    def run_job_on_station(self, project_id: str, station_id: str):
        r = self._projects_repo.run_job_on_station(project_id, station_id)
        return r.json()

    def run_job_on_machine(self, project_id: str, station_id: str, machine_id: str):
        r = self._projects_repo.run_job_on_machine(project_id, station_id, machine_id)
        return r.json()
