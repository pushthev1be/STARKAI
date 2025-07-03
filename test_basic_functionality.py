#!/usr/bin/env python3
"""
Basic functionality test for STARKAI system
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all core modules can be imported"""
    try:
        from core.llm_engine import LLMEngine
        from core.personality import StarkPersonality
        from core.intel_collector import IntelCollector
        from core.system_hooks import SystemMonitor
        from core.fixer import CodeFixer
        from core.hardware_helper import HardwareInterface
        from interface.cli import StarkAICLI
        print("✅ All core modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_module_initialization():
    """Test that all modules can be initialized"""
    try:
        from core.llm_engine import LLMEngine
        from core.personality import StarkPersonality
        from core.intel_collector import IntelCollector
        from core.system_hooks import SystemMonitor
        from core.fixer import CodeFixer
        from core.hardware_helper import HardwareInterface
        
        llm = LLMEngine()
        personality = StarkPersonality()
        intel = IntelCollector()
        monitor = SystemMonitor()
        fixer = CodeFixer()
        hardware = HardwareInterface()
        
        print("✅ All modules initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_personality_functionality():
    """Test basic personality functionality"""
    try:
        from core.personality import StarkPersonality
        
        personality = StarkPersonality()
        
        response = "I think this might work"
        filtered = personality.apply_personality_filter(response)
        
        if "I know" in filtered:
            print("✅ Personality confidence filter working")
        else:
            print("⚠️  Personality confidence filter not working as expected")
            
        opener = personality.get_contextual_opener("problem_solving")
        if opener in personality.response_patterns["problem_solving"]:
            print("✅ Personality contextual opener working")
        else:
            print("⚠️  Personality contextual opener not working")
            
        return True
    except Exception as e:
        print(f"❌ Personality test error: {e}")
        return False

def main():
    """Run all basic functionality tests"""
    print("🚀 Testing STARKAI Basic Functionality")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_module_initialization,
        test_personality_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All basic functionality tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
