from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from backend.app.core.dates import local_now


class GoalStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class GoalType(StrEnum):
    EXAM = "exam"
    LEARNING = "learning"
    GROWTH = "growth"


class PlanStatus(StrEnum):
    ACTIVE = "active"
    DRAFT = "draft"
    COMPLETED = "completed"


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class SessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


def _id() -> str:
    return str(uuid4())


@dataclass
class StudyGoal:
    user_id: str
    goal_name: str
    subjects: tuple[str, ...]
    current_level: str
    daily_available_minutes: int
    goal_type: GoalType = GoalType.EXAM
    deadline: date | None = None
    description: str = ""
    exam_name: str | None = None
    priority: str = "medium"
    status: GoalStatus = GoalStatus.ACTIVE
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "goalType": self.goal_type.value,
            "goalName": self.goal_name,
            "examName": self.exam_name,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "description": self.description,
            "subjects": list(self.subjects),
            "currentLevel": self.current_level,
            "dailyAvailableMinutes": self.daily_available_minutes,
            "priority": self.priority,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class YearPlan:
    user_id: str
    goal_id: str
    year: int
    title: str
    status: PlanStatus = PlanStatus.ACTIVE
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "goalId": self.goal_id,
            "year": self.year,
            "title": self.title,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class MonthPlan:
    user_id: str
    goal_id: str
    year_plan_id: str
    month: int
    title: str
    focus: str
    status: PlanStatus = PlanStatus.ACTIVE
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "goalId": self.goal_id,
            "yearPlanId": self.year_plan_id,
            "month": self.month,
            "title": self.title,
            "focus": self.focus,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class WeekPlan:
    user_id: str
    goal_id: str
    month_plan_id: str
    week_start: date
    week_end: date
    title: str
    focus: str
    status: PlanStatus = PlanStatus.ACTIVE
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "goalId": self.goal_id,
            "monthPlanId": self.month_plan_id,
            "weekStart": self.week_start.isoformat(),
            "weekEnd": self.week_end.isoformat(),
            "title": self.title,
            "focus": self.focus,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class DailyTask:
    user_id: str
    goal_id: str
    week_plan_id: str
    subject: str
    topic: str
    task_date: date
    estimated_minutes: int
    status: TaskStatus = TaskStatus.PENDING
    id: str = field(default_factory=_id)
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "goalId": self.goal_id,
            "weekPlanId": self.week_plan_id,
            "subject": self.subject,
            "topic": self.topic,
            "taskDate": self.task_date.isoformat(),
            "estimatedMinutes": self.estimated_minutes,
            "status": self.status.value,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class StudySession:
    user_id: str
    subject: str
    topic: str
    start_time: datetime
    task_id: str | None = None
    end_time: datetime | None = None
    duration_minutes: int = 0
    notes: str = ""
    feeling: str = ""
    status: SessionStatus = SessionStatus.IN_PROGRESS
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)
    updated_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "taskId": self.task_id,
            "subject": self.subject,
            "topic": self.topic,
            "startTime": self.start_time.isoformat(),
            "endTime": self.end_time.isoformat() if self.end_time else None,
            "durationMinutes": self.duration_minutes,
            "notes": self.notes,
            "feeling": self.feeling,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


@dataclass
class LearningEvent:
    user_id: str
    event_type: str
    summary: str
    metadata: dict[str, Any]
    id: str = field(default_factory=_id)
    created_at: datetime = field(default_factory=local_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "eventType": self.event_type,
            "summary": self.summary,
            "metadata": self.metadata,
            "createdAt": self.created_at.isoformat(),
        }
