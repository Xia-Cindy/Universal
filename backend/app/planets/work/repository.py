from backend.app.models import ResumeVersion, TechStack, WorkProject


class WorkRepository:
    def __init__(self) -> None:
        self.tech_stacks: dict[str, TechStack] = {}
        self.projects: dict[str, WorkProject] = {}
        self.resume_versions: dict[str, ResumeVersion] = {}

    def save_tech_stack(self, tech_stack: TechStack) -> TechStack:
        self.tech_stacks[tech_stack.id] = tech_stack
        return tech_stack

    def get_tech_stack(self, tech_stack_id: str, user_id: str) -> TechStack:
        tech_stack = self.tech_stacks[tech_stack_id]
        if tech_stack.user_id != user_id:
            raise PermissionError("Tech Stack does not belong to user")
        return tech_stack

    def list_tech_stacks(self, user_id: str) -> list[TechStack]:
        return sorted(
            [item for item in self.tech_stacks.values() if item.user_id == user_id],
            key=lambda item: item.updated_at,
            reverse=True,
        )

    def save_project(self, project: WorkProject) -> WorkProject:
        self.projects[project.id] = project
        return project

    def list_projects(self, user_id: str) -> list[WorkProject]:
        return sorted(
            [item for item in self.projects.values() if item.user_id == user_id],
            key=lambda item: item.updated_at,
            reverse=True,
        )

    def save_resume_version(self, resume: ResumeVersion) -> ResumeVersion:
        self.resume_versions[resume.id] = resume
        return resume

    def list_resume_versions(self, user_id: str) -> list[ResumeVersion]:
        return sorted(
            [item for item in self.resume_versions.values() if item.user_id == user_id],
            key=lambda item: item.updated_at,
            reverse=True,
        )
