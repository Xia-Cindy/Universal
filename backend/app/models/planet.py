from dataclasses import dataclass, field
from enum import StrEnum


class PlanetStatus(StrEnum):
    ACTIVE = "active"
    COMING_LATER = "coming_later"


@dataclass(frozen=True)
class PlanetModule:
    id: str
    display_name: str
    route: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "displayName": self.display_name,
            "route": self.route,
        }


@dataclass(frozen=True)
class Planet:
    name: str
    display_name: str
    status: PlanetStatus
    description: str
    primary_action: str
    modules: tuple[PlanetModule, ...] = field(default_factory=tuple)

    @property
    def enterable(self) -> bool:
        return self.status == PlanetStatus.ACTIVE

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "displayName": self.display_name,
            "status": self.status.value,
            "description": self.description,
            "primaryAction": self.primary_action,
            "enterable": self.enterable,
            "modules": [module.to_dict() for module in self.modules],
        }

