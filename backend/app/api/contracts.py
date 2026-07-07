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


def list_contracts() -> list[dict[str, str]]:
    return [contract.to_dict() for contract in MILESTONE_1_CONTRACTS]

