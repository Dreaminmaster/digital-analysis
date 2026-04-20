"""digital_analysis package."""

from .analysis.engine import AnalysisEngine, AnalysisOutput
from .contracts.evidence import EvidenceBundle, EvidenceItem, EvidenceKind, SourceProvenance
from .contracts.tasks import TaskSpec, TaskType, TimeHorizon
from .execution.concurrent import GatherError, GatherResult, gather
from .execution.snapshots import RecordingHttpClient, ReplayHttpClient, SnapshotMissError
from .models.router import ModelBackend, ModelRouter, ModelTask
from .orchestrator import DigitalAnalysisOrchestrator, OrchestratorResult
from .planner.planner import SignalPlan, SignalRequirement, SimplePlanner

__all__ = [
    "AnalysisEngine",
    "AnalysisOutput",
    "DigitalAnalysisOrchestrator",
    "OrchestratorResult",
    "EvidenceBundle",
    "EvidenceItem",
    "EvidenceKind",
    "GatherError",
    "GatherResult",
    "gather",
    "RecordingHttpClient",
    "ReplayHttpClient",
    "SignalPlan",
    "SignalRequirement",
    "SimplePlanner",
    "SnapshotMissError",
    "SourceProvenance",
    "TaskSpec",
    "TaskType",
    "TimeHorizon",
    "ModelBackend",
    "ModelRouter",
    "ModelTask",
]
