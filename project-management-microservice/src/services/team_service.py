from typing import List, Optional
from uuid import UUID
from ..models.team import Team
from ..database.team_dal import TeamDAL

class TeamService:
    def __init__(self, team_dal: TeamDAL):
        self.team_dal = team_dal

    def createTeam(self, team: Team) -> Team:
        """Create a new team."""
        team_dict = team.dict()  # Convert Team object to dictionary
        self.team_dal.add_team(team_dict)
        return team

    def getTeam(self, teamId: UUID) -> Optional[Team]:
        """Fetch a team by its ID."""
        team_data = self.team_dal.get_team(str(teamId))
        if team_data:
            return Team(**team_data)  # Convert dictionary to Team object
        return None

    def updateTeam(self, team: Team) -> Optional[Team]:
        """Update an existing team."""
        existing_team = self.getTeam(team.id)
        if not existing_team:
            return None  # Team not found
        updated_team_dict = team.dict()
        self.team_dal.update_team(str(team.id), updated_team_dict)
        return team

    def deleteTeam(self, teamId: UUID) -> bool:
        """Delete a team by its ID."""
        existing_team = self.getTeam(teamId)
        if not existing_team:
            return False  # Team not found
        self.team_dal.delete_team(str(teamId))
        return True

    def getTeamsByProject(self, projectId: UUID) -> List[Team]:
        """Fetch all teams for a specific project."""
        teams_data = self.team_dal.get_teams_by_project(str(projectId))
        return [Team(**team_data) for team_data in teams_data]

    def assignTeamLead(self, teamId: UUID, userId: UUID) -> bool:
        """Assign a team lead to a specific team."""
        team = self.getTeam(teamId)
        if not team:
            return False  # Team not found
        team.team_lead_id = str(userId)
        self.updateTeam(team)
        return True

    def addTeamMember(self, teamId: UUID, userId: UUID) -> bool:
        """Add a team member to a team."""
        team = self.getTeam(teamId)
        if not team:
            return False  # Team not found
        self.team_dal.addUserToTeam(str(userId), str(teamId))
        return True

    def removeTeamMember(self, teamId: UUID, userId: UUID) -> bool:
        """Remove a team member from a team."""
        team = self.getTeam(teamId)
        if not team:
            return False  # Team not found
        self.team_dal.removeUserfromTeam(str(userId), str(teamId))
        return True