"""
DataPulse Machine Learning Package
Multi-Scenario 3-Horizon Training and Evaluation
"""

import sys
import types
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

if "DataPulse" not in sys.modules:
    _dp = types.ModuleType("DataPulse")
    _dp.__path__ = [str(_root)]
    sys.modules["DataPulse"] = _dp
