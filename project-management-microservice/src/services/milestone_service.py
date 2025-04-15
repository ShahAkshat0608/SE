from typing import List
from uuid import UUID
from ..models.milestone import Milestone

class MilestoneService:
    def createMilestone(self, milestone: Milestone) -> Milestone:
        pass

    def getMilestone(self, milestoneId: UUID) -> Milestone:
        pass

    def updateMilestone(self, milestone: Milestone) -> Milestone:
        pass

    def deleteMilestone(self, milestoneId: UUID) -> bool:
        pass

    def getMilestonesByProject(self, projectId: UUID) -> List[Milestone]:
        pass