"""
Database Package for DataPulse.
"""

import sys
import types
from pathlib import Path

# Ensure root directory is on sys.path and DataPulse alias is bound
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

if "DataPulse" not in sys.modules:
    _dp = types.ModuleType("DataPulse")
    _dp.__path__ = [str(_root)]
    sys.modules["DataPulse"] = _dp
