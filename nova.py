#!/usr/bin/env python3
"""
NOVA - Neural Optimization & Versatile Automation
Your AI Co-Founder for Mac

This is the single entry point for NOVA. Everything happens from here.
No more multiple scripts. Just run: python3 nova.py
"""

import sys
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✋ NOVA shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ NOVA encountered an error: {e}")
        sys.exit(1)