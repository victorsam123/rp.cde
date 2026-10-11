"""Run unit checks only after selecting an isolated local QA database."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_redesign import initialize, STATE


if __name__ == "__main__":
    initialize(not STATE.exists())
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.discover(str(Path(__file__).parent), pattern="test_*.py")
    )
    sys.exit(not result.wasSuccessful())
