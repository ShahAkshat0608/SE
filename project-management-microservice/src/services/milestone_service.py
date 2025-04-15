from typing import List
from uuid import UUID
from datetime import datetime
from ..models.milestone import Milestone
from ..database.milestone_dal import MilestoneDAL

class MilestoneService:
    def __init__(self, milestone_dal: MilestoneDAL = None):
        """Initialize the milestone service with a data access layer."""
        self.milestone_dal = milestone_dal or MilestoneDAL()
    
    def createMilestone(self, milestone: Milestone) -> Milestone:
        """
        Create a new milestone in the system.
        
        Args:
            milestone: The milestone object to be created
        
        Returns:
            The created milestone with generated ID and timestamps
        
        Raises:
            ValueError: If milestone is missing required properties
        """
        # Validate required fields
        if not milestone.name or not milestone.project_id:
            raise ValueError("Milestone must have a name and project_id")
        
        # Generate ID if not provided
        if not milestone.id:
            milestone.__post_init__()  # This will generate ID and timestamps
        
        # Set creation timestamps
        if not milestone.created_at:
            milestone.created_at = datetime.now()
        if not milestone.updated_at:
            milestone.updated_at = milestone.created_at
            
        # Add milestone to database
        self.milestone_dal.add_milestone(milestone)
        
        return milestone

    def getMilestone(self, milestoneId: UUID) -> Milestone:
        """
        Retrieve a milestone by its ID.
        
        Args:
            milestoneId: The UUID of the milestone to retrieve
        
        Returns:
            The milestone if found
        
        Raises:
            ValueError: If milestone with given ID is not found
        """
        milestone = self.milestone_dal.get_milestone(str(milestoneId))
        if not milestone:
            raise ValueError(f"Milestone with ID {milestoneId} not found")
        return milestone

    def updateMilestone(self, milestone: Milestone) -> Milestone:
        """
        Update an existing milestone.
        
        Args:
            milestone: The milestone object with updated properties
        
        Returns:
            The updated milestone
        
        Raises:
            ValueError: If milestone with given ID is not found
        """
        # Check if milestone exists
        existing_milestone = self.milestone_dal.get_milestone(milestone.id)
        if not existing_milestone:
            raise ValueError(f"Milestone with ID {milestone.id} not found")
        
        # Ensure required fields are present
        if not milestone.name or not milestone.project_id:
            raise ValueError("Milestone must have a name and project_id")
            
        # Update the last modified timestamp
        milestone.updated_at = datetime.now()
        
        # Update milestone in database
        self.milestone_dal.update_milestone(milestone.id, milestone)
        
        return milestone

    def deleteMilestone(self, milestoneId: UUID) -> bool:
        """
        Delete a milestone by its ID.
        
        Args:
            milestoneId: The UUID of the milestone to delete
        
        Returns:
            True if deleted successfully
        
        Raises:
            ValueError: If milestone with given ID is not found
        """
        # Convert UUID to string for DAL
        milestone_id_str = str(milestoneId)
        
        # Check if milestone exists
        existing_milestone = self.milestone_dal.get_milestone(milestone_id_str)
        if not existing_milestone:
            raise ValueError(f"Milestone with ID {milestoneId} not found")
            
        # Delete the milestone
        self.milestone_dal.delete_milestone(milestone_id_str)
        return True

    def getMilestonesByProject(self, projectId: UUID) -> List[Milestone]:
        """
        Retrieve all milestones for a specific project.
        
        Args:
            projectId: The UUID of the project
        
        Returns:
            List of milestones belonging to the project
        """
        # Convert UUID to string for DAL
        project_id_str = str(projectId)
        return self.milestone_dal.get_milestones_by_project(project_id_str)