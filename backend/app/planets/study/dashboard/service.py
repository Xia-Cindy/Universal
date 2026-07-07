from backend.app.models import Planet
from backend.app.users.service import UserProfile


class StudyHomeService:
    """Milestone 1 Study Home aggregator.

    The complete Goal, Plan, Review and Analytics integrations are later
    milestones. This service exposes the documented empty-state contract now.
    """

    def home(self, *, user: UserProfile, planet: Planet) -> dict[str, object]:
        return {
            "user": user.to_dict(),
            "planet": {
                "name": planet.name,
                "displayName": planet.display_name,
            },
            "state": "empty",
            "currentGoal": None,
            "primaryNextAction": {
                "type": "create_goal",
                "label": "Create Goal",
                "route": "/study/plan/goal",
            },
            "aiRecommendation": {
                "status": "placeholder",
                "message": "Create your first Goal to unlock personalized study guidance.",
                "basis": "No active Goal exists yet.",
            },
            "reviewDue": [],
            "recentStudyRecords": [],
            "knowledgeStatus": {
                "documents": 0,
                "processed": 0,
                "action": "Upload learning material after creating a Goal.",
            },
            "progressSnapshot": {
                "todayStudyMinutes": 0,
                "weekStudyMinutes": 0,
                "studyStreakDays": 0,
            },
        }

