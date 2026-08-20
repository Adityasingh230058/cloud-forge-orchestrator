"""
Abstract Base Stage interface for Cloud Forge Orchestration stages.
"""

from abc import ABC, abstractmethod
import time
from typing import Dict, Any, List
from ..core.models import ClusterSpec, StageResult, StageStatus


class BaseStage(ABC):
    """
    Abstract interface for every layer in the 5-layer private cloud pipeline.
    """
    stage_number: int = 0
    stage_name: str = "Base Stage"

    def __init__(self, spec: ClusterSpec):
        self.spec = spec

    def execute(self) -> StageResult:
        start_time = time.time()
        actions: List[str] = []
        errors: List[str] = []
        details: Dict[str, Any] = {}

        try:
            details, actions = self.run()
            status = StageStatus.SUCCESS
        except Exception as e:
            status = StageStatus.FAILED
            errors.append(str(e))

        duration = round(time.time() - start_time, 2)
        return StageResult(
            stage_number=self.stage_number,
            stage_name=self.stage_name,
            status=status,
            duration_sec=duration,
            details=details,
            actions_taken=actions,
            errors=errors,
        )

    @abstractmethod
    def run(self) -> (Dict[str, Any], List[str]):
        """
        Executes the stage logic and returns (details_dict, actions_list).
        """
        pass
