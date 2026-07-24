from __future__ import annotations

import json
from datetime import date
from typing import Any, TypeVar

from backend.app.core.dates import parse_datetime
from backend.app.models import (
    Concept,
    DailyTask,
    Document,
    DocumentChunk,
    DocumentStatus,
    DocumentType,
    GoalStatus,
    GoalType,
    LearningEvent,
    MemoryEntry,
    MemoryScope,
    MemoryStatus,
    MonthPlan,
    PlanStatus,
    PlanType,
    ResumeVersion,
    ReviewItem,
    ReviewStatus,
    SessionStatus,
    StudyGoal,
    StudySession,
    TaskStatus,
    TechStack,
    WeekPlan,
    WrongQuestion,
    WrongQuestionStatus,
    WorkArticle,
    WorkLearningRecord,
    WorkProject,
    YearPlan,
)

T = TypeVar("T")


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def loads(value: str) -> Any:
    return json.loads(value)


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def goal_from_payload(payload: dict[str, Any]) -> StudyGoal:
    return StudyGoal(
        user_id=payload["userId"],
        goal_name=payload["goalName"],
        subjects=tuple(payload.get("subjects", [])),
        current_level=payload.get("currentLevel", "unknown"),
        daily_available_minutes=int(payload.get("dailyAvailableMinutes", 60)),
        goal_type=GoalType(payload.get("goalType", "exam")),
        deadline=_date(payload.get("deadline")),
        description=payload.get("description", ""),
        exam_name=payload.get("examName"),
        priority=payload.get("priority", "medium"),
        status=GoalStatus(payload.get("status", "active")),
        id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]),
        updated_at=parse_datetime(payload["updatedAt"]),
    )


def year_plan_from_payload(payload: dict[str, Any]) -> YearPlan:
    return YearPlan(
        user_id=payload["userId"], goal_id=payload["goalId"], year=int(payload["year"]),
        title=payload["title"], plan_type=PlanType(payload.get("planType", "long_term")),
        status=PlanStatus(payload.get("status", "active")), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )


def month_plan_from_payload(payload: dict[str, Any]) -> MonthPlan:
    return MonthPlan(
        user_id=payload["userId"], goal_id=payload["goalId"], year_plan_id=payload["yearPlanId"],
        month=int(payload["month"]), title=payload["title"], focus=payload.get("focus", ""),
        plan_type=PlanType(payload.get("planType", "monthly")),
        status=PlanStatus(payload.get("status", "active")), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )


def week_plan_from_payload(payload: dict[str, Any]) -> WeekPlan:
    return WeekPlan(
        user_id=payload["userId"], goal_id=payload["goalId"], month_plan_id=payload["monthPlanId"],
        week_start=date.fromisoformat(payload["weekStart"]), week_end=date.fromisoformat(payload["weekEnd"]),
        title=payload["title"], focus=payload.get("focus", ""),
        plan_type=PlanType(payload.get("planType", "weekly")),
        status=PlanStatus(payload.get("status", "active")), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )


def task_from_payload(payload: dict[str, Any]) -> DailyTask:
    return DailyTask(
        user_id=payload["userId"], goal_id=payload["goalId"], week_plan_id=payload["weekPlanId"],
        subject=payload["subject"], topic=payload["topic"], task_date=date.fromisoformat(payload["taskDate"]),
        estimated_minutes=int(payload["estimatedMinutes"]), priority=payload.get("priority", "medium"),
        sort_order=int(payload.get("sortOrder", 0)),
        status=TaskStatus(payload.get("status", "pending")), id=payload["id"],
        completed_at=parse_datetime(payload["completedAt"]) if payload.get("completedAt") else None,
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )


def session_from_payload(payload: dict[str, Any]) -> StudySession:
    return StudySession(
        user_id=payload["userId"], subject=payload["subject"], topic=payload["topic"],
        start_time=parse_datetime(payload["startTime"]), task_id=payload.get("taskId"),
        end_time=parse_datetime(payload["endTime"]) if payload.get("endTime") else None,
        duration_minutes=int(payload.get("durationMinutes", 0)), notes=payload.get("notes", ""),
        feeling=payload.get("feeling", ""), status=SessionStatus(payload.get("status", "in_progress")),
        id=payload["id"], created_at=parse_datetime(payload["createdAt"]),
        updated_at=parse_datetime(payload["updatedAt"]),
    )


def event_from_payload(payload: dict[str, Any]) -> LearningEvent:
    return LearningEvent(
        user_id=payload["userId"], event_type=payload["eventType"], summary=payload["summary"],
        metadata=payload.get("metadata", {}), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]),
    )


def wrong_question_from_payload(payload: dict[str, Any]) -> WrongQuestion:
    return WrongQuestion(
        user_id=payload["userId"], goal_id=payload["goalId"], question=payload["question"],
        correct_answer=payload.get("correctAnswer", ""), explanation=payload.get("explanation", ""),
        subject=payload.get("subject", ""), topic=payload.get("topic", ""),
        status=WrongQuestionStatus(payload.get("status", "learning")),
        source_event_id=payload.get("sourceEventId"), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )


def review_item_from_payload(payload: dict[str, Any]) -> ReviewItem:
    return ReviewItem(
        user_id=payload["userId"], wrong_question_id=payload["wrongQuestionId"],
        stage=int(payload["stage"]), interval_days=int(payload["intervalDays"]),
        due_date=date.fromisoformat(payload["dueDate"]),
        status=ReviewStatus(payload.get("status", "pending")), result=payload.get("result"),
        completed_at=parse_datetime(payload["completedAt"]) if payload.get("completedAt") else None,
        id=payload["id"], created_at=parse_datetime(payload["createdAt"]),
        updated_at=parse_datetime(payload["updatedAt"]),
    )


def document_from_payload(payload: dict[str, Any]) -> Document:
    return Document(
        user_id=payload["userId"], file_name=payload["fileName"], file_type=DocumentType(payload["fileType"]),
        subject=payload["subject"], topic=payload["topic"], goal_id=payload.get("goalId"),
        planet_type=payload.get("planetType", "study"), tech_stack_id=payload.get("techStackId"),
        tags=tuple(payload.get("tags", [])), content=payload.get("content", ""),
        content_encoding=payload.get("contentEncoding", "text"), storage_path=payload.get("storagePath"),
        provider=payload.get("provider", "local"), provider_dataset_id=payload.get("providerDatasetId"),
        provider_document_id=payload.get("providerDocumentId"), provider_status=payload.get("providerStatus"),
        processing_status=DocumentStatus(payload.get("processingStatus", "uploaded")),
        error_message=payload.get("errorMessage"), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )


def chunk_from_payload(payload: dict[str, Any]) -> DocumentChunk:
    return DocumentChunk(
        user_id=payload["userId"], document_id=payload["documentId"], chunk_index=int(payload["chunkIndex"]),
        content=payload["content"], metadata=payload.get("metadata", {}), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]),
    )


def concept_from_payload(payload: dict[str, Any]) -> Concept:
    return Concept(
        user_id=payload["userId"], subject=payload["subject"], topic=payload["topic"], name=payload["name"],
        source=payload.get("source", "system_placeholder"), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]),
    )


def memory_from_payload(payload: dict[str, Any]) -> MemoryEntry:
    return MemoryEntry(
        user_id=payload["userId"], scope=MemoryScope(payload["scope"]), key=payload["key"],
        value=payload["value"], memory_type=payload.get("memoryType", "system"),
        status=MemoryStatus(payload.get("status", "active")), importance=int(payload.get("importance", 1)),
        planet_type=payload.get("planetType"), session_id=payload.get("sessionId"),
        metadata=payload.get("metadata", {}), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
        last_accessed_at=parse_datetime(payload["lastAccessedAt"]) if payload.get("lastAccessedAt") else None,
        expires_at=parse_datetime(payload["expiresAt"]) if payload.get("expiresAt") else None,
    )


def tech_stack_from_payload(payload: dict[str, Any]) -> TechStack:
    return TechStack(
        user_id=payload["userId"], name=payload["name"], category=payload["category"],
        proficiency=payload["proficiency"], description=payload.get("description", ""),
        tags=tuple(payload.get("tags", [])), status=payload.get("status", "active"), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )


def project_from_payload(payload: dict[str, Any]) -> WorkProject:
    return WorkProject(
        user_id=payload["userId"], title=payload["title"], description=payload.get("description", ""),
        tech_stack_ids=tuple(payload.get("techStackIds", [])), evidence_refs=tuple(payload.get("evidenceRefs", [])),
        status=payload.get("status", "draft"), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )


def article_from_payload(payload: dict[str, Any]) -> WorkArticle:
    return WorkArticle(
        user_id=payload["userId"], tech_stack_id=payload["techStackId"], title=payload["title"],
        content=payload.get("content", ""), article_type=payload.get("articleType", "knowledge"),
        summary=payload.get("summary", ""), tags=tuple(payload.get("tags", [])), status=payload.get("status", "draft"),
        id=payload["id"], created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )


def learning_record_from_payload(payload: dict[str, Any]) -> WorkLearningRecord:
    return WorkLearningRecord(
        user_id=payload["userId"], tech_stack_id=payload["techStackId"], title=payload["title"],
        notes=payload.get("notes", ""), minutes=int(payload.get("minutes", 0)), tags=tuple(payload.get("tags", [])),
        status=payload.get("status", "recorded"), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )


def resume_from_payload(payload: dict[str, Any]) -> ResumeVersion:
    return ResumeVersion(
        user_id=payload["userId"], role_target=payload["roleTarget"], title=payload["title"],
        content=payload.get("content", ""), evidence_refs=tuple(payload.get("evidenceRefs", [])),
        status=payload.get("status", "draft"), id=payload["id"],
        created_at=parse_datetime(payload["createdAt"]), updated_at=parse_datetime(payload["updatedAt"]),
    )
