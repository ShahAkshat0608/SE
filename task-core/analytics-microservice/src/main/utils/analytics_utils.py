from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import statistics
import math
from enum import Enum

class ProjectHealthStatus(str, Enum):
    """Project health status classifications"""
    ON_TRACK = "On Track"
    AT_RISK = "At Risk"
    DELAYED = "Delayed"
    CRITICAL = "Critical"


def calculate_completion_rate(completed: int, total: int) -> float:
    """Calculate completion rate as a percentage"""
    if total == 0:
        return 0.0
    return round((completed / total) * 100, 1)

def get_aware_datetime(dt):
    """Convert datetime to timezone-aware if it's not already"""
    if dt is None:
        return datetime.now(timezone.utc)
    
    if isinstance(dt, str):
        # Try parsing ISO format
        try:
            if 'Z' in dt:
                # Replace 'Z' with proper timezone format
                dt = dt.replace('Z', '+00:00')
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return datetime.now(timezone.utc)
    
    # Make timezone-aware if it's not
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
        
    return dt

def calculate_due_dates_distribution(subtasks: List[Dict]) -> Dict[str, int]:
    """Calculate distribution of due dates for tasks"""
    today = datetime.now(timezone.utc)
    next_week = today + timedelta(days=7)
    next_month = today + timedelta(days=30)
    
    this_week = 0
    this_month = 0
    later = 0
    
    for task in subtasks:
        due_date_str = task.get("due_date", "")
        if not due_date_str:
            continue
        
        due_date = get_aware_datetime(due_date_str)
        
        if due_date <= next_week:
            this_week += 1
        elif due_date <= next_month:
            this_month += 1
        else:
            later += 1
    
    return {
        "this_week": this_week,
        "this_month": this_month,
        "later": later
    }

def group_subtasks_by_priority(subtasks: List[Dict]) -> Dict[str, int]:
    """Group subtasks by priority level"""
    priorities = {"high": 0, "medium": 0, "low": 0}
    
    for task in subtasks:
        priority = task.get("priority", "").lower()
        if priority in priorities:
            priorities[priority] += 1
    
    return priorities

def calculate_milestone_completion(milestones: List[Dict], subtasks: List[Dict]) -> List[Dict]:
    """Calculate completion rate for each milestone"""
    milestone_subtasks = {}
    
    # Group subtasks by milestone
    for subtask in subtasks:
        milestone_id = subtask.get("milestone_id")
        if not milestone_id:
            continue
        
        if milestone_id not in milestone_subtasks:
            milestone_subtasks[milestone_id] = {"total": 0, "completed": 0}
        
        milestone_subtasks[milestone_id]["total"] += 1
        if subtask.get("completed", False):
            milestone_subtasks[milestone_id]["completed"] += 1
    
    # Calculate completion rate for each milestone
    result = []
    for milestone in milestones:
        milestone_id = milestone.get("id")
        stats = milestone_subtasks.get(milestone_id, {"total": 0, "completed": 0})
        
        completion_rate = calculate_completion_rate(
            stats["completed"], stats["total"]
        )
        
        result.append({
            "id": milestone_id,
            "name": milestone.get("name", "Unnamed Milestone"),
            "completion_rate": completion_rate
        })
    
    return result

def calculate_estimated_completion_date(project: Dict, completed_tasks: int, total_tasks: int) -> Optional[datetime]:
    """Calculate estimated completion date based on current progress"""
    try:
        # Convert string dates to datetime objects
        start_date_str = project.get("start_date")
        target_end_date_str = project.get("target_end_date")
        
        if not start_date_str or not target_end_date_str:
            return None
        
        start_date = get_aware_datetime(start_date_str)
        target_end_date = get_aware_datetime(target_end_date_str)
        today = datetime.now(timezone.utc)
        
        # If project is complete, return actual end date
        if completed_tasks >= total_tasks:
            return today
        
        # Calculate estimated completion based on progress rate
        if completed_tasks == 0:
            # No progress yet, return target end date
            return target_end_date
            
        # Calculate elapsed time and progress ratio
        elapsed_days = (today - start_date).days
        
        # Avoid division by zero
        if elapsed_days <= 0:
            return target_end_date
            
        tasks_per_day = completed_tasks / elapsed_days
        
        # Avoid division by zero
        if tasks_per_day <= 0:
            return target_end_date
            
        remaining_tasks = total_tasks - completed_tasks
        remaining_days = remaining_tasks / tasks_per_day
        
        estimated_completion = today + timedelta(days=remaining_days)
        
        return estimated_completion
        
    except Exception as e:
        print(f"Error calculating completion date: {str(e)}")
        return None

def calculate_workload_balance(member_workloads: Dict) -> float:
    """Calculate workload balance across team members (0-100%)"""
    if not member_workloads:
        return 0.0
    
    hours_per_member = [workload.estimated_hours for workload in member_workloads.values()]
    
    if not hours_per_member:
        return 0.0
        
    avg_hours = sum(hours_per_member) / len(hours_per_member)
    
    # Avoid division by zero
    if avg_hours == 0:
        return 100.0
        
    # Calculate deviation from average
    deviations = [abs(hours - avg_hours) / avg_hours for hours in hours_per_member]
    avg_deviation = sum(deviations) / len(deviations)
    
    # Convert to balance percentage (100% means perfect balance)
    balance = max(0, 100 - (avg_deviation * 100))
    
    return round(balance, 1)

def calculate_workload_distribution(team_members: List[Dict], subtasks: List[Dict]) -> Dict:
    """Calculate distribution of workload among team members"""
    if not team_members:
        return {"overallocated": 0, "balanced": 0, "underallocated": 0}
    
    # Count tasks per member
    member_tasks = {}
    for member in team_members:
        user_id = member.get("id") or member.get("user_id")
        if user_id:
            member_tasks[user_id] = 0
    
    for task in subtasks:
        assigned_to = task.get("assigned_to")
        if assigned_to in member_tasks:
            member_tasks[assigned_to] += 1
    
    # Calculate average tasks per member
    total_tasks = sum(member_tasks.values())
    avg_tasks = total_tasks / len(member_tasks) if member_tasks else 0
    
    # Categorize members by workload
    overallocated = 0
    balanced = 0
    underallocated = 0
    
    for tasks in member_tasks.values():
        if tasks == 0:
            underallocated += 1
        elif tasks < avg_tasks * 0.7:  # Less than 70% of average
            underallocated += 1
        elif tasks > avg_tasks * 1.3:  # More than 130% of average
            overallocated += 1
        else:
            balanced += 1
    
    return {
        "overallocated": overallocated,
        "balanced": balanced,
        "underallocated": underallocated
    }

def identify_project_bottlenecks(teams: List[Dict], subtasks: List[Dict]) -> List[Dict]:
    """Identify potential bottlenecks in the project workflow"""
    bottlenecks = []
    
    # Check for teams with high workload but few members
    for team in teams:
        team_id = team.get("id")
        members = team.get("members", [])
        
        team_subtasks = [s for s in subtasks if s.get("team_id") == team_id]
        pending_tasks = [s for s in team_subtasks if not s.get("completed", False)]
        
        if members and len(pending_tasks) > len(members) * 3:  # More than 3 tasks per member
            bottlenecks.append({
                "type": "team_overload",
                "team_id": team_id,
                "description": f"Team has {len(pending_tasks)} pending tasks with only {len(members)} members",
                "severity": "high" if len(pending_tasks) > len(members) * 5 else "medium"
            })
    
    # Check for high priority tasks with dependencies
    high_priority_tasks = [s for s in subtasks if s.get("priority") == "high" and not s.get("completed", False)]
    for task in high_priority_tasks:
        if task.get("parent_subtask_id"):
            parent_id = task.get("parent_subtask_id")
            parent_task = next((s for s in subtasks if s.get("id") == parent_id), None)
            
            if parent_task and not parent_task.get("completed", False):
                bottlenecks.append({
                    "type": "dependency_bottleneck",
                    "task_id": task.get("id"),
                    "description": f"High priority task blocked by uncompleted parent task {parent_id}",
                    "severity": "high"
                })
    
    return bottlenecks

# More utility functions

def generate_recommendations(user: Dict, progress_data: Dict, workload_data: Dict) -> List[Dict]:
    """Generate personalized recommendations based on user data"""
    recommendations = []
    
    # Check completion rate
    completion_rate = progress_data.get("completion_rate", 0)
    if completion_rate < 30:
        recommendations.append({
            "type": "productivity",
            "description": "Your task completion rate is low. Consider focusing on completing some quick wins.",
            "priority": "high"
        })
    
    # Check workload distribution
    priority_distribution = workload_data.get("priority_distribution", {})
    high_priority = priority_distribution.get("high", 0)
    
    if high_priority > 3:
        recommendations.append({
            "type": "focus",
            "description": f"You have {high_priority} high priority tasks pending. Focus on these first.",
            "priority": "high"
        })
    
    # Check upcoming deadlines
    due_this_week = workload_data.get("due_this_week", 0)
    if due_this_week > 2:
        recommendations.append({
            "type": "time_management",
            "description": f"You have {due_this_week} tasks due this week. Plan your time carefully.",
            "priority": "medium"
        })
    
    # If no issues found, add positive recommendation
    if not recommendations:
        recommendations.append({
            "type": "positive",
            "description": "You're doing well! Keep up the good work.",
            "priority": "low"
        })
    
    return recommendations

def generate_team_recommendations(progress_data: Dict, workload_data: Dict) -> List[Dict]:
    """Generate team recommendations based on analytics data"""
    recommendations = []
    
    # Check team completion rate
    completion_rate = progress_data.get("completion_rate", 0)
    if completion_rate < 40:
        recommendations.append({
            "type": "team_productivity",
            "description": "Team's task completion rate is below target. Consider a team sync to address blockers.",
            "priority": "high"
        })
    
    # Check workload balance
    workload_balance = workload_data.get("workload_balance", 0)
    if workload_balance < 70:
        recommendations.append({
            "type": "workload_distribution",
            "description": "Workload is unevenly distributed across team members. Consider rebalancing assignments.",
            "priority": "medium"
        })
    
    # Check for member-specific issues
    member_workloads = workload_data.get("member_workloads", {})
    overallocated_members = []
    
    for member_id, workload in member_workloads.items():
        if workload.get("estimated_hours", 0) > 40:
            overallocated_members.append(workload.get("user_name", member_id))
    
    if overallocated_members:
        member_list = ", ".join(overallocated_members[:3])
        recommendations.append({
            "type": "resource_allocation",
            "description": f"Some team members are overallocated (e.g., {member_list}). Consider redistributing work.",
            "priority": "high"
        })
    
    # If no issues found, add positive recommendation
    if not recommendations:
        recommendations.append({
            "type": "positive",
            "description": "Team is performing well with good workload distribution.",
            "priority": "low"
        })
    
    return recommendations

def assess_project_health(progress_data: Dict, workload_data: Dict, project: Dict) -> Dict:
    """Assess overall health of a project"""
    issues = []
    
    # Get project dates
    try:
        start_date_str = project.get("start_date", "")
        target_end_date_str = project.get("target_end_date", "")
        
        start_date = get_aware_datetime(start_date_str)
        target_end_date = get_aware_datetime(target_end_date_str)
        today = datetime.now(timezone.utc)
        
        # Calculate progress metrics
        completion_rate = progress_data.get("completion_rate", 0)
        estimated_completion = progress_data.get("estimated_completion")
        if estimated_completion:
            estimated_completion = get_aware_datetime(estimated_completion)
        
        # Calculate time elapsed vs progress made
        total_days = (target_end_date - start_date).days
        elapsed_days = (today - start_date).days
        
        if total_days > 0:
            time_elapsed_pct = min(100, (elapsed_days / total_days) * 100)
        else:
            time_elapsed_pct = 100
        
        # Check if project is behind schedule
        if time_elapsed_pct > completion_rate + 10:
            issues.append("Project is behind schedule")
        
        # Check estimated completion against target
        if estimated_completion and estimated_completion > target_end_date:
            delay_days = (estimated_completion - target_end_date).days
            issues.append(f"Project estimated to be delayed by {delay_days} days")
        
        # Check resource allocation
        resource_allocation = workload_data.get("resource_allocation", {})
        if resource_allocation.get("overallocated_teams", []):
            issues.append("Some teams are overallocated")
        
        # Check bottlenecks
        bottlenecks = workload_data.get("bottlenecks", [])
        high_severity_bottlenecks = sum(1 for b in bottlenecks if b.get("severity") == "high")
        if high_severity_bottlenecks > 0:
            issues.append(f"Project has {high_severity_bottlenecks} high-severity bottlenecks")
        
        # Determine project health status
        if len(issues) >= 3 or (completion_rate < 25 and time_elapsed_pct > 50):
            status = "at_risk"
        elif len(issues) >= 1 or (time_elapsed_pct > completion_rate + 5):
            status = "needs_attention"
        else:
            status = "on_track"
        
        return {
            "status": status,
            "issues": issues
        }
        
    except Exception as e:
        print(f"Error in project health assessment: {str(e)}")
        return {
            "status": "unknown",
            "issues": ["Unable to assess project health due to data issues"]
        }

def generate_visualization_data(report_type: str, data: Dict) -> Dict:
    """Generate visualization data for reports"""
    visualizations = {}
    
    if report_type == "progress":
        # Task completion chart
        visualizations["completionChart"] = {
            "type": "doughnut",
            "data": {
                "labels": ["Completed", "Pending"],
                "datasets": [{
                    "data": [
                        data.get("completed_subtasks", 0),
                        data.get("pending_subtasks", 0)
                    ],
                    "backgroundColor": ["#4CAF50", "#FFC107"]
                }]
            }
        }
        
        # If there's historical data, add trend chart
        if "historical_performance" in data:
            visualizations["trendChart"] = {
                "type": "line",
                "data": {
                    "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
                    "datasets": [{
                        "label": "Tasks Completed",
                        "data": [3, 4, 5, 4],  # Placeholder data
                        "borderColor": "#2196F3",
                        "fill": False
                    }]
                }
            }
    
    elif report_type == "workload":
        # Priority distribution chart
        priority_data = data.get("priority_distribution", {})
        visualizations["priorityChart"] = {
            "type": "pie",
            "data": {
                "labels": ["High", "Medium", "Low"],
                "datasets": [{
                    "data": [
                        priority_data.get("high", 0),
                        priority_data.get("medium", 0),
                        priority_data.get("low", 0)
                    ],
                    "backgroundColor": ["#F44336", "#FF9800", "#8BC34A"]
                }]
            }
        }
        
        # Due date distribution
        visualizations["dueDateChart"] = {
            "type": "bar",
            "data": {
                "labels": ["This Week", "This Month", "Later"],
                "datasets": [{
                    "label": "Tasks Due",
                    "data": [
                        data.get("due_this_week", 0),
                        data.get("due_this_month", 0),
                        data.get("due_later", 0)
                    ],
                    "backgroundColor": ["#F44336", "#FF9800", "#8BC34A"]
                }]
            }
        }
    
    elif report_type == "comprehensive":
        # Progress chart
        progress_stats = data.get("progress_stats", {})
        visualizations["progressChart"] = {
            "type": "doughnut",
            "data": {
                "labels": ["Completed", "Pending"],
                "datasets": [{
                    "data": [
                        progress_stats.get("completed_subtasks", 0),
                        progress_stats.get("pending_subtasks", 0)
                    ],
                    "backgroundColor": ["#4CAF50", "#FFC107"]
                }]
            }
        }
        
        # Priority chart
        priority_data = data.get("workload_stats", {}).get("priority_distribution", {})
        visualizations["priorityChart"] = {
            "type": "pie",
            "data": {
                "labels": ["High", "Medium", "Low"],
                "datasets": [{
                    "data": [
                        priority_data.get("high", 0),
                        priority_data.get("medium", 0),
                        priority_data.get("low", 0)
                    ],
                    "backgroundColor": ["#F44336", "#FF9800", "#8BC34A"]
                }]
            }
        }
        
        # Historical performance chart (if available)
        historical_data = data.get("historical_performance")
        if historical_data:
            visualizations["trendChart"] = {
                "type": "line",
                "data": {
                    "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
                    "datasets": [{
                        "label": "Tasks Completed",
                        "data": [3, 4, 5, 4],  # Placeholder data
                        "borderColor": "#2196F3",
                        "fill": False
                    }]
                }
            }
    
    return visualizations