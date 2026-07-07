from backend.app.models import Planet, PlanetModule, PlanetStatus


class PlanetNotFoundError(LookupError):
    pass


class PlanetUnavailableError(PermissionError):
    pass


STUDY_MODULES: tuple[PlanetModule, ...] = (
    PlanetModule("dashboard", "Home", "/study"),
    PlanetModule("goal", "Goal", "/study/plan/goal"),
    PlanetModule("plan", "Plan", "/study/plan"),
    PlanetModule("study_record", "Study Record", "/study/session/:id"),
    PlanetModule("file_upload", "File Upload", "/study/knowledge/upload"),
    PlanetModule("ai_summary", "AI Summary", "/study/knowledge/summary/:id"),
    PlanetModule("knowledge", "Knowledge", "/study/knowledge"),
    PlanetModule("rag_qa", "RAG Q&A", "/study/tutor"),
    PlanetModule("tutor", "Tutor", "/study/tutor"),
    PlanetModule("wrong_questions", "Wrong Questions", "/study/review/wrong-questions"),
    PlanetModule("review", "Review", "/study/review"),
    PlanetModule("analytics", "Analytics", "/study/analytics"),
)


class PlanetRegistry:
    def __init__(self, planets: tuple[Planet, ...]):
        self._planets = {planet.name: planet for planet in planets}

    def list_planets(self) -> list[Planet]:
        return list(self._planets.values())

    def get_planet(self, name: str) -> Planet:
        try:
            return self._planets[name]
        except KeyError as exc:
            raise PlanetNotFoundError(f"Unknown planet: {name}") from exc

    def get_enterable_planet(self, name: str) -> Planet:
        planet = self.get_planet(name)
        if not planet.enterable:
            raise PlanetUnavailableError(f"{planet.display_name} is coming later")
        return planet

    def portal_payload(self) -> dict[str, object]:
        return {
            "product": "Universe OS",
            "planets": [planet.to_dict() for planet in self.list_planets()],
        }


def create_default_registry() -> PlanetRegistry:
    return PlanetRegistry(
        (
            Planet(
                name="study",
                display_name="Study Planet",
                status=PlanetStatus.ACTIVE,
                description="A calm AI learning workspace focused on next action.",
                primary_action="Enter Study Planet",
                modules=STUDY_MODULES,
            ),
            Planet(
                name="work",
                display_name="Work Planet",
                status=PlanetStatus.COMING_LATER,
                description="Future professional workspace placeholder.",
                primary_action="Coming Later",
            ),
            Planet(
                name="novel",
                display_name="Novel Planet",
                status=PlanetStatus.COMING_LATER,
                description="Future creative writing workspace placeholder.",
                primary_action="Coming Later",
            ),
            Planet(
                name="life",
                display_name="Life Planet",
                status=PlanetStatus.COMING_LATER,
                description="Future personal life rhythm workspace placeholder.",
                primary_action="Coming Later",
            ),
            Planet(
                name="creator",
                display_name="Creator Planet",
                status=PlanetStatus.COMING_LATER,
                description="Future creator workspace placeholder.",
                primary_action="Coming Later",
            ),
        )
    )

