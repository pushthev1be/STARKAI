"""
Code Fixer Module
Handles automatic code analysis and fixing for Python projects
"""

import os
import ast
import re
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path

from core.llm_engine import LLMEngine

class CodeFixer:
    """Handles code analysis and automatic fixing"""
    
    def __init__(self):
        self.llm_engine = LLMEngine()
        self.supported_extensions = {'.py', '.pyx'}
        self.common_issues = {
            'syntax_errors': [],
            'import_errors': [],
            'style_issues': [],
            'logic_issues': []
        }
    
    def fix_project(self, project_path: str, focus_python: bool = True) -> Dict[str, Any]:
        """Fix issues in an entire project"""
        results = {
            'files_analyzed': 0,
            'issues_found': 0,
            'fixes_applied': 0,
            'fixes': []
        }
        
        if os.path.isfile(project_path):
            files_to_fix = [project_path]
        else:
            files_to_fix = self._find_code_files(project_path, focus_python)
        
        for file_path in files_to_fix:
            file_results = self._fix_file(file_path)
            results['files_analyzed'] += 1
            results['issues_found'] += file_results['issues_found']
            results['fixes_applied'] += file_results['fixes_applied']
            results['fixes'].extend(file_results['fixes'])
        
        return results
    
    def analyze_project(self, project_path: str, focus_python: bool = True) -> Dict[str, Any]:
        """Analyze project without making changes"""
        results = {
            'files_scanned': 0,
            'total_issues': 0,
            'quality_score': 0,
            'issues': []
        }
        
        if os.path.isfile(project_path):
            files_to_scan = [project_path]
        else:
            files_to_scan = self._find_code_files(project_path, focus_python)
        
        total_quality = 0
        for file_path in files_to_scan:
            file_results = self._analyze_file(file_path)
            results['files_scanned'] += 1
            results['total_issues'] += file_results['issues_count']
            results['issues'].extend(file_results['issues'])
            total_quality += file_results['quality_score']
        
        if results['files_scanned'] > 0:
            results['quality_score'] = round(total_quality / results['files_scanned'], 1)
        
        return results
    
    def _find_code_files(self, directory: str, focus_python: bool = True) -> List[str]:
        """Find code files in directory"""
        code_files = []
        extensions = self.supported_extensions if focus_python else {'.py', '.js', '.ts', '.java', '.cpp', '.c'}
        
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    code_files.append(os.path.join(root, file))
        
        return code_files
    
    def _fix_file(self, file_path: str) -> Dict[str, Any]:
        """Fix issues in a single file"""
        results = {
            'issues_found': 0,
            'fixes_applied': 0,
            'fixes': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            analysis = self._analyze_file_content(original_content, file_path)
            results['issues_found'] = len(analysis['issues'])
            
            if analysis['issues']:
                fixed_content = self._get_llm_fixes(original_content, analysis['issues'], file_path)
                
                if fixed_content and fixed_content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    results['fixes_applied'] = len(analysis['issues'])
                    results['fixes'].append(f"Fixed {len(analysis['issues'])} issues in {file_path}")
            
        except Exception as e:
            results['fixes'].append(f"Error processing {file_path}: {str(e)}")
        
        return results
    
    def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for issues"""
        results = {
            'issues_count': 0,
            'quality_score': 8,
            'issues': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = self._analyze_file_content(content, file_path)
            results['issues_count'] = len(analysis['issues'])
            results['issues'] = [f"{file_path}: {issue}" for issue in analysis['issues']]
            results['quality_score'] = analysis['quality_score']
            
        except Exception as e:
            results['issues'].append(f"Error analyzing {file_path}: {str(e)}")
            results['quality_score'] = 5
        
        return results
    
    def _analyze_file_content(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze file content for various issues"""
        issues = []
        quality_score = 10
        
        if file_path.endswith('.py'):
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(f"Syntax error: {e}")
                quality_score -= 3
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(f"Line {i}: Line too long ({len(line)} chars)")
                quality_score -= 0.1
        
        todo_count = len(re.findall(r'#\s*TODO|#\s*FIXME|#\s*HACK', content, re.IGNORECASE))
        if todo_count > 0:
            issues.append(f"Found {todo_count} TODO/FIXME comments")
            quality_score -= 0.5 * todo_count
        
        if file_path.endswith('.py'):
            import_lines = re.findall(r'^import\s+(\w+)|^from\s+(\w+)', content, re.MULTILINE)
            for match in import_lines:
                module = match[0] or match[1]
                if module and module not in content.replace(f'import {module}', '').replace(f'from {module}', ''):
                    issues.append(f"Potentially unused import: {module}")
                    quality_score -= 0.2
        
        empty_except = len(re.findall(r'except.*:\s*pass', content))
        if empty_except > 0:
            issues.append(f"Found {empty_except} empty except blocks")
            quality_score -= 1 * empty_except
        
        return {
            'issues': issues,
            'quality_score': max(1, min(10, quality_score))
        }
    
    def _get_llm_fixes(self, content: str, issues: List[str], file_path: str) -> Optional[str]:
        """Use LLM to generate fixes for code issues"""
        try:
            issues_text = '\n'.join(f"- {issue}" for issue in issues)
            
            response = self.llm_engine.suggest_fix(
                content, 
                f"Issues found:\n{issues_text}",
                "python" if file_path.endswith('.py') else "code"
            )
            
            if response.success:
                code_match = re.search(r'```(?:python|py)?\n(.*?)\n```', response.content, re.DOTALL)
                if code_match:
                    return code_match.group(1)
                else:
                    return content
            
        except Exception:
            pass
        
        return None
    
    def run_linter(self, file_path: str) -> Dict[str, Any]:
        """Run external linter on file"""
        results = {'issues': [], 'success': False}
        
        try:
            result = subprocess.run(
                ['flake8', file_path], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                results['success'] = True
            else:
                results['issues'] = result.stdout.split('\n')
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return results
