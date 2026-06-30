"""IntentSpec: Execution-based Intent Violation Rate measurement for LLM code generation."""

from .schema import ConstraintTest, IVRResult, SpecPair, SolutionResult
from .dataset import load_spec_pairs
from .execute import evaluate_solution, run_solution
from .ivr import compute_ivr, compute_ivr_by_type

__version__ = "0.2.0"
__all__ = [
    # schema
    "ConstraintTest",
    "SpecPair",
    "SolutionResult",
    "IVRResult",
    # dataset
    "load_spec_pairs",
    # execute
    "run_solution",
    "evaluate_solution",
    # ivr
    "compute_ivr",
    "compute_ivr_by_type",
]
