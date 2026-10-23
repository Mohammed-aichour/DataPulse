"""
DataPulse — Smart Campus Analytics & Predictive Intelligence Platform
Package root initialization.
"""

import sys
import types
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure DataPulse namespace is bound
if "DataPulse" not in sys.modules:
    dp = types.ModuleType("DataPulse")
    dp.__path__ = [str(ROOT_DIR)]
    sys.modules["DataPulse"] = dp

__version__ = "1.0.0"
