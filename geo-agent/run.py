#!/usr/bin/env python3
"""Convenience entry point so you can run without installing the package:

    python run.py run --target havarie
    python run.py list

(equivalent to `python -m geo_agent.cli ...`)
"""
import sys
from geo_agent.cli import main

if __name__ == "__main__":
    sys.exit(main())
