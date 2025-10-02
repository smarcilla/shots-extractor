# tests/conftest.py
import os
import sys

REPO_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SRC_PATH = os.path.join(REPO_ROOT, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)
