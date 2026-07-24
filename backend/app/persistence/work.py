from __future__ import annotations

import json

from backend.app.models import ResumeVersion, TechStack, WorkArticle, WorkLearningRecord, WorkProject
from backend.app.persistence.codec import (
    article_from_payload,
    dumps,
    learning_record_from_payload,
    project_from_payload,
    resume_from_payload,
    tech_stack_from_payload,
)
from backend.app.persistence.sqlite import SQLitePersistence


class SQLiteWorkRepository:
    def __init__(self, persistence: SQLitePersistence) -> None:
        self._db = persistence

    def save_tech_stack(self, tech_stack: TechStack) -> TechStack:
        return self._save("tech_stack", tech_stack.id, tech_stack.user_id, tech_stack.to_dict(), tech_stack.created_at.isoformat(), tech_stack.updated_at.isoformat())

    def delete_tech_stack(self, tech_stack_id: str, user_id: str) -> TechStack:
        tech_stack = self.get_tech_stack(tech_stack_id, user_id)
        tech_stack.status = "archived"
        return self.save_tech_stack(tech_stack)

    def get_tech_stack(self, tech_stack_id: str, user_id: str) -> TechStack:
        return tech_stack_from_payload(self._get("tech_stack", tech_stack_id, user_id))

    def list_tech_stacks(self, user_id: str) -> list[TechStack]:
        return [tech_stack_from_payload(item) for item in self._list("tech_stack", user_id) if item.get("status") != "archived"]

    def save_project(self, project: WorkProject) -> WorkProject:
        return self._save("project", project.id, project.user_id, project.to_dict(), project.created_at.isoformat(), project.updated_at.isoformat())

    def list_projects(self, user_id: str) -> list[WorkProject]:
        return [project_from_payload(item) for item in self._list("project", user_id)]

    def save_article(self, article: WorkArticle) -> WorkArticle:
        return self._save("article", article.id, article.user_id, article.to_dict(), article.created_at.isoformat(), article.updated_at.isoformat(), article.tech_stack_id)

    def list_articles(self, user_id: str, tech_stack_id: str | None = None) -> list[WorkArticle]:
        return [article_from_payload(item) for item in self._list("article", user_id, tech_stack_id)]

    def save_learning_record(self, record: WorkLearningRecord) -> WorkLearningRecord:
        return self._save("learning_record", record.id, record.user_id, record.to_dict(), record.created_at.isoformat(), record.updated_at.isoformat(), record.tech_stack_id)

    def list_learning_records(self, user_id: str, tech_stack_id: str | None = None) -> list[WorkLearningRecord]:
        return [learning_record_from_payload(item) for item in self._list("learning_record", user_id, tech_stack_id)]

    def save_resume_version(self, resume: ResumeVersion) -> ResumeVersion:
        return self._save("resume", resume.id, resume.user_id, resume.to_dict(), resume.created_at.isoformat(), resume.updated_at.isoformat())

    def list_resume_versions(self, user_id: str) -> list[ResumeVersion]:
        return [resume_from_payload(item) for item in self._list("resume", user_id)]

    def _save(self, record_type: str, record_id: str, user_id: str, payload: dict, created_at: str, updated_at: str, tech_stack_id: str | None = None):
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO work_records(id,user_id,record_type,tech_stack_id,payload,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                   tech_stack_id=excluded.tech_stack_id,payload=excluded.payload,updated_at=excluded.updated_at""",
                (record_id, user_id, record_type, tech_stack_id, dumps(payload), created_at, updated_at),
            )
        return payload_to_model(record_type, payload)

    def _get(self, record_type: str, record_id: str, user_id: str) -> dict:
        row = self._db.connection.execute(
            "SELECT payload FROM work_records WHERE id = ? AND record_type = ?", (record_id, record_type)
        ).fetchone()
        if not row:
            raise KeyError(record_id)
        payload = json.loads(row["payload"])
        if payload.get("userId") != user_id:
            raise PermissionError("Work record does not belong to user")
        return payload

    def _list(self, record_type: str, user_id: str, tech_stack_id: str | None = None) -> list[dict]:
        query = "SELECT payload FROM work_records WHERE user_id = ? AND record_type = ?"
        params: list[object] = [user_id, record_type]
        if tech_stack_id:
            query += " AND tech_stack_id = ?"
            params.append(tech_stack_id)
        query += " ORDER BY updated_at DESC"
        return [json.loads(row["payload"]) for row in self._db.connection.execute(query, params).fetchall()]


def payload_to_model(record_type: str, payload: dict):
    return {
        "tech_stack": tech_stack_from_payload,
        "project": project_from_payload,
        "article": article_from_payload,
        "learning_record": learning_record_from_payload,
        "resume": resume_from_payload,
    }[record_type](payload)
