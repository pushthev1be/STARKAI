"""
StarkAI Command Line Interface
Handles all CLI interactions with Tony Stark personality
"""

import os
import sys
import time
from typing import Any, Dict, List
from argparse import Namespace

from core.personality import StarkPersonality
from core.llm_engine import LLMEngine
from core.fixer import CodeFixer
from core.intel_collector import IntelCollector
from core.system_hooks import SystemMonitor

class StarkCLI:
    """Main CLI interface for StarkAI with Tony Stark personality"""
    
    def __init__(self):
        self.personality = StarkPersonality()
        self.llm_engine = LLMEngine()
        self.code_fixer = CodeFixer()
        self.intel_collector = IntelCollector()
        self.system_monitor = SystemMonitor()
        self.session_history = []
        
    def run(self, args: Namespace):
        """Main CLI execution logic"""
        print(self.personality.format_response(self.personality.get_greeting()))
        
        if args.command == "chat":
            self._interactive_mode()
        elif args.command == "intel":
            self._intel_command(args)
        elif args.command == "fix":
            self._fix_command(args)
        elif args.command == "scan":
            self._scan_command(args)
        elif args.command == "pulse":
            self._pulse_command(args)
    
    def _interactive_mode(self):
        """Interactive chat mode with StarkAI"""
        print(self.personality.format_response("Entering interactive mode. Type 'exit' to quit."))
        
        while True:
            try:
                user_input = input("\n[USER] ").strip()
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print(self.personality.format_response("Leaving so soon? Fine, I have better things to do anyway."))
                    break
                
                if not user_input:
                    continue
                
                response = self.llm_engine.generate_response(user_input)
                if response.success:
                    print(self.personality.format_response(response.content))
                else:
                    print(self.personality.format_response(
                        self.personality.get_response("error", False)
                    ))
                
                self.session_history.append({"user": user_input, "stark": response.content})
                
            except KeyboardInterrupt:
                print(self.personality.format_response("\nInterrupted. Even I need a break sometimes."))
                break
            except Exception as e:
                print(self.personality.format_response(f"Error: {e}"))
    
    def _intel_command(self, args: Namespace):
        """Handle intelligence gathering command"""
        print(self.personality.format_response("Gathering intelligence from the digital realm..."))
        
        try:
            if args.trends:
                trends = self.intel_collector.get_trending_topics()
                self._display_trends(trends)
            else:
                intel = self.intel_collector.collect_all_intel()
                self._display_intel(intel)
                
            print(self.personality.format_response(
                self.personality.get_response("intel_gathering", True)
            ))
            
        except Exception as e:
            print(self.personality.format_response(f"Intel gathering failed: {e}"))
    
    def _fix_command(self, args: Namespace):
        """Handle code fixing command"""
        if not args.path:
            print(self.personality.format_response("I need a path to fix something. I'm good, but not psychic."))
            return
        
        if not os.path.exists(args.path):
            print(self.personality.format_response(f"Path '{args.path}' doesn't exist. Check your typing."))
            return
        
        print(self.personality.format_response(f"Analyzing and fixing code at {args.path}..."))
        
        try:
            results = self.code_fixer.fix_project(args.path, focus_python=args.python)
            self._display_fix_results(results)
            
            success = results.get('fixes_applied', 0) > 0
            print(self.personality.format_response(
                self.personality.get_response("code_fix", success)
            ))
            
        except Exception as e:
            print(self.personality.format_response(f"Code fixing failed: {e}"))
    
    def _scan_command(self, args: Namespace):
        """Handle code scanning command"""
        if not args.path:
            print(self.personality.format_response("I need a path to scan. Point me in the right direction."))
            return
        
        if not os.path.exists(args.path):
            print(self.personality.format_response(f"Path '{args.path}' doesn't exist. Try again."))
            return
        
        print(self.personality.format_response(f"Scanning code at {args.path}..."))
        
        try:
            results = self.code_fixer.analyze_project(args.path, focus_python=args.python)
            self._display_scan_results(results)
            
            issues_found = results.get('total_issues', 0) == 0
            print(self.personality.format_response(
                self.personality.get_response("system_scan", issues_found)
            ))
            
        except Exception as e:
            print(self.personality.format_response(f"Code scanning failed: {e}"))
    
    def _pulse_command(self, args: Namespace):
        """Handle system pulse command"""
        print(self.personality.format_response("Checking system pulse and trends..."))
        
        try:
            system_status = self.system_monitor.get_system_status()
            
            trends = self.intel_collector.get_trending_topics()
            
            self._display_pulse(system_status, trends)
            
            print(self.personality.format_response(
                "Pulse check complete. Everything's under control, as usual."
            ))
            
        except Exception as e:
            print(self.personality.format_response(f"Pulse check failed: {e}"))
    
    def _display_trends(self, trends: Dict[str, List[Dict]]):
        """Display trending topics"""
        print("\n" + "="*60)
        print(self.personality.format_response("TRENDING INTELLIGENCE"))
        print("="*60)
        
        for platform, items in trends.items():
            if items:
                print(f"\n📊 {platform.upper()}:")
                for i, item in enumerate(items[:5], 1):
                    title = item.get('title', item.get('name', 'Unknown'))
                    score = item.get('score', item.get('stars', 0))
                    print(f"  {i}. {title} ({score})")
    
    def _display_intel(self, intel: Dict[str, Any]):
        """Display collected intelligence"""
        print("\n" + "="*60)
        print(self.personality.format_response("INTELLIGENCE REPORT"))
        print("="*60)
        
        for source, data in intel.items():
            print(f"\n📡 {source.upper()}:")
            if isinstance(data, list):
                for item in data[:3]:
                    print(f"  • {item}")
            else:
                print(f"  {data}")
    
    def _display_fix_results(self, results: Dict[str, Any]):
        """Display code fixing results"""
        print("\n" + "="*60)
        print(self.personality.format_response("CODE FIX RESULTS"))
        print("="*60)
        
        print(f"Files analyzed: {results.get('files_analyzed', 0)}")
        print(f"Issues found: {results.get('issues_found', 0)}")
        print(f"Fixes applied: {results.get('fixes_applied', 0)}")
        
        if results.get('fixes'):
            print("\nFixes applied:")
            for fix in results['fixes']:
                print(f"  • {fix}")
    
    def _display_scan_results(self, results: Dict[str, Any]):
        """Display code scanning results"""
        print("\n" + "="*60)
        print(self.personality.format_response("CODE SCAN RESULTS"))
        print("="*60)
        
        print(f"Files scanned: {results.get('files_scanned', 0)}")
        print(f"Total issues: {results.get('total_issues', 0)}")
        print(f"Code quality: {results.get('quality_score', 'N/A')}/10")
        
        if results.get('issues'):
            print("\nIssues found:")
            for issue in results['issues'][:10]:
                print(f"  • {issue}")
    
    def _display_pulse(self, system_status: Dict[str, Any], trends: Dict[str, List[Dict]]):
        """Display system pulse information"""
        print("\n" + "="*60)
        print(self.personality.format_response("SYSTEM PULSE"))
        print("="*60)
        
        print(f"System Status: {system_status.get('status', 'Unknown')}")
        print(f"Active Projects: {system_status.get('active_projects', 0)}")
        print(f"Recent Activity: {system_status.get('recent_activity', 'None')}")
        
        print("\n🔥 Hot Topics:")
        for platform, items in trends.items():
            if items:
                top_item = items[0]
                title = top_item.get('title', top_item.get('name', 'Unknown'))
                print(f"  {platform}: {title}")
    
    def _format_output(self, message: str) -> str:
        """Format output with StarkAI styling"""
        return self.personality.format_response(message)
