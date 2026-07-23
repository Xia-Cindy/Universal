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

MILESTONE_2_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("POST", "/api/study/goals", "create_goal", "milestone_2"),
    ApiContract("PATCH", "/api/study/goals/{goal_id}", "update_goal", "milestone_2"),
    ApiContract("GET", "/api/study/goals/active", "get_active_goal", "milestone_2"),
    ApiContract("POST", "/api/study/plans", "create_plan", "milestone_2"),
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
)

MILESTONE_4_1_CONTRACTS: tuple[ApiContract, ...] = (
    ApiContract("POST", "/api/study/knowledge/documents", "create_knowledge_document", "milestone_4_1"),
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
    ApiContract("GET", "/api/work/tech-stacks", "list_work_tech_stacks", "milestone_10"),
    ApiContract("POST", "/api/work/tech-stacks", "create_work_tech_stack", "milestone_10"),
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
    ApiContract("GET", "/api/work/projects", "list_work_projects", "milestone_10"),
    ApiContract("POST", "/api/work/projects", "create_work_project", "milestone_10"),
    ApiContract("GET", "/api/work/resumes", "list_work_resumes", "milestone_10"),
    ApiContract("POST", "/api/work/resumes/draft", "create_work_resume_draft", "milestone_10"),
)


def list_contracts() -> list[dict[str, str]]:
    return [
        contract.to_dict()
        for contract in (
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
            *MILESTONE_10_CONTRACTS,
        )
    ]
