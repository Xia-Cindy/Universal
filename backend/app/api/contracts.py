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


def list_contracts() -> list[dict[str, str]]:
    return [
        contract.to_dict()
        for contract in (
            *MILESTONE_1_CONTRACTS,
            *MILESTONE_2_CONTRACTS,
            *MILESTONE_3_CONTRACTS,
        )
    ]
