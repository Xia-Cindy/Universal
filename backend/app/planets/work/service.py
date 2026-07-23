from backend.app.models import ResumeVersion, TechStack, WorkArticle, WorkLearningRecord, WorkProject
from backend.app.planets.work.repository import WorkRepository


class WorkService:
    def __init__(self, repository: WorkRepository) -> None:
        self._repository = repository

    def home(self, user_id: str, knowledge_summary: dict[str, object]) -> dict[str, object]:
        tech_stacks = self.list_tech_stacks(user_id)
        projects = self.list_projects(user_id)
        articles = self.list_articles(user_id)
        learning_records = self.list_learning_records(user_id)
        resumes = self.list_resumes(user_id)
        primary_action = (
            {
                "type": "create_tech_stack",
                "label": "Create Tech Stack",
                "route": "/work/tech-stack",
                "description": "Start by naming one capability you want to build evidence for.",
            }
            if not tech_stacks
            else {
                "type": "review_resume",
                "label": "Review Dynamic Resume",
                "route": "/work/resume",
                "description": "Turn your tech stack and evidence into a role-specific resume draft.",
            }
        )
        return {
            "state": "ready",
            "primaryAction": primary_action,
            "summary": {
                "techStackCount": len(tech_stacks),
                "projectCount": len(projects),
                "articleCount": len(articles),
                "learningRecordCount": len(learning_records),
                "resumeCount": len(resumes),
                "knowledgeDocumentCount": len(knowledge_summary.get("documents", [])),
            },
            "techStacks": tech_stacks,
            "projects": projects,
            "articles": articles,
            "learningRecords": learning_records,
            "resumes": resumes,
        }

    def create_tech_stack(self, user_id: str, payload: dict) -> dict[str, object]:
        tech_stack = TechStack(
            user_id=user_id,
            name=payload["name"],
            category=payload.get("category", "Engineering"),
            proficiency=payload.get("proficiency", "learning"),
            description=payload.get("description", ""),
            tags=tuple(payload.get("tags", [])),
            status=payload.get("status", "active"),
        )
        return self._repository.save_tech_stack(tech_stack).to_dict()

    def list_tech_stacks(self, user_id: str) -> list[dict[str, object]]:
        return [item.to_dict() for item in self._repository.list_tech_stacks(user_id)]

    def tech_stack_detail(self, user_id: str, tech_stack_id: str, knowledge_summary: dict[str, object]) -> dict[str, object]:
        tech_stack = self._repository.get_tech_stack(tech_stack_id, user_id)
        related_documents = [
            document
            for document in knowledge_summary.get("documents", [])
            if self._is_related_to_tech_stack(tech_stack.to_dict(), document)
        ]
        related_projects = [
            project
            for project in self.list_projects(user_id)
            if tech_stack.id in project.get("techStackIds", [])
        ]
        return {
            "techStack": tech_stack.to_dict(),
            "relatedKnowledge": related_documents,
            "projects": related_projects,
            "articles": self.list_articles(user_id, tech_stack_id=tech_stack.id),
            "learningRecords": self.list_learning_records(user_id, tech_stack_id=tech_stack.id),
            "resumeSnippets": self._resume_snippets(user_id, tech_stack.name),
        }

    def create_article(self, user_id: str, tech_stack_id: str, payload: dict) -> dict[str, object]:
        self._repository.get_tech_stack(tech_stack_id, user_id)
        article = WorkArticle(
            user_id=user_id,
            tech_stack_id=tech_stack_id,
            title=payload["title"],
            summary=payload.get("summary", ""),
            content=payload.get("content", ""),
            tags=tuple(payload.get("tags", [])),
            status=payload.get("status", "draft"),
        )
        return self._repository.save_article(article).to_dict()

    def list_articles(self, user_id: str, tech_stack_id: str | None = None) -> list[dict[str, object]]:
        return [item.to_dict() for item in self._repository.list_articles(user_id, tech_stack_id)]

    def create_learning_record(self, user_id: str, tech_stack_id: str, payload: dict) -> dict[str, object]:
        self._repository.get_tech_stack(tech_stack_id, user_id)
        record = WorkLearningRecord(
            user_id=user_id,
            tech_stack_id=tech_stack_id,
            title=payload["title"],
            notes=payload.get("notes", ""),
            minutes=int(payload.get("minutes", 0)),
            tags=tuple(payload.get("tags", [])),
            status=payload.get("status", "recorded"),
        )
        return self._repository.save_learning_record(record).to_dict()

    def list_learning_records(
        self,
        user_id: str,
        tech_stack_id: str | None = None,
    ) -> list[dict[str, object]]:
        return [item.to_dict() for item in self._repository.list_learning_records(user_id, tech_stack_id)]

    def create_project(self, user_id: str, payload: dict) -> dict[str, object]:
        for tech_stack_id in payload.get("techStackIds", []):
            self._repository.get_tech_stack(tech_stack_id, user_id)
        project = WorkProject(
            user_id=user_id,
            title=payload["title"],
            description=payload.get("description", ""),
            tech_stack_ids=tuple(payload.get("techStackIds", [])),
            evidence_refs=tuple(payload.get("evidenceRefs", [])),
            status=payload.get("status", "draft"),
        )
        return self._repository.save_project(project).to_dict()

    def list_projects(self, user_id: str) -> list[dict[str, object]]:
        return [item.to_dict() for item in self._repository.list_projects(user_id)]

    def create_resume_draft(self, user_id: str, payload: dict) -> dict[str, object]:
        role_target = payload.get("roleTarget", "AI Engineer")
        tech_stacks = self.list_tech_stacks(user_id)
        projects = self.list_projects(user_id)
        articles = self.list_articles(user_id)
        learning_records = self.list_learning_records(user_id)
        evidence_refs = [f"tech_stack:{item['id']}" for item in tech_stacks]
        evidence_refs.extend(f"project:{item['id']}" for item in projects)
        evidence_refs.extend(f"article:{item['id']}" for item in articles)
        evidence_refs.extend(f"learning_record:{item['id']}" for item in learning_records)
        content = self._resume_content(role_target=role_target, tech_stacks=tech_stacks, projects=projects)
        resume = ResumeVersion(
            user_id=user_id,
            role_target=role_target,
            title=f"{role_target} Resume Draft",
            content=content,
            evidence_refs=tuple(evidence_refs),
        )
        return self._repository.save_resume_version(resume).to_dict()

    def list_resumes(self, user_id: str) -> list[dict[str, object]]:
        return [item.to_dict() for item in self._repository.list_resume_versions(user_id)]

    def _resume_content(
        self,
        *,
        role_target: str,
        tech_stacks: list[dict[str, object]],
        projects: list[dict[str, object]],
    ) -> str:
        if not tech_stacks and not projects:
            return (
                f"{role_target} resume draft is not ready yet. "
                "Add Tech Stack and project evidence before generating role-specific content."
            )
        stack_names = ", ".join(str(item["name"]) for item in tech_stacks) or "pending skills"
        project_names = ", ".join(str(item["title"]) for item in projects) or "pending projects"
        return (
            f"Role target: {role_target}\n"
            f"Core tech stack: {stack_names}\n"
            f"Evidence projects: {project_names}\n"
            "Draft rule: only use user-confirmed Work Planet evidence."
        )

    def _resume_snippets(self, user_id: str, tech_stack_name: str) -> list[dict[str, object]]:
        snippets = []
        for resume in self.list_resumes(user_id):
            if tech_stack_name.lower() in str(resume.get("content", "")).lower():
                snippets.append(resume)
        return snippets

    def _is_related_to_tech_stack(self, tech_stack: dict[str, object], document: object) -> bool:
        if not isinstance(document, dict):
            return False
        if document.get("techStackId") == tech_stack.get("id"):
            return True
        haystack = " ".join(
            str(value)
            for value in (
                document.get("fileName"),
                document.get("subject"),
                document.get("topic"),
                " ".join(str(tag) for tag in document.get("tags", [])),
                " ".join(str(tag) for tag in tech_stack.get("tags", [])),
            )
        ).lower()
        needles = [str(tech_stack.get("name", "")).lower(), *[str(tag).lower() for tag in tech_stack.get("tags", [])]]
        return any(needle and needle in haystack for needle in needles)
