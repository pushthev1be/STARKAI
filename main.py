#!/usr/bin/env python3
"""
STARKAI - Tony Stark Inspired AI Assistant

A comprehensive AI assistant with intelligence gathering,
system monitoring, code fixing, and hardware integration.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interface.cli import main

if __name__ == "__main__":
    asyncio.run(main())
