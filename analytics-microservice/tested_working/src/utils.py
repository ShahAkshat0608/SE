"""Helper utilities for the analytics microservice."""

from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

import config


def parse_date(date_str: str) -> datetime:
    """Parse a date string into a datetime object.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime object
    """
    try:
        return datetime.strptime(date_str, config.DEFAULT_DATE_FORMAT)
    except ValueError:
        # Try parsing without the time part
        return datetime.strptime(date_str.split('T')[0], "%Y-%m-%d")


def calculate_days_difference(date1_str: str, date2_str: Optional[str] = None) -> int:
    """Calculate the difference in days between two dates.
    
    Args:
        date1_str: First date string
        date2_str: Second date string, defaults to current date if None
        
    Returns:
        Number of days difference
    """
    date1 = parse_date(date1_str)
    date2 = datetime.now() if date2_str is None else parse_date(date2_str)
    return abs((date2 - date1).days)


def get_priority_score(priority: str) -> int:
    """Get the numeric score for a priority level.
    
    Args:
        priority: Priority level (low, medium, high, critical)
        
    Returns:
        Numeric priority score
    """
    return config.PRIORITY_LEVELS.get(priority.lower(), 0)


def group_by_attribute(tasks: List[Dict[str, Any]], attribute: str) -> Dict[str, List[Dict[str, Any]]]:
    """Group tasks by a specific attribute.
    
    Args:
        tasks: List of task dictionaries
        attribute: The attribute to group by
        
    Returns:
        Dictionary with groups of tasks
    """
    result = {}
    for task in tasks:
        key = str(task.get(attribute, "undefined"))
        if key not in result:
            result[key] = []
        result[key].append(task)
    return result