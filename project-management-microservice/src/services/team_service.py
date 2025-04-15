from typing import List
from uuid import UUID
from ..models.team import Team

class TeamService:
    def createTeam(self, team: Team) -> Team:
        pass

    def getTeam(self, teamId: UUID) -> Team:
        pass

    def updateTeam(self, team: Team) -> Team:
        pass

    def deleteTeam(self, teamId: UUID) -> bool:
        pass

    def getTeamsByProject(self, projectId: UUID) -> List[Team]:
        pass

    def assignTeamLead(self, teamId: UUID, userId: UUID) -> bool:
        pass

    def addTeamMember(self, teamId: UUID, userId: UUID) -> bool:
        pass

    def removeTeamMember(self, teamId: UUID, userId: UUID) -> bool:
        pass