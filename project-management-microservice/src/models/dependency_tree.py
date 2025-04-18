from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json

@dataclass
class DependencyTree:
    id: str
    task_id: str
    root_subtask_id: Optional[str] = 0
    dependencies: Dict[str, List[str]] = field(default_factory=dict) # adjacency list representation

    def has_cyclic_dependency(self) -> bool:
        """Check if the dependency tree has a cyclic dependency."""
        visited = set()
        rec_stack = set()

        def visit(node: str) -> bool:
            if node in rec_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.dependencies.get(node, []):
                if visit(neighbor):
                    return True

            rec_stack.remove(node)
            return False

        for subtask in self.dependencies.keys():
            if visit(subtask):
                return True
        return False

    def get_critical_path(self) -> List[str]:
        """Get the critical path in the dependency tree."""
        pass

    def add_dependency(self, parent_subtask_id: str, child_subtask_id: str) -> None:
        """Add a dependency between two subtasks."""
        if parent_subtask_id not in self.dependencies:
            self.dependencies[parent_subtask_id] = []
       
        if child_subtask_id not in self.dependencies:
            self.dependencies[child_subtask_id] = []
        
        
        if child_subtask_id not in self.dependencies[parent_subtask_id]:
            self.dependencies[parent_subtask_id].append(child_subtask_id)
        else:
            raise ValueError(f"Dependency {parent_subtask_id} -> {child_subtask_id} already exists.")
        

        # check if it's a cyclic dependency
        if self.has_cyclic_dependency():
            # remove the added dependency
            self.dependencies[parent_subtask_id].remove(child_subtask_id)
            raise ValueError(f"Cyclic dependency detected: {parent_subtask_id} -> {child_subtask_id}")
    
    def remove_dependency(self, parent_subtask_id: str, child_subtask_id: str) -> None:
        """Remove a dependency between two subtasks."""
        if parent_subtask_id in self.dependencies and child_subtask_id in self.dependencies[parent_subtask_id]:
            self.dependencies[parent_subtask_id].remove(child_subtask_id)
        else:
            raise ValueError(f"Dependency {parent_subtask_id} -> {child_subtask_id} does not exist.")
        # check if it's a cyclic dependency
        if self.has_cyclic_dependency():
            # re-add the removed dependency
            self.dependencies[parent_subtask_id].append(child_subtask_id)
            raise ValueError(f"Cyclic dependency detected: {parent_subtask_id} -> {child_subtask_id}")

    def add_subtask(self, subtask_id: str) -> None:
        """Add a subtask to the dependency tree."""
        if subtask_id not in self.dependencies:
            self.dependencies[subtask_id] = []
        else:
            raise ValueError(f"Subtask {subtask_id} already exists in the dependency tree.")


    def to_dict(self) -> Dict:
        """Convert the DependencyTree object to a dictionary."""
        return {
            "id": str(self.id),
            "task_id": str(self.task_id),
            "root_subtask_id": str(self.root_subtask_id) if self.root_subtask_id else None,
            "dependencies": {str(k): [str(i) for i in v] for k, v in self.dependencies.items()}
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'DependencyTree':
        """Create a DependencyTree object from a dictionary."""
        dependencies = data.get("dependencies", {})
        if isinstance(dependencies, str):
            dependencies = json.loads(dependencies)
        return DependencyTree(
            id=data.get("id"),
            task_id=data.get("task_id"),
            root_subtask_id=data.get("root_subtask_id"),
            dependencies={k: v for k, v in dependencies.items() if isinstance(v, list)}
        )