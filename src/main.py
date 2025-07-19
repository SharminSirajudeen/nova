#!/usr/bin/env python3
"""
NOVA Main Entry Point
"""

import asyncio
import sys
from pathlib import Path

from .core.nova_core import NOVACore


async def main():
    """Main entry point for NOVA"""
    # Run the main function from nova_core
    from .core.nova_core import main as nova_main
    return await nova_main()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)