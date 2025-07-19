#!/usr/bin/env python3
"""
STARKAI - Tony Stark AI Assistant
Entry point for the StarkAI Assistant system
"""

import sys
import os
import argparse
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from interface.cli import CLI
from core.llm_engine import LLMEngine
from core.personality import TonyStarkPersonality
from core.intel_collector import IntelligenceCollector
from core.hardware_helper import HardwareHelper
from core.system_hooks import SystemMonitor
from core.fixer import CodeFixer

class StarkAI:
    """Main StarkAI Assistant orchestrator"""
    
    def __init__(self):
        self.personality = TonyStarkPersonality()
        self.llm_engine = LLMEngine(personality=self.personality)
        self.intel_collector = IntelligenceCollector()
        self.hardware_helper = HardwareHelper()
        self.system_monitor = SystemMonitor()
        self.code_fixer = CodeFixer()
        self.cli = CLI(self)
        
    def initialize(self):
        """Initialize all components"""
        print(f"{self.personality.get_greeting()}")
        print("Initializing STARKAI systems...")
        
        self.llm_engine.initialize()
        self.intel_collector.initialize()
        self.hardware_helper.initialize()
        self.system_monitor.start_monitoring()
        
        print("All systems online. Ready for operation.")
        
    def shutdown(self):
        """Gracefully shutdown all components"""
        print("Shutting down STARKAI systems...")
        self.system_monitor.stop_monitoring()
        self.hardware_helper.disconnect_all()
        print("Shutdown complete.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="STARKAI - Tony Stark AI Assistant")
    parser.add_argument("--mode", choices=["cli", "interactive"], default="cli",
                       help="Operation mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    try:
        stark_ai = StarkAI()
        stark_ai.initialize()
        
        if args.mode == "cli":
            stark_ai.cli.run_interactive()
        else:
            stark_ai.cli.run_interactive()
            
    except KeyboardInterrupt:
        print("\nReceived interrupt signal...")
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        if 'stark_ai' in locals():
            stark_ai.shutdown()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
