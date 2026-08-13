from dataclasses import dataclass


@dataclass(frozen=True)
class ApiContract:
    method: str
    path: str
    name: str
    milestone: str

    def to_dict(self) -> dict[str, str]:
        return {
            "method": self.method,
            "path": self.path,
            "name": self.name,
            "milestone": self.milestone,
        }


MILESTONE_1_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/health", "health", "milestone_1"),
    ApiContract("GET", "/api/planets", "list_planets", "milestone_1"),
    ApiContract("GET", "/api/planets/{planet_name}", "get_planet", "milestone_1"),
    ApiContract("GET", "/api/study/home", "study_home", "milestone_1"),
)

AUTH_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("POST", "/api/auth/register/request", "request_registration", "auth_foundation"),
    ApiContract("POST", "/api/auth/register/verify", "verify_registration", "auth_foundation"),
    ApiContract("POST", "/api/auth/login", "login", "auth_foundation"),
    ApiContract("GET", "/api/auth/me", "auth_me", "auth_foundation"),
)

MILESTONE_2_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("POST", "/api/study/goals", "create_goal", "milestone_2"),
    ApiContract("PATCH", "/api/study/goals/{goal_id}", "update_goal", "milestone_2"),
    ApiContract("GET", "/api/study/goals/active", "get_active_goal", "milestone_2"),
    ApiContract("POST", "/api/study/plans", "create_plan", "milestone_2"),
    ApiContract("POST", "/api/study/plans/nodes", "create_plan_node", "plan_builder"),
    ApiContract("GET", "/api/study/plans/current", "get_current_plan", "milestone_2"),
    ApiContract("PATCH", "/api/study/plans/year/{plan_id}", "update_year_plan", "milestone_2"),
    ApiContract("PATCH", "/api/study/plans/month/{plan_id}", "update_month_plan", "milestone_2"),
    ApiContract("PATCH", "/api/study/plans/week/{plan_id}", "update_week_plan", "milestone_2"),
    ApiContract("PATCH", "/api/study/tasks/{task_id}", "update_task", "milestone_2"),
    ApiContract("PATCH", "/api/study/tasks/{task_id}/complete", "complete_task", "milestone_2"),
    ApiContract("POST", "/api/study/sessions", "start_session", "milestone_2"),
    ApiContract("PATCH", "/api/study/sessions/{session_id}/finish", "finish_session", "milestone_2"),
    ApiContract("GET", "/api/study/records", "list_study_records", "milestone_2"),
)

MILESTONE_3_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("POST", "/api/study/tutor/ask", "study_tutor_ask", "milestone_3"),
    ApiContract("GET", "/api/study/tutor/history", "study_tutor_history", "milestone_3"),
    ApiContract("POST", "/api/study/tutor/events", "save_tutor_answer_event", "milestone_8_citations"),
    ApiContract("GET", "/api/study/knowledge/documents/{document_id}/evidence", "knowledge_evidence", "milestone_8_citations"),
)

MILESTONE_4_1_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/knowledge/provider/health", "knowledge_provider_health", "milestone_8_runtime"),
    ApiContract("POST", "/api/study/knowledge/documents", "create_knowledge_document", "milestone_4_1"),
    ApiContract(
        "POST",
        "/api/study/knowledge/documents/adopt-ragflow",
        "adopt_ragflow_knowledge_document",
        "milestone_8_runtime",
    ),
    ApiContract("GET", "/api/study/knowledge", "knowledge_overview", "milestone_4_1"),
    ApiContract("GET", "/api/study/knowledge/documents", "list_knowledge_documents", "milestone_4_1"),
    ApiContract(
        "GET",
        "/api/study/knowledge/documents/{document_id}",
        "get_knowledge_document",
        "milestone_4_1",
    ),
    ApiContract(
        "POST",
        "/api/study/knowledge/documents/{document_id}/process",
        "process_knowledge_document",
        "milestone_4_1",
    ),
    ApiContract(
        "PATCH",
        "/api/study/knowledge/documents/{document_id}",
        "update_knowledge_document",
        "milestone_4_1",
    ),
    ApiContract("GET", "/api/study/knowledge/documents/{document_id}/status", "refresh_knowledge_document", "milestone_8_runtime"),
    ApiContract("POST", "/api/study/knowledge/documents/{document_id}/retry", "retry_knowledge_document", "milestone_8_runtime"),
    ApiContract("DELETE", "/api/study/knowledge/documents/{document_id}", "delete_knowledge_document", "milestone_8_runtime"),
)

MILESTONE_4_2_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract(
        "POST",
        "/api/study/knowledge/documents/{document_id}/embeddings/prepare",
        "prepare_document_embeddings",
        "milestone_4_2",
    ),
    ApiContract(
        "GET",
        "/api/study/knowledge/documents/{document_id}/embeddings",
        "list_document_embeddings",
        "milestone_4_2",
    ),
    ApiContract(
        "POST",
        "/api/study/knowledge/retrieval/search",
        "search_knowledge_chunks",
        "milestone_4_2",
    ),
)

MILESTONE_5_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("POST", "/api/memory", "create_memory", "milestone_5"),
    ApiContract("GET", "/api/memory", "list_memory", "milestone_5"),
    ApiContract("PATCH", "/api/memory/{memory_id}", "update_memory", "milestone_5"),
    ApiContract("POST", "/api/memory/{memory_id}/archive", "archive_memory", "milestone_5"),
    ApiContract("GET", "/api/memory/context", "memory_context", "milestone_5"),
)

MILESTONE_6_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/study/analytics", "study_analytics", "milestone_6"),
    ApiContract("POST", "/api/study/analytics/report", "study_analytics_report", "milestone_6"),
    ApiContract("GET", "/api/study/feedback/recommendations", "study_feedback_recommendations", "study_feedback"),
)

MILESTONE_7_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/study/onboarding", "study_onboarding_status", "milestone_7"),
    ApiContract("POST", "/api/study/onboarding/goal", "study_onboarding_goal", "milestone_7"),
    ApiContract("POST", "/api/study/execution/sessions", "start_execution_session", "milestone_7"),
    ApiContract(
        "PATCH",
        "/api/study/execution/sessions/{session_id}/finish",
        "finish_execution_session",
        "milestone_7",
    ),
)

MILESTONE_7_5_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/study/goals", "list_goals", "milestone_7_5"),
    ApiContract("POST", "/api/study/goals/{goal_id}/switch", "switch_goal", "milestone_7_5"),
)

MILESTONE_7_6_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/study/workspace", "study_workspace", "milestone_7_6"),
)

MILESTONE_8_REVIEW_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("POST", "/api/study/review/wrong-questions", "create_wrong_question", "milestone_8_review"),
    ApiContract("GET", "/api/study/review/wrong-questions", "list_wrong_questions", "milestone_8_review"),
    ApiContract("GET", "/api/study/review/queue", "get_review_queue", "milestone_8_review"),
    ApiContract("POST", "/api/study/review/items/{review_id}/complete", "complete_review_item", "milestone_8_review"),
)

WORD_BOOK_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/study/wordbook/entries", "list_wordbook_entries", "study_wordbook"),
    ApiContract("POST", "/api/study/wordbook/entries", "create_wordbook_entry", "study_wordbook"),
    ApiContract("GET", "/api/study/wordbook/entries/{entry_id}", "get_wordbook_entry", "study_wordbook"),
    ApiContract("PATCH", "/api/study/wordbook/entries/{entry_id}", "update_wordbook_entry", "study_wordbook"),
    ApiContract("DELETE", "/api/study/wordbook/entries/{entry_id}", "delete_wordbook_entry", "study_wordbook"),
    ApiContract("POST", "/api/study/wordbook/import", "import_wordbook_entries", "study_wordbook"),
    ApiContract(
        "POST",
        "/api/study/wordbook/entries/{entry_id}/dictionary/refresh",
        "refresh_wordbook_dictionary",
        "study_wordbook",
    ),
    ApiContract("POST", "/api/study/wordbook/entries/{entry_id}/review", "review_wordbook_entry", "study_wordbook"),
)

FOCUS_READER_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/study/knowledge/documents/{document_id}/annotations", "list_knowledge_annotations", "focus_reader"),
    ApiContract("POST", "/api/study/knowledge/documents/{document_id}/annotations", "create_knowledge_annotation", "focus_reader"),
    ApiContract("PATCH", "/api/study/knowledge/documents/{document_id}/annotations/{annotation_id}", "update_knowledge_annotation", "focus_reader"),
    ApiContract("POST", "/api/study/knowledge/documents/{document_id}/annotations/{annotation_id}/mastered", "mark_knowledge_annotation_mastered", "focus_reader"),
    ApiContract("DELETE", "/api/study/knowledge/documents/{document_id}/annotations/{annotation_id}", "delete_knowledge_annotation", "focus_reader"),
)

KNOWLEDGE_SHARE_GRANT_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/study/knowledge/documents/{document_id}/share-grants", "list_knowledge_share_grants", "knowledge_share_grants"),
    ApiContract("POST", "/api/study/knowledge/documents/{document_id}/share-grants", "create_knowledge_share_grant", "knowledge_share_grants"),
    ApiContract("DELETE", "/api/study/knowledge/share-grants/{grant_id}", "revoke_knowledge_share_grant", "knowledge_share_grants"),
    ApiContract("GET", "/api/study/knowledge/documents/{document_id}/goal-links", "get_knowledge_document_goal_links", "knowledge_goal_links"),
    ApiContract("PUT", "/api/study/knowledge/documents/{document_id}/goal-links", "replace_knowledge_document_goal_links", "knowledge_goal_links"),
    ApiContract("GET", "/api/study/knowledge/documents/{document_id}/reading-progress", "get_knowledge_reading_progress", "reading_progress"),
    ApiContract("PUT", "/api/study/knowledge/documents/{document_id}/reading-progress", "save_knowledge_reading_progress", "reading_progress"),
)

STUDY_RECALL_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/study/recall/schedules", "list_recall_schedules", "study_recall_v2"),
    ApiContract("GET", "/api/study/recall/schedules/{source_type}/{source_id}", "get_recall_schedule", "study_recall_v2"),
    ApiContract("PATCH", "/api/study/recall/schedules/{source_type}/{source_id}", "adjust_recall_schedule", "study_recall_v2"),
)

MILESTONE_10_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/work/home", "work_home", "milestone_10"),
    ApiContract("POST", "/api/work/knowledge/documents", "create_work_knowledge_document", "milestone_10"),
    ApiContract("GET", "/api/work/knowledge", "work_knowledge_overview", "milestone_10"),
    ApiContract("GET", "/api/work/knowledge/documents", "list_work_knowledge_documents", "milestone_10"),
    ApiContract(
        "GET",
        "/api/work/knowledge/documents/{document_id}",
        "get_work_knowledge_document",
        "milestone_10",
    ),
    ApiContract(
        "POST",
        "/api/work/knowledge/documents/{document_id}/process",
        "process_work_knowledge_document",
        "milestone_10",
    ),
    ApiContract(
        "GET",
        "/api/work/knowledge/documents/{document_id}/status",
        "refresh_work_knowledge_document",
        "milestone_10",
    ),
    ApiContract("GET", "/api/work/tech-stacks", "list_work_tech_stacks", "milestone_10"),
    ApiContract("POST", "/api/work/tech-stacks", "create_work_tech_stack", "milestone_10"),
    ApiContract("PATCH", "/api/work/tech-stacks/{tech_stack_id}", "update_work_tech_stack", "milestone_10"),
    ApiContract("DELETE", "/api/work/tech-stacks/{tech_stack_id}", "delete_work_tech_stack", "milestone_10"),
    ApiContract("GET", "/api/work/tech-stacks/{tech_stack_id}", "work_tech_stack_detail", "milestone_10"),
    ApiContract("GET", "/api/work/tech-stacks/{tech_stack_id}/articles", "list_work_articles", "milestone_10"),
    ApiContract("POST", "/api/work/tech-stacks/{tech_stack_id}/articles", "create_work_article", "milestone_10"),
    ApiContract(
        "GET",
        "/api/work/tech-stacks/{tech_stack_id}/learning-records",
        "list_work_learning_records",
        "milestone_10",
    ),
    ApiContract(
        "POST",
        "/api/work/tech-stacks/{tech_stack_id}/learning-records",
        "create_work_learning_record",
        "milestone_10",
    ),
    ApiContract("GET", "/api/work/community/csdn", "work_community_csdn", "milestone_10"),
    ApiContract("GET", "/api/work/community/csdn/article", "work_community_csdn_article", "milestone_10"),
    ApiContract("GET", "/api/work/projects", "list_work_projects", "milestone_10"),
    ApiContract("POST", "/api/work/projects", "create_work_project", "milestone_10"),
    ApiContract("GET", "/api/work/resumes", "list_work_resumes", "milestone_10"),
    ApiContract("POST", "/api/work/resumes/draft", "create_work_resume_draft", "milestone_10"),
)

SPATIAL_STUDIO_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("GET", "/api/novel/drafts", "list_novel_drafts", "spatial_studio"),
    ApiContract("POST", "/api/novel/drafts", "create_novel_draft", "spatial_studio"),
    ApiContract("PATCH", "/api/novel/drafts/{draft_id}", "update_novel_draft", "spatial_studio"),
)


def list_contracts() -> list[dict[str, str]]:
    return [
        contract.to_dict()
        for contract in (
            *AUTH_CONTRACTS,
            *MILESTONE_1_CONTRACTS,
            *MILESTONE_2_CONTRACTS,
            *MILESTONE_3_CONTRACTS,
            *MILESTONE_4_1_CONTRACTS,
            *MILESTONE_4_2_CONTRACTS,
            *MILESTONE_5_CONTRACTS,
            *MILESTONE_6_CONTRACTS,
            *MILESTONE_7_CONTRACTS,
            *MILESTONE_7_5_CONTRACTS,
            *MILESTONE_7_6_CONTRACTS,
            *MILESTONE_8_REVIEW_CONTRACTS,
            *WORD_BOOK_CONTRACTS,
            *FOCUS_READER_CONTRACTS,
            *KNOWLEDGE_SHARE_GRANT_CONTRACTS,
            *STUDY_RECALL_CONTRACTS,
            *MILESTONE_10_CONTRACTS,
            *SPATIAL_STUDIO_CONTRACTS,
        )
    ]
