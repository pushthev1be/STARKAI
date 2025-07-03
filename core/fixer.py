import ast
import os
import subprocess
from typing import Dict, List, Any, Optional
import re

class CodeFixer:
    def __init__(self):
        self.common_fixes = {}
        
    async def analyze_and_fix(self, file_path: str) -> Dict[str, Any]:
        """Analyze code file and suggest/apply fixes"""
        if not os.path.exists(file_path):
            return {"error": "File not found"}
            
        analysis = {
            "file": file_path,
            "issues": [],
            "fixes_applied": [],
            "suggestions": []
        }
        
        with open(file_path, 'r') as f:
            content = f.read()
            
        syntax_issues = self._check_syntax(content)
        analysis["issues"].extend(syntax_issues)
        
        import_issues = self._check_imports(content)
        analysis["issues"].extend(import_issues)
        
        style_issues = self._check_style(file_path)
        analysis["issues"].extend(style_issues)
        
        return analysis
        
    def _check_syntax(self, content: str) -> List[Dict[str, Any]]:
        """Check for Python syntax errors"""
        issues = []
        try:
            ast.parse(content)
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "line": e.lineno,
                "message": str(e),
                "severity": "error"
            })
        return issues
        
    def _check_imports(self, content: str) -> List[Dict[str, Any]]:
        """Check for import issues"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                module_name = self._extract_module_name(line)
                if module_name and module_name not in content.replace(line, ''):
                    issues.append({
                        "type": "unused_import",
                        "line": i,
                        "message": f"Unused import: {module_name}",
                        "severity": "warning"
                    })
        return issues
        
    def _check_style(self, file_path: str) -> List[Dict[str, Any]]:
        """Check for style issues using flake8"""
        issues = []
        try:
            result = subprocess.run(
                ['flake8', file_path, '--format=%(row)d:%(col)d:%(code)s:%(text)s'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        issues.append({
                            "type": "style_issue",
                            "line": int(parts[0]),
                            "column": int(parts[1]),
                            "code": parts[2],
                            "message": parts[3],
                            "severity": "warning"
                        })
        except FileNotFoundError:
            pass
        return issues
        
    def _extract_module_name(self, import_line: str) -> Optional[str]:
        """Extract module name from import statement"""
        if 'import ' in import_line:
            parts = import_line.split('import ')
            if len(parts) > 1:
                return parts[1].split()[0].split('.')[0]
        return None
