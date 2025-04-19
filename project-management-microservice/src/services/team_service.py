from typing import List, Optional
from uuid import UUID, uuid4
from ..models.team import Team
from datetime import datetime
from ..database.team_dal import TeamDAL

class TeamService:
    def __init__(self, team_dal: TeamDAL = None):
        self.team_dal = team_dal or TeamDAL()

    def createTeam(self, team: Team) -> Team:
        """Create a new team."""
        # Generate ID and set creation time if not provided
        if not team.id:
            team.id = f"team-{str(uuid4())[:8]}"
        if not team.created_at:
            team.created_at = datetime.now()
            
        # Convert Team object to dictionary
        team_dict = team.to_dict()
        self.team_dal.add_team(team_dict)
        return team

    def getTeam(self, teamId: UUID) -> Optional[Team]:
        """Fetch a team by its ID."""
        team_data = self.team_dal.get_team(str(teamId))
        if team_data:
            return Team.from_dict(team_data)  # Convert dictionary to Team object
        return None

    def updateTeam(self, team: Team) -> Optional[Team]:
        """Update an existing team."""
        updated_team_dict = team.to_dict()
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
        return [Team.from_dict(team_data) for team_data in teams_data]

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
        # Check if user is already in team
        if self.team_dal.isUserInTeam(str(userId), str(teamId)):
            return False  # User already in team
        self.team_dal.addUserToTeam(str(userId), str(teamId))
        return True

    def removeTeamMember(self, teamId: UUID, userId: UUID) -> bool:
        """Remove a team member from a team."""
        team = self.getTeam(teamId)
        if not team:
            return False  # Team not found
        self.team_dal.removeUserFromTeam(str(userId), str(teamId))
        return True
        
    def getTeamMembers(self, teamId: UUID) -> List[dict]:
        """Get all members of a specific team."""
        return self.team_dal.getTeamMembers(str(teamId))