#!/usr/bin/env python3
"""
RTK v2 Agent Memory Setup
Part of RTK v2 roadmap: "Obsidian vault integration for cross-session memory"

This script sets up the agent memory directory structure for RTK v2.
Run once on any machine running RTK agents.
"""

import os
from pathlib import Path

MEMORY_STRUCTURE = {
    "memory/": {
        "agent_memory.md": "# Agent Memory\n\nPersistent context across sessions.\n",
        "evolution_log.md": "# Evolution Log\n\nTrack agent improvements over time.\n",
        "strategy.md": "# Strategy\n\nCurrent agent strategy and goals.\n",
    },
    "memory/archive/": {},
}

def setup_memory():
    base = Path.home() / ".rtk"
    print(f"Setting up RTK v2 memory at {base}")
    
    for dir_name, files in MEMORY_STRUCTURE.items():
        dir_path = base / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        
        for file_name, content in files.items():
            file_path = dir_path / file_name
            if not file_path.exists():
                file_path.write_text(content)
                print(f"  Created {file_path}")
            else:
                print(f"  Exists {file_path}")
    
    print("\nRTK v2 memory setup complete!")

if __name__ == "__main__":
    setup_memory()
