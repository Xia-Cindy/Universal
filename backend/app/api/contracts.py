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
        )
    ]
