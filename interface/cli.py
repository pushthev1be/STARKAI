"""
Command Line Interface for STARKAI
Provides interactive CLI for user interaction with the AI assistant
"""

import cmd
import sys
from typing import Optional, Dict, Any
from colorama import init, Fore, Back, Style

init(autoreset=True)

class CLI(cmd.Cmd):
    """Interactive command line interface for STARKAI"""
    
    intro = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                        STARKAI ASSISTANT                     ║
║                     Tony Stark AI System                     ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

Type 'help' for available commands or 'quit' to exit.
"""
    
    prompt = f"{Fore.YELLOW}STARKAI> {Style.RESET_ALL}"
    
    def __init__(self, stark_ai):
        super().__init__()
        self.stark_ai = stark_ai
        self.conversation_history = []
    
    def run_interactive(self):
        """Run the interactive CLI"""
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Interrupted by user{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}CLI Error: {e}{Style.RESET_ALL}")
    
    def do_ask(self, line):
        """Ask STARKAI a question
        Usage: ask <your question>
        """
        if not line.strip():
            print(f"{Fore.RED}Please provide a question{Style.RESET_ALL}")
            return
        
        print(f"{Fore.BLUE}Processing...{Style.RESET_ALL}")
        
        try:
            response = self.stark_ai.llm_engine.generate_response(line)
            print(f"{Fore.GREEN}STARKAI: {response}{Style.RESET_ALL}")
            
            self.conversation_history.append({
                "user": line,
                "assistant": response
            })
            
        except Exception as e:
            print(f"{Fore.RED}Error generating response: {e}{Style.RESET_ALL}")
    
    def do_status(self, line):
        """Show system status
        Usage: status
        """
        print(f"{Fore.CYAN}=== STARKAI System Status ==={Style.RESET_ALL}")
        
        llm_status = self.stark_ai.llm_engine.get_status()
        print(f"LLM Engine:")
        print(f"  OpenAI: {'✓' if llm_status['openai_available'] else '✗'}")
        print(f"  Local Model: {'✓' if llm_status['local_model_available'] else '✗'}")
        print(f"  Personality: {'✓' if llm_status['personality_active'] else '✗'}")
        
        hw_status = self.stark_ai.hardware_helper.get_status()
        print(f"Hardware:")
        print(f"  Connected Devices: {hw_status['connected_devices']}")
        print(f"  Available Ports: {len(hw_status['available_ports'])}")
        
        sys_status = self.stark_ai.system_monitor.get_status()
        print(f"System Monitor:")
        print(f"  Active: {'✓' if sys_status['monitoring_active'] else '✗'}")
        print(f"  Tracked Files: {sys_status['tracked_files']}")
        print(f"  Tracked Processes: {sys_status['tracked_processes']}")
        
        intel_status = self.stark_ai.intel_collector.get_status()
        print(f"Intelligence Collector:")
        print(f"  Reddit: {'✓' if intel_status['reddit_connected'] else '✗'}")
        print(f"  Twitter: {'✓' if intel_status['twitter_connected'] else '✗'}")
        print(f"  GitHub: {'✓' if intel_status['github_connected'] else '✗'}")
    
    def do_hardware(self, line):
        """Hardware interface commands
        Usage: 
          hardware list - List available devices
          hardware connect <port> - Connect to device
          hardware send <device_id> <command> - Send command to device
          hardware disconnect <device_id> - Disconnect device
        """
        args = line.split()
        
        if not args:
            print("Usage: hardware <list|connect|send|disconnect> [args]")
            return
        
        command = args[0]
        
        if command == "list":
            devices = self.stark_ai.hardware_helper.list_devices()
            print(f"{Fore.CYAN}Available Hardware:{Style.RESET_ALL}")
            for device in devices:
                print(f"  {device}")
        
        elif command == "connect" and len(args) > 1:
            port = args[1]
            result = self.stark_ai.hardware_helper.connect_device(port)
            if result:
                print(f"{Fore.GREEN}Connected to {port}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to connect to {port}{Style.RESET_ALL}")
        
        elif command == "send" and len(args) > 2:
            device_id = args[1]
            command_text = " ".join(args[2:])
            result = self.stark_ai.hardware_helper.send_command(device_id, command_text)
            print(f"Response: {result}")
        
        elif command == "disconnect" and len(args) > 1:
            device_id = args[1]
            self.stark_ai.hardware_helper.disconnect_device(device_id)
            print(f"{Fore.YELLOW}Disconnected {device_id}{Style.RESET_ALL}")
        
        else:
            print("Invalid hardware command")
    
    def do_intel(self, line):
        """Intelligence collection commands
        Usage:
          intel reddit <subreddit> - Collect from Reddit
          intel twitter <query> - Collect from Twitter  
          intel github <repo> - Collect from GitHub
          intel status - Show collection status
        """
        args = line.split()
        
        if not args:
            print("Usage: intel <reddit|twitter|github|status> [args]")
            return
        
        command = args[0]
        
        if command == "reddit" and len(args) > 1:
            subreddit = args[1]
            print(f"Collecting from r/{subreddit}...")
            data = self.stark_ai.intel_collector.collect_reddit_data(subreddit)
            print(f"Collected {len(data)} posts")
        
        elif command == "twitter" and len(args) > 1:
            query = " ".join(args[1:])
            print(f"Searching Twitter for: {query}")
            data = self.stark_ai.intel_collector.collect_twitter_data(query)
            print(f"Collected {len(data)} tweets")
        
        elif command == "github" and len(args) > 1:
            repo = args[1]
            print(f"Analyzing GitHub repo: {repo}")
            data = self.stark_ai.intel_collector.collect_github_data(repo)
            print(f"Collected repository data")
        
        elif command == "status":
            status = self.stark_ai.intel_collector.get_status()
            print(f"Intelligence Collection Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
        
        else:
            print("Invalid intel command")
    
    def do_fix(self, line):
        """Code fixing commands
        Usage:
          fix file <filepath> - Analyze and fix code file
          fix project <directory> - Fix entire project
        """
        args = line.split()
        
        if not args:
            print("Usage: fix <file|project> <path>")
            return
        
        command = args[0]
        
        if command == "file" and len(args) > 1:
            filepath = args[1]
            print(f"Analyzing {filepath}...")
            result = self.stark_ai.code_fixer.fix_file(filepath)
            print(f"Fix result: {result}")
        
        elif command == "project" and len(args) > 1:
            directory = args[1]
            print(f"Fixing project in {directory}...")
            result = self.stark_ai.code_fixer.fix_project(directory)
            print(f"Project fix complete: {result}")
        
        else:
            print("Invalid fix command")
    
    def do_history(self, line):
        """Show conversation history
        Usage: history [count]
        """
        try:
            count = int(line) if line.strip() else 10
        except ValueError:
            count = 10
        
        print(f"{Fore.CYAN}=== Conversation History (last {count}) ==={Style.RESET_ALL}")
        
        for i, entry in enumerate(self.conversation_history[-count:], 1):
            print(f"{Fore.YELLOW}{i}. User: {entry['user']}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}   STARKAI: {entry['assistant']}{Style.RESET_ALL}")
            print()
    
    def do_clear(self, line):
        """Clear the screen
        Usage: clear
        """
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def do_quit(self, line):
        """Exit STARKAI
        Usage: quit
        """
        print(f"{Fore.CYAN}STARKAI shutting down. Goodbye!{Style.RESET_ALL}")
        return True
    
    def do_exit(self, line):
        """Exit STARKAI (alias for quit)
        Usage: exit
        """
        return self.do_quit(line)
    
    def default(self, line):
        """Handle unknown commands by treating them as questions"""
        if line.strip():
            print(f"{Fore.YELLOW}Interpreting as question...{Style.RESET_ALL}")
            self.do_ask(line)
        else:
            print(f"{Fore.RED}Unknown command. Type 'help' for available commands.{Style.RESET_ALL}")
    
    def emptyline(self):
        """Handle empty line input"""
        pass
