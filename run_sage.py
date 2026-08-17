"""
SAGE Situated Companion
Roadmap 2 — Application Launcher

Provides the repository-level entry point for running the SAGE
console application.

Usage:

    python run_sage.py

The launcher intentionally remains thin. Application behavior belongs
in the console application and adapter layers rather than in this
entry point.
"""

from apps.console import main


if __name__ == "__main__":
    main()
