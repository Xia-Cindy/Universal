from backend.app.models import ResumeVersion, TechStack, WorkArticle, WorkLearningRecord, WorkProject


class WorkRepository:
    def __init__(self) -> None:
        self.tech_stacks: dict[str, TechStack] = {}
        self.projects: dict[str, WorkProject] = {}
        self.articles: dict[str, WorkArticle] = {}
        self.learning_records: dict[str, WorkLearningRecord] = {}
        self.resume_versions: dict[str, ResumeVersion] = {}

    def save_tech_stack(self, tech_stack: TechStack) -> TechStack:
        self.tech_stacks[tech_stack.id] = tech_stack
        return tech_stack

    def delete_tech_stack(self, tech_stack_id: str, user_id: str) -> TechStack:
        tech_stack = self.get_tech_stack(tech_stack_id, user_id)
        tech_stack.status = "archived"
        return self.save_tech_stack(tech_stack)

    def get_tech_stack(self, tech_stack_id: str, user_id: str) -> TechStack:
        tech_stack = self.tech_stacks[tech_stack_id]
        if tech_stack.user_id != user_id:
            raise PermissionError("Tech Stack does not belong to user")
        return tech_stack

    def list_tech_stacks(self, user_id: str) -> list[TechStack]:
        return sorted(
            [item for item in self.tech_stacks.values() if item.user_id == user_id and item.status != "archived"],
            key=lambda item: item.created_at,
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

    def save_article(self, article: WorkArticle) -> WorkArticle:
        self.articles[article.id] = article
        return article

    def list_articles(self, user_id: str, tech_stack_id: str | None = None) -> list[WorkArticle]:
        articles = [item for item in self.articles.values() if item.user_id == user_id]
        if tech_stack_id:
            articles = [item for item in articles if item.tech_stack_id == tech_stack_id]
        return sorted(articles, key=lambda item: item.updated_at, reverse=True)

    def save_learning_record(self, record: WorkLearningRecord) -> WorkLearningRecord:
        self.learning_records[record.id] = record
        return record

    def list_learning_records(
        self,
        user_id: str,
        tech_stack_id: str | None = None,
    ) -> list[WorkLearningRecord]:
        records = [item for item in self.learning_records.values() if item.user_id == user_id]
        if tech_stack_id:
            records = [item for item in records if item.tech_stack_id == tech_stack_id]
        return sorted(records, key=lambda item: item.updated_at, reverse=True)

    def save_resume_version(self, resume: ResumeVersion) -> ResumeVersion:
        self.resume_versions[resume.id] = resume
        return resume

    def list_resume_versions(self, user_id: str) -> list[ResumeVersion]:
        return sorted(
            [item for item in self.resume_versions.values() if item.user_id == user_id],
            key=lambda item: item.updated_at,
            reverse=True,
        )
