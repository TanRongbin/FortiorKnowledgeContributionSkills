#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

SCRIPT_DIR = Path(__file__).resolve().parent / "skills" / "fortior-knowledge-contributor" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
runpy.run_path(str(SCRIPT_DIR / "bootstrap_feishu.py"), run_name="__main__")
