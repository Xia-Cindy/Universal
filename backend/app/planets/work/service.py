import re

from backend.app.models import (
    WORK_CASE_STAGES,
    WORK_CASE_STATUSES,
    PracticeCase,
    ResumeVersion,
    TechStack,
    WorkArticle,
    WorkLearningRecord,
    WorkProject,
)
from backend.app.planets.work.repository import WorkRepository
from backend.app.core.dates import local_now


class WorkService:
    _MAX_IMAGE_ATTACHMENTS = 4
    _MAX_IMAGE_DATA_URL_LENGTH = 1_500_000
    _IMAGE_DATA_URL = re.compile(r"^data:image/(?:png|jpeg|webp|gif);base64,[A-Za-z0-9+/=]+$")

    def __init__(self, repository: WorkRepository) -> None:
        self._repository = repository

    def home(self, user_id: str, knowledge_summary: dict[str, object]) -> dict[str, object]:
        cases = self.list_practice_cases(user_id)
        active_case = next((case for case in cases if case["status"] == "active"), None)
        tech_stacks = self.list_tech_stacks(user_id)
        projects = self.list_projects(user_id)
        articles = self.list_articles(user_id)
        learning_records = self.list_learning_records(user_id)
        resumes = self.list_resumes(user_id)
        next_action = self._next_action(active_case)
        return {
            "state": "ready",
            "primaryAction": next_action,
            "activeCase": active_case,
            "currentStage": active_case["currentStage"] if active_case else None,
            "nextAction": next_action,
            "caseProgress": self._case_progress(active_case) if active_case else self._empty_case_progress(),
            "summary": {
                "caseCount": len(cases),
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
            "relatedBookshelfContent": [],
            "activeLabs": [],
            "operationsAttention": [],
        }

    def create_practice_case(self, user_id: str, payload: dict) -> dict[str, object]:
        title = str(payload.get("title", "")).strip()
        if not title:
            raise ValueError("Practice Case title is required")
        status = self._case_status(payload.get("status", "active"))
        case = PracticeCase(
            user_id=user_id,
            title=title,
            problem=self._text(payload, "problem"),
            goal=self._text(payload, "goal"),
            scope=self._text(payload, "scope"),
            non_goal=self._text(payload, "nonGoal"),
            status=status,
            current_stage=self._case_stage(payload.get("currentStage", "discover")),
            success_metrics=self._string_list(payload.get("successMetrics", [])),
            risks=self._string_list(payload.get("risks", [])),
            dependencies=self._string_list(payload.get("dependencies", [])),
        )
        if case.status == "active":
            self._pause_other_active_cases(user_id, except_case_id=case.id)
        return self._case_view(self._repository.save_practice_case(case))

    def list_practice_cases(self, user_id: str) -> list[dict[str, object]]:
        return [self._case_view(case) for case in self._repository.list_practice_cases(user_id)]

    def get_practice_case(self, user_id: str, case_id: str) -> dict[str, object]:
        return self._case_view(self._repository.get_practice_case(case_id, user_id))

    def update_practice_case(self, user_id: str, case_id: str, payload: dict) -> dict[str, object]:
        case = self._repository.get_practice_case(case_id, user_id)
        for field, key in (
            ("title", "title"),
            ("problem", "problem"),
            ("goal", "goal"),
            ("scope", "scope"),
            ("non_goal", "nonGoal"),
        ):
            if key in payload:
                value = self._text(payload, key)
                if field == "title" and not value:
                    raise ValueError("Practice Case title is required")
                setattr(case, field, value)
        if "successMetrics" in payload:
            case.success_metrics = self._string_list(payload["successMetrics"])
        if "risks" in payload:
            case.risks = self._string_list(payload["risks"])
        if "dependencies" in payload:
            case.dependencies = self._string_list(payload["dependencies"])
        if "currentStage" in payload:
            next_stage = self._case_stage(payload["currentStage"])
            current_index = WORK_CASE_STAGES.index(case.current_stage)
            next_index = WORK_CASE_STAGES.index(next_stage)
            if next_index > current_index + 1:
                raise ValueError("Practice Case stages must advance one stage at a time")
            case.current_stage = next_stage
        if "status" in payload:
            case.status = self._case_status(payload["status"])
        if case.status == "active":
            self._pause_other_active_cases(user_id, except_case_id=case.id)
        case.updated_at = local_now()
        return self._case_view(self._repository.save_practice_case(case))

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

    def update_tech_stack(self, user_id: str, tech_stack_id: str, payload: dict) -> dict[str, object]:
        tech_stack = self._repository.get_tech_stack(tech_stack_id, user_id)
        if "name" in payload:
            tech_stack.name = str(payload["name"]).strip() or tech_stack.name
        if "category" in payload:
            tech_stack.category = str(payload["category"]).strip() or tech_stack.category
        if "proficiency" in payload:
            tech_stack.proficiency = str(payload["proficiency"]).strip() or tech_stack.proficiency
        if "description" in payload:
            tech_stack.description = str(payload.get("description", ""))
        if "tags" in payload:
            tech_stack.tags = tuple(str(tag).strip() for tag in payload.get("tags", []) if str(tag).strip())
        if "status" in payload:
            tech_stack.status = str(payload["status"]).strip() or tech_stack.status
        tech_stack.updated_at = local_now()
        return self._repository.save_tech_stack(tech_stack).to_dict()

    def archive_tech_stack(self, user_id: str, tech_stack_id: str) -> dict[str, object]:
        tech_stack = self._repository.delete_tech_stack(tech_stack_id, user_id)
        tech_stack.updated_at = local_now()
        return tech_stack.to_dict()

    def tech_stack_detail(self, user_id: str, tech_stack_id: str, knowledge_summary: dict[str, object]) -> dict[str, object]:
        tech_stack = self._repository.get_tech_stack(tech_stack_id, user_id)
        if tech_stack.status == "archived":
            raise ValueError("Tech Stack is archived")
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
        content = payload.get("content", "")
        outline = payload.get("outline", "")
        chapters = payload.get("chapters", [])
        if chapters:
            content = self._compose_article_content(content=content, outline=outline, chapters=chapters)
        article = WorkArticle(
            user_id=user_id,
            tech_stack_id=tech_stack_id,
            title=payload["title"],
            article_type=payload.get("articleType", "knowledge"),
            summary=payload.get("summary", ""),
            content=content,
            tags=tuple(payload.get("tags", [])),
            attachments=self._image_attachments(payload),
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
            attachments=self._image_attachments(payload),
            status=payload.get("status", "recorded"),
        )
        return self._repository.save_learning_record(record).to_dict()

    def list_learning_records(
        self,
        user_id: str,
        tech_stack_id: str | None = None,
    ) -> list[dict[str, object]]:
        return [item.to_dict() for item in self._repository.list_learning_records(user_id, tech_stack_id)]

    def _image_attachments(self, payload: dict) -> tuple[str, ...]:
        """Allow a small, private screenshot set without accepting executable data URLs."""
        attachments = payload.get("attachments", [])
        if not isinstance(attachments, (list, tuple)):
            raise ValueError("Image attachments must be a list")
        if len(attachments) > self._MAX_IMAGE_ATTACHMENTS:
            raise ValueError(f"A technical entry can include at most {self._MAX_IMAGE_ATTACHMENTS} images")
        normalized: list[str] = []
        for attachment in attachments:
            if not isinstance(attachment, str) or len(attachment) > self._MAX_IMAGE_DATA_URL_LENGTH:
                raise ValueError("Each pasted image is too large")
            if not self._IMAGE_DATA_URL.fullmatch(attachment):
                raise ValueError("Only base64 PNG, JPEG, WebP, or GIF images are allowed")
            normalized.append(attachment)
        return tuple(normalized)

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

    def _compose_article_content(self, *, content: str, outline: str, chapters: list[object]) -> str:
        blocks = []
        if outline.strip():
            blocks.append(f"## 大纲\n\n{outline.strip()}")
        for index, chapter in enumerate(chapters, start=1):
            if not isinstance(chapter, dict):
                continue
            title = str(chapter.get("title", "")).strip() or f"章节 {index}"
            body = str(chapter.get("body", "")).strip()
            blocks.append(f"## {title}\n\n{body}".strip())
        if content.strip():
            blocks.append(content.strip())
        return "\n\n".join(block for block in blocks if block)

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
        if any(
            grant.get("techStackId") == tech_stack.get("id")
            for grant in document.get("shareGrants", [])
            if isinstance(grant, dict)
        ):
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

    def _pause_other_active_cases(self, user_id: str, *, except_case_id: str) -> None:
        for item in self._repository.list_practice_cases(user_id):
            if item.id == except_case_id or item.status != "active":
                continue
            item.status = "paused"
            item.updated_at = local_now()
            self._repository.save_practice_case(item)

    def _case_view(self, case: PracticeCase) -> dict[str, object]:
        payload = case.to_dict()
        payload["progress"] = self._case_progress(payload)
        payload["nextAction"] = self._next_action(payload)
        return payload

    def _case_progress(self, case: dict[str, object] | None) -> dict[str, object]:
        if not case:
            return self._empty_case_progress()
        stage_index = WORK_CASE_STAGES.index(str(case["currentStage"]))
        return {
            "completedStages": stage_index,
            "totalStages": len(WORK_CASE_STAGES),
            "ratio": round(stage_index / (len(WORK_CASE_STAGES) - 1), 2),
            "stages": list(WORK_CASE_STAGES),
        }

    def _empty_case_progress(self) -> dict[str, object]:
        return {
            "completedStages": 0,
            "totalStages": len(WORK_CASE_STAGES),
            "ratio": 0,
            "stages": list(WORK_CASE_STAGES),
        }

    def _next_action(self, case: dict[str, object] | None) -> dict[str, object]:
        if not case:
            return {
                "type": "create_practice_case",
                "label": "Create Practice Case",
                "route": "/work/cases",
                "target": "/work/cases",
                "description": "Start with one real professional problem to investigate and validate.",
            }
        route = f"/work/cases/{case['id']}"
        if case["status"] == "draft":
            return {
                "type": "activate_practice_case",
                "label": "Activate Practice Case",
                "route": route,
                "target": route,
                "description": "Confirm this case as the one currently driving your Work practice.",
            }
        stage = str(case["currentStage"])
        label = {
            "discover": "Complete case brief",
            "define": "Continue definition",
            "govern": "Review governance needs",
            "validate": "Prepare validation",
            "operate": "Record operations readiness",
            "review": "Capture review lessons",
        }[stage]
        return {
            "type": "continue_case_stage",
            "label": label,
            "route": route,
            "target": route,
            "description": f"Current stage: {stage}. Continue from the Case workspace; later phases add its dedicated module.",
        }

    def _case_stage(self, value: object) -> str:
        stage = str(value).strip().lower()
        if stage not in WORK_CASE_STAGES:
            raise ValueError(f"Unsupported Practice Case stage: {value}")
        return stage

    def _case_status(self, value: object) -> str:
        status = str(value).strip().lower()
        if status not in WORK_CASE_STATUSES:
            raise ValueError(f"Unsupported Practice Case status: {value}")
        return status

    def _text(self, payload: dict, key: str) -> str:
        return str(payload.get(key, "")).strip()

    def _string_list(self, value: object) -> tuple[str, ...]:
        if not isinstance(value, (list, tuple)):
            raise ValueError("Practice Case list fields must be arrays")
        return tuple(str(item).strip() for item in value if str(item).strip())
