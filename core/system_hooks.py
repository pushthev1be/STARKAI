"""
System Hooks Module
Monitors active files, processes, and usage patterns
"""

import os
import psutil
import time
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

class SystemMonitor:
    """Monitors system status and usage patterns"""
    
    def __init__(self):
        self.monitoring_active = False
        self.activity_log = []
        self.project_paths = set()
        self.last_scan_time = 0
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'status': 'operational',
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': self._get_cpu_usage(),
            'memory_usage': self._get_memory_usage(),
            'disk_usage': self._get_disk_usage(),
            'active_projects': len(self.project_paths),
            'recent_activity': self._get_recent_activity(),
            'running_processes': self._get_relevant_processes()
        }
        
        if status['cpu_usage'] > 90 or status['memory_usage'] > 90:
            status['status'] = 'high_load'
        elif status['cpu_usage'] > 70 or status['memory_usage'] > 70:
            status['status'] = 'moderate_load'
        
        return status
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=1)
        except Exception:
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            return psutil.virtual_memory().percent
        except Exception:
            return 0.0
    
    def _get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage for relevant partitions"""
        try:
            disk_info = {}
            
            home_usage = psutil.disk_usage(os.path.expanduser('~'))
            disk_info['home'] = (home_usage.used / home_usage.total) * 100
            
            root_usage = psutil.disk_usage('/')
            disk_info['root'] = (root_usage.used / root_usage.total) * 100
            
            return disk_info
        except Exception:
            return {'home': 0.0, 'root': 0.0}
    
    def _get_recent_activity(self) -> str:
        """Get description of recent system activity"""
        try:
            dev_dirs = [
                os.path.expanduser('~/'),
                '/tmp',
                '/var/log'
            ]
            
            recent_files = []
            cutoff_time = time.time() - 3600  # Last hour
            
            for directory in dev_dirs:
                if os.path.exists(directory):
                    try:
                        for root, dirs, files in os.walk(directory):
                            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                                     d not in ['node_modules', '__pycache__', 'venv', 'env']]
                            
                            for file in files[:10]:  # Limit to avoid performance issues
                                file_path = os.path.join(root, file)
                                try:
                                    if os.path.getmtime(file_path) > cutoff_time:
                                        recent_files.append(file_path)
                                except (OSError, IOError):
                                    continue
                            
                            if len(recent_files) > 20:  # Limit results
                                break
                    except (OSError, IOError):
                        continue
            
            if recent_files:
                return f"Found {len(recent_files)} recently modified files"
            else:
                return "No significant recent activity detected"
                
        except Exception:
            return "Activity monitoring unavailable"
    
    def _get_relevant_processes(self) -> List[Dict[str, Any]]:
        """Get list of development-relevant running processes"""
        try:
            relevant_processes = []
            dev_keywords = [
                'python', 'node', 'npm', 'yarn', 'pnpm', 'pip', 'poetry',
                'git', 'code', 'vim', 'emacs', 'docker', 'kubectl',
                'java', 'mvn', 'gradle', 'cargo', 'rustc', 'go'
            ]
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    if any(keyword in proc_name for keyword in dev_keywords):
                        relevant_processes.append({
                            'name': proc_info['name'],
                            'pid': proc_info['pid'],
                            'cpu_percent': proc_info['cpu_percent'] or 0,
                            'memory_percent': proc_info['memory_percent'] or 0
                        })
                        
                        if len(relevant_processes) >= 10:  # Limit results
                            break
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return relevant_processes
            
        except Exception:
            return []
    
    def scan_for_projects(self, base_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scan for development projects in the system"""
        if base_path is None:
            base_path = os.path.expanduser('~')
        
        projects = []
        project_indicators = [
            'package.json',      # Node.js
            'requirements.txt',  # Python
            'pyproject.toml',   # Python Poetry
            'Cargo.toml',       # Rust
            'pom.xml',          # Java Maven
            'build.gradle',     # Java Gradle
            'go.mod',           # Go
            '.git',             # Git repository
            'Dockerfile',       # Docker
            'docker-compose.yml' # Docker Compose
        ]
        
        try:
            for root, dirs, files in os.walk(base_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d not in ['node_modules', '__pycache__', 'venv', 'env', 'target', 'build']]
                
                project_files = [f for f in files if f in project_indicators]
                has_git = '.git' in dirs
                
                if project_files or has_git:
                    project_info = {
                        'path': root,
                        'name': os.path.basename(root),
                        'type': self._determine_project_type(project_files, dirs),
                        'last_modified': self._get_directory_last_modified(root),
                        'size': self._get_directory_size(root)
                    }
                    projects.append(project_info)
                    self.project_paths.add(root)
                
                if root.count(os.sep) - base_path.count(os.sep) > 3:
                    dirs.clear()
                    
                if len(projects) > 50:  # Limit total projects found
                    break
                    
        except Exception as e:
            projects.append({
                'path': base_path,
                'name': 'scan_error',
                'type': 'unknown',
                'error': str(e)
            })
        
        return projects
    
    def _determine_project_type(self, files: List[str], dirs: List[str]) -> str:
        """Determine project type based on files and directories"""
        if 'package.json' in files:
            return 'nodejs'
        elif any(f in files for f in ['requirements.txt', 'pyproject.toml', 'setup.py']):
            return 'python'
        elif 'Cargo.toml' in files:
            return 'rust'
        elif any(f in files for f in ['pom.xml', 'build.gradle']):
            return 'java'
        elif 'go.mod' in files:
            return 'go'
        elif '.git' in dirs:
            return 'git_repository'
        elif any(f in files for f in ['Dockerfile', 'docker-compose.yml']):
            return 'docker'
        else:
            return 'unknown'
    
    def _get_directory_last_modified(self, path: str) -> str:
        """Get last modified time of directory"""
        try:
            mtime = os.path.getmtime(path)
            return datetime.fromtimestamp(mtime).isoformat()
        except Exception:
            return "unknown"
    
    def _get_directory_size(self, path: str) -> int:
        """Get approximate directory size (limited scan for performance)"""
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'venv', 'env']]
                
                for file in files[:100]:  # Limit files per directory
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                        
                        if file_count > 1000:  # Limit total files scanned
                            return total_size
                    except (OSError, IOError):
                        continue
                        
            return total_size
        except Exception:
            return 0
    
    def monitor_file_changes(self, paths: List[str]) -> Dict[str, Any]:
        """Monitor file changes in specified paths"""
        changes = {
            'modified_files': [],
            'new_files': [],
            'deleted_files': [],
            'timestamp': datetime.now().isoformat()
        }
        
        for path in paths:
            if os.path.exists(path):
                try:
                    mtime = os.path.getmtime(path)
                    if mtime > self.last_scan_time:
                        changes['modified_files'].append(path)
                except Exception:
                    continue
        
        self.last_scan_time = time.time()
        return changes
    
    def get_system_recommendations(self) -> List[str]:
        """Get system optimization recommendations"""
        recommendations = []
        status = self.get_system_status()
        
        if status['cpu_usage'] > 80:
            recommendations.append("High CPU usage detected. Consider closing unnecessary applications.")
        
        if status['memory_usage'] > 80:
            recommendations.append("High memory usage detected. Consider restarting memory-intensive applications.")
        
        disk_usage = status.get('disk_usage', {})
        for partition, usage in disk_usage.items():
            if usage > 85:
                recommendations.append(f"Disk space low on {partition} partition. Consider cleaning up files.")
        
        if not recommendations:
            recommendations.append("System performance is optimal.")
        
        return recommendations
