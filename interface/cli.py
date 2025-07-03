import asyncio
import argparse
from typing import Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_engine import LLMEngine
from core.personality import StarkPersonality
from core.intel_collector import IntelCollector
from core.system_hooks import SystemMonitor
from core.fixer import CodeFixer
from core.hardware_helper import HardwareInterface

class StarkAICLI:
    def __init__(self):
        self.llm = LLMEngine()
        self.personality = StarkPersonality()
        self.intel = IntelCollector()
        self.monitor = SystemMonitor()
        self.fixer = CodeFixer()
        self.hardware = HardwareInterface()
        self.running = False
        
    async def start_interactive_mode(self):
        """Start interactive CLI mode"""
        print("🚀 STARKAI Interactive Mode")
        print("Type 'help' for commands, 'exit' to quit")
        
        await self.monitor.start_monitoring()
        self.monitor.register_callback(self._handle_system_event)
        
        self.running = True
        while self.running:
            try:
                user_input = input("\n🤖 STARK> ").strip()
                
                if user_input.lower() == 'exit':
                    self.running = False
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                elif user_input.startswith('/'):
                    await self._handle_command(user_input)
                else:
                    await self._handle_chat(user_input)
                    
            except KeyboardInterrupt:
                self.running = False
                break
                
        print("\n👋 STARKAI shutting down...")
        
    async def _handle_chat(self, message: str):
        """Handle general chat messages"""
        context = await self._gather_context()
        
        response = await self.llm.generate_response(message, context)
        
        response = self.personality.apply_personality_filter(response, context)
        
        print(f"\n🎯 {response}")
        
    async def _handle_command(self, command: str):
        """Handle special commands"""
        parts = command[1:].split()
        cmd = parts[0] if parts else ""
        
        if cmd == "intel":
            topics = parts[1:] if len(parts) > 1 else ["python", "ai", "technology"]
            intel = await self.intel.gather_tech_intelligence(topics)
            print(f"\n📊 Intelligence Report:")
            print(f"Reddit trends: {len(intel['reddit_trends'])} items")
            print(f"GitHub trends: {len(intel['github_trends'])} items")
            
        elif cmd == "system":
            print(f"\n💻 System Status:")
            print(f"CPU: {self.monitor.system_state.get('cpu_percent', 'N/A')}%")
            print(f"Memory: {self.monitor.system_state.get('memory', {}).get('percent', 'N/A')}%")
            
        elif cmd == "fix":
            if len(parts) > 1:
                file_path = parts[1]
                analysis = await self.fixer.analyze_and_fix(file_path)
                print(f"\n🔧 Code Analysis for {file_path}:")
                print(f"Issues found: {len(analysis['issues'])}")
                for issue in analysis['issues'][:5]:
                    print(f"  Line {issue['line']}: {issue['message']}")
            else:
                print("Usage: /fix <file_path>")
                
        elif cmd == "hardware":
            if len(parts) > 2:
                action, device = parts[1], parts[2]
                if action == "connect":
                    port = parts[3] if len(parts) > 3 else "/dev/ttyUSB0"
                    success = await self.hardware.connect_device(device, port)
                    print(f"🔌 Device {device}: {'Connected' if success else 'Failed'}")
                elif action == "read":
                    data = await self.hardware.read_sensors(device)
                    print(f"📡 {device} sensors: {data}")
            else:
                print("Usage: /hardware <connect|read> <device_name> [port]")
                
        else:
            print(f"Unknown command: {cmd}")
            
    async def _gather_context(self) -> Dict[str, Any]:
        """Gather current system context"""
        return {
            "system_state": self.monitor.system_state,
            "timestamp": self.monitor.system_state.get('timestamp'),
            "active_connections": list(self.hardware.connections.keys())
        }
        
    async def _handle_system_event(self, event_type: str, data: Dict[str, Any]):
        """Handle system monitoring events"""
        if event_type == "high_cpu":
            print(f"\n⚠️  High CPU usage detected: {data['cpu_percent']}%")
        elif event_type == "high_memory":
            print(f"\n⚠️  High memory usage detected: {data['memory']['percent']}%")
        elif event_type == "file_modified":
            print(f"\n📝 File modified: {data['path']}")
            
    def _show_help(self):
        """Show available commands"""
        print("""
🎯 STARKAI Commands:

Chat:
- Just type your message for AI assistance

Commands:
- /intel [topics...]     - Gather intelligence on topics
- /system               - Show system status
- /fix <file>           - Analyze and fix code issues
- /hardware <action>    - Hardware device control
- help                  - Show this help
- exit                  - Quit STARKAI
""")

async def main():
    parser = argparse.ArgumentParser(description="STARKAI - Tony Stark AI Assistant")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
    parser.add_argument("--command", "-c", help="Execute single command")
    
    args = parser.parse_args()
    
    cli = StarkAICLI()
    
    if args.interactive or not args.command:
        await cli.start_interactive_mode()
    else:
        await cli._handle_chat(args.command)

if __name__ == "__main__":
    asyncio.run(main())
