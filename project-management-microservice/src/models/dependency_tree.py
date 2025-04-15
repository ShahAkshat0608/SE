from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import UUID

@dataclass
class DependencyTree:
    task_id: UUID
    root_subtask_id: Optional[UUID] = 0
    dependencies: Dict[UUID, List[UUID]] = field(default_factory=dict)

    def has_cyclic_dependency(self) -> bool:
        """Check if the dependency tree has a cyclic dependency."""
        pass

    def get_critical_path(self) -> List[UUID]:
        """Get the critical path in the dependency tree."""
        pass