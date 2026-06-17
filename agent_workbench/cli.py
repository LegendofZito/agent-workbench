#!/usr/bin/env python3
"""CLI entry point for Agent Workbench."""

import sys
import os

# Import the main application module
# The actual app code is in the agent-workbench script at the repo root
# This imports it dynamically to avoid duplication

def main():
    """Entry point for installed package."""
    # Get the path to the actual agent-workbench script
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(repo_root, "agent-workbench")
    
    # Execute the main script
    import importlib.util
    spec = importlib.util.spec_from_file_location("agent_workbench_main", script_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        print("Error: Could not load agent-workbench script", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
