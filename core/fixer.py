"""
Code Fixer - Automated code analysis and patching logic
Provides intelligent code fixing and improvement capabilities
"""

import os
import re
import ast
import json
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

class CodeFixer:
    """Automated code analysis and fixing"""
    
    def __init__(self):
        self.supported_languages = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust'
        }
        
        self.common_fixes = {
            'python': [
                self._fix_python_imports,
                self._fix_python_syntax,
                self._fix_python_style,
                self._fix_python_security
            ],
            'javascript': [
                self._fix_js_syntax,
                self._fix_js_style
            ]
        }
        
        self.fix_history = []
    
    def fix_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze and fix a single file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": f"File {file_path} does not exist"}
        
        language = self.supported_languages.get(file_path.suffix.lower())
        if not language:
            return {"error": f"Unsupported file type: {file_path.suffix}"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            issues = self._analyze_file(file_path, original_content, language)
            
            fixed_content, applied_fixes = self._apply_fixes(original_content, language, issues)
            
            if fixed_content != original_content:
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                fix_result = {
                    "status": "fixed",
                    "file": str(file_path),
                    "backup": str(backup_path),
                    "issues_found": len(issues),
                    "fixes_applied": len(applied_fixes),
                    "issues": issues,
                    "fixes": applied_fixes
                }
            else:
                fix_result = {
                    "status": "no_changes_needed",
                    "file": str(file_path),
                    "issues_found": len(issues),
                    "issues": issues
                }
            
            self.fix_history.append({
                "timestamp": __import__('time').time(),
                "file": str(file_path),
                "result": fix_result
            })
            
            return fix_result
            
        except Exception as e:
            return {"error": f"Error processing {file_path}: {str(e)}"}
    
    def fix_project(self, directory: str) -> Dict[str, Any]:
        """Fix all supported files in a project directory"""
        directory = Path(directory)
        
        if not directory.exists():
            return {"error": f"Directory {directory} does not exist"}
        
        results = {
            "directory": str(directory),
            "files_processed": 0,
            "files_fixed": 0,
            "total_issues": 0,
            "total_fixes": 0,
            "file_results": []
        }
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_languages:
                if file_path.name.startswith('.') or file_path.suffix == '.backup':
                    continue
                
                file_result = self.fix_file(file_path)
                results["file_results"].append(file_result)
                results["files_processed"] += 1
                
                if file_result.get("status") == "fixed":
                    results["files_fixed"] += 1
                
                results["total_issues"] += file_result.get("issues_found", 0)
                results["total_fixes"] += file_result.get("fixes_applied", 0)
        
        return results
    
    def _analyze_file(self, file_path: Path, content: str, language: str) -> List[Dict[str, Any]]:
        """Analyze file for issues"""
        issues = []
        
        if language == 'python':
            issues.extend(self._analyze_python(content))
        elif language in ['javascript', 'typescript']:
            issues.extend(self._analyze_javascript(content))
        
        issues.extend(self._analyze_common_issues(content))
        
        return issues
    
    def _analyze_python(self, content: str) -> List[Dict[str, Any]]:
        """Analyze Python-specific issues"""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in content:
                            issues.append({
                                "type": "unused_import",
                                "line": node.lineno,
                                "message": f"Unused import: {alias.name}",
                                "severity": "warning"
                            })
                
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        issues.append({
                            "type": "missing_docstring",
                            "line": node.lineno,
                            "message": f"Missing docstring for {node.name}",
                            "severity": "info"
                        })
        
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "line": e.lineno,
                "message": f"Syntax error: {e.msg}",
                "severity": "error"
            })
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append({
                    "type": "long_line",
                    "line": i,
                    "message": f"Line too long ({len(line)} characters)",
                    "severity": "warning"
                })
            
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    "type": "trailing_whitespace",
                    "line": i,
                    "message": "Trailing whitespace",
                    "severity": "info"
                })
        
        return issues
    
    def _analyze_javascript(self, content: str) -> List[Dict[str, Any]]:
        """Analyze JavaScript-specific issues"""
        issues = []
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(r'[^;{}]\s*$', line.strip()) and line.strip() and not line.strip().startswith('//'):
                if any(keyword in line for keyword in ['var ', 'let ', 'const ', 'return ', 'throw ']):
                    issues.append({
                        "type": "missing_semicolon",
                        "line": i,
                        "message": "Missing semicolon",
                        "severity": "warning"
                    })
            
            if 'var ' in line:
                issues.append({
                    "type": "use_var",
                    "line": i,
                    "message": "Use 'let' or 'const' instead of 'var'",
                    "severity": "warning"
                })
        
        return issues
    
    def _analyze_common_issues(self, content: str) -> List[Dict[str, Any]]:
        """Analyze common issues across all languages"""
        issues = []
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'TODO' in line.upper():
                issues.append({
                    "type": "todo_comment",
                    "line": i,
                    "message": "TODO comment found",
                    "severity": "info"
                })
            
            if 'FIXME' in line.upper():
                issues.append({
                    "type": "fixme_comment",
                    "line": i,
                    "message": "FIXME comment found",
                    "severity": "warning"
                })
            
            if re.search(r'(password|key|secret|token)\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                issues.append({
                    "type": "hardcoded_secret",
                    "line": i,
                    "message": "Potential hardcoded secret",
                    "severity": "error"
                })
        
        return issues
    
    def _apply_fixes(self, content: str, language: str, issues: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Apply automatic fixes to content"""
        fixed_content = content
        applied_fixes = []
        
        if language in self.common_fixes:
            for fix_function in self.common_fixes[language]:
                try:
                    fixed_content, fixes = fix_function(fixed_content, issues)
                    applied_fixes.extend(fixes)
                except Exception as e:
                    print(f"Error applying fix: {e}")
        
        return fixed_content, applied_fixes
    
    def _fix_python_imports(self, content: str, issues: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Fix Python import issues"""
        fixes = []
        lines = content.split('\n')
        
        for issue in issues:
            if issue["type"] == "unused_import":
                line_num = issue["line"] - 1
                if line_num < len(lines):
                    lines[line_num] = ""
                    fixes.append({
                        "type": "removed_unused_import",
                        "line": issue["line"],
                        "description": f"Removed unused import on line {issue['line']}"
                    })
        
        return '\n'.join(lines), fixes
    
    def _fix_python_syntax(self, content: str, issues: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Fix Python syntax issues"""
        fixes = []
        return content, fixes
    
    def _fix_python_style(self, content: str, issues: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Fix Python style issues"""
        fixes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.endswith(' ') or line.endswith('\t'):
                lines[i] = line.rstrip()
                fixes.append({
                    "type": "removed_trailing_whitespace",
                    "line": i + 1,
                    "description": f"Removed trailing whitespace on line {i + 1}"
                })
        
        return '\n'.join(lines), fixes
    
    def _fix_python_security(self, content: str, issues: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Fix Python security issues"""
        fixes = []
        return content, fixes
    
    def _fix_js_syntax(self, content: str, issues: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Fix JavaScript syntax issues"""
        fixes = []
        lines = content.split('\n')
        
        for issue in issues:
            if issue["type"] == "missing_semicolon":
                line_num = issue["line"] - 1
                if line_num < len(lines):
                    lines[line_num] = lines[line_num].rstrip() + ';'
                    fixes.append({
                        "type": "added_semicolon",
                        "line": issue["line"],
                        "description": f"Added semicolon on line {issue['line']}"
                    })
        
        return '\n'.join(lines), fixes
    
    def _fix_js_style(self, content: str, issues: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Fix JavaScript style issues"""
        fixes = []
        return content, fixes
    
    def generate_patch(self, original_content: str, fixed_content: str, filename: str) -> str:
        """Generate a unified diff patch"""
        import difflib
        
        original_lines = original_content.splitlines(keepends=True)
        fixed_lines = fixed_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm=""
        )
        
        return ''.join(diff)
    
    def run_linter(self, file_path: str, language: str) -> Dict[str, Any]:
        """Run external linter on file"""
        linter_commands = {
            'python': ['flake8', '--max-line-length=100'],
            'javascript': ['eslint'],
            'typescript': ['tslint']
        }
        
        if language not in linter_commands:
            return {"error": f"No linter configured for {language}"}
        
        try:
            cmd = linter_commands[language] + [file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "linter": cmd[0]
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Linter timed out"}
        except FileNotFoundError:
            return {"error": f"Linter {cmd[0]} not found"}
        except Exception as e:
            return {"error": f"Linter error: {str(e)}"}
    
    def get_fix_suggestions(self, file_path: str) -> List[Dict[str, Any]]:
        """Get fix suggestions for a file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return []
        
        language = self.supported_languages.get(file_path.suffix.lower())
        if not language:
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = self._analyze_file(file_path, content, language)
            
            suggestions = []
            for issue in issues:
                suggestion = {
                    "issue": issue,
                    "auto_fixable": issue["type"] in [
                        "trailing_whitespace", 
                        "unused_import", 
                        "missing_semicolon"
                    ],
                    "priority": self._get_issue_priority(issue["severity"])
                }
                suggestions.append(suggestion)
            
            return sorted(suggestions, key=lambda x: x["priority"], reverse=True)
            
        except Exception as e:
            return [{"error": f"Error analyzing {file_path}: {str(e)}"}]
    
    def _get_issue_priority(self, severity: str) -> int:
        """Get numeric priority for issue severity"""
        priorities = {
            "error": 3,
            "warning": 2,
            "info": 1
        }
        return priorities.get(severity, 0)
    
    def get_status(self) -> Dict[str, Any]:
        """Get fixer status and statistics"""
        return {
            "supported_languages": list(self.supported_languages.values()),
            "fix_history_count": len(self.fix_history),
            "recent_fixes": self.fix_history[-5:] if self.fix_history else [],
            "available_fixers": {
                lang: len(fixers) for lang, fixers in self.common_fixes.items()
            }
        }
