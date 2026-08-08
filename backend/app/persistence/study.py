from __future__ import annotations

from datetime import date

from backend.app.models import (
    DailyTask,
    LearningEvent,
    ReviewItem,
    WrongQuestion,
    WordEntry,
    MonthPlan,
    PlanStatus,
    SessionStatus,
    StudyGoal,
    StudySession,
    TaskStatus,
    WeekPlan,
    YearPlan,
)
from backend.app.persistence.codec import (
    dumps,
    loads,
    event_from_payload,
    review_item_from_payload,
    goal_from_payload,
    month_plan_from_payload,
    session_from_payload,
    task_from_payload,
    week_plan_from_payload,
    year_plan_from_payload,
    wrong_question_from_payload,
    word_entry_from_payload,
)
from backend.app.persistence.sqlite import SQLitePersistence


class SQLiteStudyRepository:
    """SQLite implementation of the existing StudyRepository contract."""

    def __init__(self, persistence: SQLitePersistence) -> None:
        self._db = persistence

    def save_goal(self, goal: StudyGoal) -> StudyGoal:
        payload = goal.to_dict()
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO study_goals
                (id,user_id,goal_name,goal_type,exam_name,deadline,description,subjects,
                 current_level,daily_available_minutes,priority,status,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                goal_name=excluded.goal_name,goal_type=excluded.goal_type,exam_name=excluded.exam_name,
                deadline=excluded.deadline,description=excluded.description,subjects=excluded.subjects,
                current_level=excluded.current_level,daily_available_minutes=excluded.daily_available_minutes,
                priority=excluded.priority,status=excluded.status,updated_at=excluded.updated_at""",
                (
                    goal.id, goal.user_id, goal.goal_name, goal.goal_type.value, goal.exam_name,
                    payload["deadline"], goal.description, dumps(payload["subjects"]), goal.current_level,
                    goal.daily_available_minutes, goal.priority, goal.status.value, payload["createdAt"], payload["updatedAt"],
                ),
            )
        return goal

    def get_goal(self, goal_id: str, user_id: str) -> StudyGoal:
        row = self._db.connection.execute(
            "SELECT * FROM study_goals WHERE id = ?", (goal_id,)
        ).fetchone()
        if not row or row["user_id"] != user_id:
            raise PermissionError("Goal does not belong to user")
        return self._goal_row(row)

    def get_active_goal(self, user_id: str) -> StudyGoal | None:
        row = self._db.connection.execute(
            """SELECT g.* FROM user_planet_context c
               JOIN study_goals g ON g.id = c.current_goal_id
               WHERE c.user_id = ? AND c.planet_type = 'study'""",
            (user_id,),
        ).fetchone()
        if row and row["status"] == "active":
            return self._goal_row(row)
        row = self._db.connection.execute(
            "SELECT * FROM study_goals WHERE user_id = ? AND status = 'active' ORDER BY updated_at DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        if not row:
            return None
        goal = self._goal_row(row)
        self.set_current_goal(user_id, goal.id)
        return goal

    def set_current_goal(self, user_id: str, goal_id: str) -> StudyGoal:
        goal = self.get_goal(goal_id, user_id)
        if goal.status.value != "active":
            raise ValueError("Cannot switch to an archived goal")
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO user_planet_context(user_id,planet_type,current_goal_id,updated_at)
                   VALUES(?, 'study', ?, ?)
                   ON CONFLICT(user_id,planet_type) DO UPDATE SET
                   current_goal_id=excluded.current_goal_id,updated_at=excluded.updated_at""",
                (user_id, goal.id, goal.updated_at.isoformat()),
            )
        return goal

    def list_goals(self, user_id: str) -> list[StudyGoal]:
        rows = self._db.connection.execute(
            "SELECT * FROM study_goals WHERE user_id = ? ORDER BY updated_at DESC", (user_id,)
        ).fetchall()
        return [self._goal_row(row) for row in rows]

    def save_year_plan(self, plan: YearPlan) -> YearPlan:
        self._save_plan(plan, year=plan.year)
        return plan

    def save_month_plan(self, plan: MonthPlan) -> MonthPlan:
        self._save_plan(plan, parent_id=plan.year_plan_id, month=plan.month)
        return plan

    def save_week_plan(self, plan: WeekPlan) -> WeekPlan:
        self._save_plan(
            plan,
            parent_id=plan.month_plan_id,
            week_start=plan.week_start.isoformat(),
            week_end=plan.week_end.isoformat(),
        )
        return plan

    def save_daily_task(self, task: DailyTask) -> DailyTask:
        payload = task.to_dict()
        with self._db.transaction() as db:
            self._ensure_postgres_task_parent_anchors(db, task)
            db.execute(
                """INSERT INTO daily_tasks
                (id,user_id,goal_id,week_plan_id,subject,topic,task_date,estimated_minutes,priority,sort_order,status,
                 completed_at,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET subject=excluded.subject,topic=excluded.topic,
                task_date=excluded.task_date,estimated_minutes=excluded.estimated_minutes,priority=excluded.priority,
                sort_order=excluded.sort_order,
                status=excluded.status,completed_at=excluded.completed_at,updated_at=excluded.updated_at""",
                (
                    task.id, task.user_id, task.goal_id, task.week_plan_id, task.subject, task.topic,
                    payload["taskDate"], task.estimated_minutes, task.priority, task.sort_order, task.status.value,
                    payload["completedAt"], payload["createdAt"], payload["updatedAt"],
                ),
            )
        return task

    def _ensure_postgres_task_parent_anchors(self, db, task: DailyTask) -> None:
        """Repair compatibility anchors before a PostgreSQL task write.

        Earlier runtime versions persisted only `study_plans`. Rebuilding the
        normalized parent chain here lets those existing plans accept tasks
        without a destructive data migration.
        """
        if getattr(self._db, "backend", "sqlite") != "postgres":
            return

        week = self.get_week_plan(task.week_plan_id, task.user_id)
        month = self.get_month_plan(week.month_plan_id, task.user_id)
        year = self.get_year_plan(month.year_plan_id, task.user_id)
        self._save_postgres_plan_anchor(
            db, year, parent_id=None, year=year.year, month=None,
            week_start=None, week_end=None, payload=year.to_dict(),
        )
        self._save_postgres_plan_anchor(
            db, month, parent_id=year.id, year=None, month=month.month,
            week_start=None, week_end=None, payload=month.to_dict(),
        )
        self._save_postgres_plan_anchor(
            db, week, parent_id=month.id, year=None, month=None,
            week_start=week.week_start.isoformat(), week_end=week.week_end.isoformat(),
            payload=week.to_dict(),
        )

    def get_year_plan(self, plan_id: str, user_id: str) -> YearPlan:
        return year_plan_from_payload(self._plan_payload(plan_id, user_id, "long_term"))

    def get_month_plan(self, plan_id: str, user_id: str) -> MonthPlan:
        return month_plan_from_payload(self._plan_payload(plan_id, user_id, "monthly"))

    def get_week_plan(self, plan_id: str, user_id: str) -> WeekPlan:
        return week_plan_from_payload(self._plan_payload(plan_id, user_id, "weekly"))

    def get_task(self, task_id: str, user_id: str) -> DailyTask:
        row = self._db.connection.execute("SELECT * FROM daily_tasks WHERE id = ?", (task_id,)).fetchone()
        if not row or row["user_id"] != user_id:
            raise PermissionError("Task does not belong to user")
        return self._task_row(row)

    def get_current_plan(self, user_id: str, goal_id: str) -> dict[str, object] | None:
        year_rows = self._plan_rows(user_id, goal_id, "long_term")
        if not year_rows:
            return None
        year = year_plan_from_payload(self._plan_payload(year_rows[-1]["id"], user_id, "long_term"))
        months = [month_plan_from_payload(self._plan_payload(row["id"], user_id, "monthly")) for row in self._plan_rows(user_id, goal_id, "monthly")]
        weeks = [week_plan_from_payload(self._plan_payload(row["id"], user_id, "weekly")) for row in self._plan_rows(user_id, goal_id, "weekly")]
        tasks = [self._task_row(row) for row in self._task_rows(user_id, goal_id)]
        return {
            "yearPlan": year,
            "monthPlans": sorted(months, key=lambda item: item.month),
            "weekPlans": sorted(weeks, key=lambda item: item.week_start),
            "dailyTasks": sorted(tasks, key=lambda item: (item.task_date, item.sort_order, item.created_at)),
        }

    def list_year_plans_for_goal(self, user_id: str, goal_id: str) -> list[YearPlan]:
        return [year_plan_from_payload(self._plan_payload(row["id"], user_id, "long_term")) for row in self._plan_rows(user_id, goal_id, "long_term")]

    def list_month_plans_for_goal(self, user_id: str, goal_id: str) -> list[MonthPlan]:
        return [month_plan_from_payload(self._plan_payload(row["id"], user_id, "monthly")) for row in self._plan_rows(user_id, goal_id, "monthly")]

    def list_week_plans_for_goal(self, user_id: str, goal_id: str) -> list[WeekPlan]:
        return [week_plan_from_payload(self._plan_payload(row["id"], user_id, "weekly")) for row in self._plan_rows(user_id, goal_id, "weekly")]

    def list_tasks_for_date(self, user_id: str, goal_id: str, task_date: date) -> list[DailyTask]:
        return [self._task_row(row) for row in self._task_rows(user_id, goal_id, task_date)]

    def list_tasks_for_goal(self, user_id: str, goal_id: str) -> list[DailyTask]:
        return [self._task_row(row) for row in self._task_rows(user_id, goal_id)]

    def save_session(self, session: StudySession) -> StudySession:
        payload = session.to_dict()
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO study_sessions
                (id,user_id,task_id,subject,topic,start_time,end_time,duration_minutes,notes,feeling,status,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET end_time=excluded.end_time,duration_minutes=excluded.duration_minutes,
                notes=excluded.notes,feeling=excluded.feeling,status=excluded.status,updated_at=excluded.updated_at""",
                (
                    session.id, session.user_id, session.task_id, session.subject, session.topic,
                    payload["startTime"], payload["endTime"], session.duration_minutes, session.notes,
                    session.feeling, session.status.value, payload["createdAt"], payload["updatedAt"],
                ),
            )
        return session

    def get_session(self, session_id: str, user_id: str) -> StudySession:
        row = self._db.connection.execute("SELECT * FROM study_sessions WHERE id = ?", (session_id,)).fetchone()
        if not row or row["user_id"] != user_id:
            raise PermissionError("Session does not belong to user")
        return self._session_row(row)

    def list_finished_sessions(self, user_id: str) -> list[StudySession]:
        rows = self._db.connection.execute(
            "SELECT * FROM study_sessions WHERE user_id = ? AND status = 'finished' ORDER BY start_time DESC",
            (user_id,),
        ).fetchall()
        return [self._session_row(row) for row in rows]

    def save_learning_event(self, event: LearningEvent) -> LearningEvent:
        payload = event.to_dict()
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO learning_events(id,user_id,event_type,summary,metadata,created_at)
                   VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO NOTHING""",
                (event.id, event.user_id, event.event_type, event.summary, dumps(event.metadata), payload["createdAt"]),
            )
        return event

    def list_learning_events(self, user_id: str) -> list[LearningEvent]:
        rows = self._db.connection.execute(
            "SELECT * FROM learning_events WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        return [event_from_payload({
            "id": row["id"], "userId": row["user_id"], "eventType": row["event_type"],
            "summary": row["summary"], "metadata": loads(row["metadata"]),
            "createdAt": row["created_at"],
        }) for row in rows]

    def save_wrong_question(self, question: WrongQuestion) -> WrongQuestion:
        payload = question.to_dict()
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO wrong_questions(id,user_id,goal_id,payload,created_at,updated_at)
                   VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at""",
                (question.id, question.user_id, question.goal_id, dumps(payload), payload["createdAt"], payload["updatedAt"]),
            )
        return question

    def get_wrong_question(self, question_id: str, user_id: str) -> WrongQuestion:
        row = self._db.connection.execute("SELECT payload FROM wrong_questions WHERE id = ?", (question_id,)).fetchone()
        if not row:
            raise KeyError(question_id)
        question = wrong_question_from_payload(loads(row["payload"]))
        if question.user_id != user_id:
            raise PermissionError("Wrong question does not belong to user")
        return question

    def list_wrong_questions(self, user_id: str, goal_id: str | None = None) -> list[WrongQuestion]:
        query = "SELECT payload FROM wrong_questions WHERE user_id = ?"
        params: list[object] = [user_id]
        if goal_id:
            query += " AND goal_id = ?"
            params.append(goal_id)
        query += " ORDER BY created_at DESC"
        rows = self._db.connection.execute(query, params).fetchall()
        return [wrong_question_from_payload(loads(row["payload"])) for row in rows]

    def save_review_item(self, item: ReviewItem) -> ReviewItem:
        payload = item.to_dict()
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO review_items(id,user_id,wrong_question_id,due_date,payload,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET due_date=excluded.due_date,
                   payload=excluded.payload, updated_at=excluded.updated_at""",
                (item.id, item.user_id, item.wrong_question_id, payload["dueDate"], dumps(payload), payload["createdAt"], payload["updatedAt"]),
            )
        return item

    def get_review_item(self, item_id: str, user_id: str) -> ReviewItem:
        row = self._db.connection.execute("SELECT payload FROM review_items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            raise KeyError(item_id)
        item = review_item_from_payload(loads(row["payload"]))
        if item.user_id != user_id:
            raise PermissionError("Review item does not belong to user")
        return item

    def list_review_items(self, user_id: str, wrong_question_id: str | None = None) -> list[ReviewItem]:
        query = "SELECT payload FROM review_items WHERE user_id = ?"
        params: list[object] = [user_id]
        if wrong_question_id:
            query += " AND wrong_question_id = ?"
            params.append(wrong_question_id)
        query += " ORDER BY due_date, created_at"
        rows = self._db.connection.execute(query, params).fetchall()
        return [review_item_from_payload(loads(row["payload"])) for row in rows]

    def save_word_entry(self, entry: WordEntry) -> WordEntry:
        payload = entry.to_dict()
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO study_word_entries(id,user_id,goal_id,normalized_word,language,payload,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET goal_id=excluded.goal_id,
                   normalized_word=excluded.normalized_word,language=excluded.language,payload=excluded.payload,updated_at=excluded.updated_at""",
                (
                    entry.id, entry.user_id, entry.goal_id, entry.normalized_word, entry.language, dumps(payload),
                    payload["createdAt"], payload["updatedAt"],
                ),
            )
        return entry

    def get_word_entry(self, entry_id: str, user_id: str) -> WordEntry:
        row = self._db.connection.execute(
            "SELECT payload FROM study_word_entries WHERE id = ?", (entry_id,)
        ).fetchone()
        if not row:
            raise KeyError(entry_id)
        entry = word_entry_from_payload(loads(row["payload"]))
        if entry.user_id != user_id:
            raise PermissionError("Word entry does not belong to user")
        return entry

    def delete_word_entry(self, entry_id: str, user_id: str) -> None:
        self.get_word_entry(entry_id, user_id)
        with self._db.transaction() as db:
            db.execute("DELETE FROM study_word_entries WHERE id = ?", (entry_id,))

    def list_word_entries(
        self,
        user_id: str,
        goal_id: str | None = None,
        language: str | None = None,
        tag: str | None = None,
    ) -> list[WordEntry]:
        query = "SELECT payload FROM study_word_entries WHERE user_id = ?"
        params: list[object] = [user_id]
        if goal_id:
            query += " AND goal_id = ?"
            params.append(goal_id)
        query += " ORDER BY normalized_word, created_at"
        rows = self._db.connection.execute(query, params).fetchall()
        entries = [word_entry_from_payload(loads(row["payload"])) for row in rows]
        if language:
            entries = [entry for entry in entries if entry.language == language]
        if tag:
            entries = [entry for entry in entries if tag in entry.tags]
        return entries

    def find_word_entry(
        self,
        user_id: str,
        normalized_word: str,
        goal_id: str | None = None,
        language: str | None = None,
    ) -> WordEntry | None:
        query = "SELECT payload FROM study_word_entries WHERE user_id = ? AND normalized_word = ?"
        params: list[object] = [user_id, normalized_word]
        if goal_id is None:
            query += " AND goal_id IS NULL"
        else:
            query += " AND goal_id = ?"
            params.append(goal_id)
        if language:
            query += " AND language = ?"
            params.append(language)
        row = self._db.connection.execute(query, params).fetchone()
        return word_entry_from_payload(loads(row["payload"])) if row else None

    def _save_plan(self, plan, *, parent_id: str | None = None, year: int | None = None, month: int | None = None, week_start: str | None = None, week_end: str | None = None) -> None:
        payload = plan.to_dict()
        with self._db.transaction() as db:
            db.execute(
                """INSERT INTO study_plans
                (id,user_id,goal_id,plan_type,parent_id,year,month,week_start,week_end,title,focus,status,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,focus=excluded.focus,status=excluded.status,updated_at=excluded.updated_at""",
                (
                    plan.id, plan.user_id, plan.goal_id, plan.plan_type.value, parent_id, year, month,
                    week_start, week_end, plan.title, getattr(plan, "focus", ""), plan.status.value,
                    payload["createdAt"], payload["updatedAt"],
                ),
            )
            self._save_postgres_plan_anchor(
                db,
                plan,
                parent_id=parent_id,
                year=year,
                month=month,
                week_start=week_start,
                week_end=week_end,
                payload=payload,
            )

    def _save_postgres_plan_anchor(
        self,
        db,
        plan,
        *,
        parent_id: str | None,
        year: int | None,
        month: int | None,
        week_start: str | None,
        week_end: str | None,
        payload: dict,
    ) -> None:
        """Maintain legacy normalized parents required by PostgreSQL task FKs.

        The portable repository reads `study_plans`, while the original
        PostgreSQL schema still constrains `daily_tasks.week_plan_id` through
        `week_plans` and its parent chain. These rows are compatibility
        anchors only; the shared plan contract remains `study_plans`.
        """
        if getattr(self._db, "backend", "sqlite") != "postgres":
            return

        if plan.plan_type.value == "long_term":
            db.execute(
                """INSERT INTO year_plans(id,user_id,goal_id,year,title,status,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                   year=excluded.year,title=excluded.title,status=excluded.status,updated_at=excluded.updated_at""",
                (plan.id, plan.user_id, plan.goal_id, year, plan.title, plan.status.value,
                 payload["createdAt"], payload["updatedAt"]),
            )
        elif plan.plan_type.value == "monthly":
            db.execute(
                """INSERT INTO month_plans(id,user_id,goal_id,year_plan_id,month,title,focus,status,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                   year_plan_id=excluded.year_plan_id,month=excluded.month,title=excluded.title,
                   focus=excluded.focus,status=excluded.status,updated_at=excluded.updated_at""",
                (plan.id, plan.user_id, plan.goal_id, parent_id, month, plan.title, plan.focus,
                 plan.status.value, payload["createdAt"], payload["updatedAt"]),
            )
        elif plan.plan_type.value == "weekly":
            db.execute(
                """INSERT INTO week_plans(id,user_id,goal_id,month_plan_id,week_start,week_end,title,focus,status,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                   month_plan_id=excluded.month_plan_id,week_start=excluded.week_start,week_end=excluded.week_end,
                   title=excluded.title,focus=excluded.focus,status=excluded.status,updated_at=excluded.updated_at""",
                (plan.id, plan.user_id, plan.goal_id, parent_id, week_start, week_end, plan.title,
                 plan.focus, plan.status.value, payload["createdAt"], payload["updatedAt"]),
            )

    def _plan_payload(self, plan_id: str, user_id: str, plan_type: str) -> dict:
        row = self._db.connection.execute("SELECT * FROM study_plans WHERE id = ?", (plan_id,)).fetchone()
        if not row or row["user_id"] != user_id or row["plan_type"] != plan_type:
            raise PermissionError("Plan does not belong to user")
        return self._plan_row_payload(row)

    def _plan_rows(self, user_id: str, goal_id: str, plan_type: str):
        return self._db.connection.execute(
            "SELECT * FROM study_plans WHERE user_id = ? AND goal_id = ? AND plan_type = ? ORDER BY created_at",
            (user_id, goal_id, plan_type),
        ).fetchall()

    def _task_rows(self, user_id: str, goal_id: str, task_date: date | None = None):
        if task_date:
            return self._db.connection.execute(
                "SELECT * FROM daily_tasks WHERE user_id = ? AND goal_id = ? AND task_date = ? ORDER BY task_date, created_at",
                (user_id, goal_id, task_date.isoformat()),
            ).fetchall()
        return self._db.connection.execute(
            "SELECT * FROM daily_tasks WHERE user_id = ? AND goal_id = ? ORDER BY task_date, created_at",
            (user_id, goal_id),
        ).fetchall()

    def _goal_row(self, row) -> StudyGoal:
        return goal_from_payload({
            "id": row["id"], "userId": row["user_id"], "goalName": row["goal_name"],
            "goalType": row["goal_type"], "examName": row["exam_name"], "deadline": row["deadline"],
            "description": row["description"], "subjects": loads(row["subjects"]),
            "currentLevel": row["current_level"], "dailyAvailableMinutes": row["daily_available_minutes"],
            "priority": row["priority"], "status": row["status"], "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        })

    def _plan_row_payload(self, row) -> dict:
        base = {
            "id": row["id"], "userId": row["user_id"], "goalId": row["goal_id"],
            "planType": row["plan_type"], "title": row["title"], "focus": row["focus"],
            "status": row["status"], "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        }
        if row["plan_type"] == "long_term":
            base["year"] = row["year"]
        elif row["plan_type"] == "monthly":
            base.update({"yearPlanId": row["parent_id"], "month": row["month"]})
        else:
            base.update({"monthPlanId": row["parent_id"], "weekStart": row["week_start"], "weekEnd": row["week_end"]})
        return base

    def _task_row(self, row) -> DailyTask:
        return task_from_payload({
            "id": row["id"], "userId": row["user_id"], "goalId": row["goal_id"], "weekPlanId": row["week_plan_id"],
            "subject": row["subject"], "topic": row["topic"], "taskDate": row["task_date"],
            "estimatedMinutes": row["estimated_minutes"], "priority": row["priority"],
            "sortOrder": row["sort_order"], "status": row["status"],
            "completedAt": row["completed_at"], "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        })

    def _session_row(self, row) -> StudySession:
        return session_from_payload({
            "id": row["id"], "userId": row["user_id"], "taskId": row["task_id"], "subject": row["subject"],
            "topic": row["topic"], "startTime": row["start_time"], "endTime": row["end_time"],
            "durationMinutes": row["duration_minutes"], "notes": row["notes"], "feeling": row["feeling"],
            "status": row["status"], "createdAt": row["created_at"], "updatedAt": row["updated_at"],
        })
