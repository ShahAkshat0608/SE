"""JSON file data connector implementation."""

import json
import os
from typing import Dict, Any, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class JsonConnector:
    """Connector for reading and writing JSON data files."""
    
    def __init__(self, file_path: str, create_if_missing: bool = True):
        """Initialize the JSON connector.
        
        Args:
            file_path: Path to the JSON file
            create_if_missing: Whether to create the file if it doesn't exist
        """
        self.file_path = file_path
        self.create_if_missing = create_if_missing
    
    def read_data(self) -> Dict[str, Any]:
        """Read data from the JSON file.
        
        Returns:
            Dictionary containing the JSON data
            
        Raises:
            FileNotFoundError: If the file doesn't exist and create_if_missing is False
        """
        if not os.path.exists(self.file_path):
            if self.create_if_missing:
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                # Return empty dictionary, will be written on first write
                return {}
            raise FileNotFoundError(f"JSON file not found: {self.file_path}")
            
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from {self.file_path}: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error reading JSON file {self.file_path}: {str(e)}")
            return {}
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """Write data to the JSON file.
        
        Args:
            data: Dictionary to write to the file
            
        Returns:
            True if write was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            with open(self.file_path, 'w') as file:
                json.dump(data, file, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error writing to JSON file {self.file_path}: {str(e)}")
            return False
    
    def update_item(self, item_id: str, item_data: Dict[str, Any]) -> bool:
        """Update a specific item in the JSON file.
        
        Args:
            item_id: ID of the item to update
            item_data: New data for the item
            
        Returns:
            True if update was successful, False otherwise
        """
        data = self.read_data()
        data[item_id] = item_data
        return self.write_data(data)
    
    def delete_item(self, item_id: str) -> bool:
        """Delete a specific item from the JSON file.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        data = self.read_data()
        if item_id in data:
            del data[item_id]
            return self.write_data(data)
        return False