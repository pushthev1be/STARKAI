#!/usr/bin/env python3
"""
StarkAI v1.0 - Core Intelligence Unit
Entry point for the Tony Stark-inspired AI assistant
"""

import sys
import argparse
from interface.cli import StarkCLI

def main():
    """Main entry point for StarkAI"""
    parser = argparse.ArgumentParser(
        description="StarkAI v1.0 - Your sarcastic AI assistant with a genius complex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Commands:
  intel     - Gather intelligence from social platforms
  fix       - Auto-fix code issues in your projects  
  scan      - Analyze codebase for problems
  pulse     - Check system status and trends
  chat      - Interactive conversation mode
  
Examples:
  python main.py intel --trends
  python main.py fix /path/to/project
  python main.py scan --python /path/to/code
  python main.py pulse
        """
    )
    
    parser.add_argument('command', nargs='?', default='chat',
                       choices=['intel', 'fix', 'scan', 'pulse', 'chat'],
                       help='Command to execute')
    parser.add_argument('--path', type=str, help='Path to project or file')
    parser.add_argument('--trends', action='store_true', help='Show trending topics')
    parser.add_argument('--python', action='store_true', help='Focus on Python code')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        cli = StarkCLI()
        cli.run(args)
    except KeyboardInterrupt:
        print("\n[STARK] Interrupted by user. Even I need a break sometimes.")
        sys.exit(0)
    except Exception as e:
        print(f"[STARK] Well, this is embarrassing. Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
