"""
System Hooks - Monitors active files, processes, and usage patterns
Provides system monitoring and telemetry for the STARKAI assistant
"""

import os
import time
import json
import threading
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from collections import defaultdict, deque

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class SystemMonitor:
    """System monitoring and telemetry"""
    
    def __init__(self):
        self.monitoring_active = False
        self.monitor_thread = None
        self.tracked_files = set()
        self.tracked_processes = {}
        self.file_access_log = deque(maxlen=1000)
        self.process_log = deque(maxlen=1000)
        self.system_stats = {}
        self.monitoring_interval = 5.0  # seconds
        self.stop_monitoring_flag = threading.Event()
        
    def start_monitoring(self):
        """Start system monitoring"""
        if self.monitoring_active:
            return
        
        print("Starting System Monitor...")
        
        if not PSUTIL_AVAILABLE:
            print("⚠ psutil library not available - limited monitoring")
        
        self.monitoring_active = True
        self.stop_monitoring_flag.clear()
        
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        print("✓ System Monitor started")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        if not self.monitoring_active:
            return
        
        print("Stopping System Monitor...")
        self.monitoring_active = False
        self.stop_monitoring_flag.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        print("✓ System Monitor stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_monitoring_flag.wait(self.monitoring_interval):
            try:
                self._collect_system_stats()
                self._monitor_processes()
                self._monitor_file_system()
            except Exception as e:
                print(f"Monitoring error: {e}")
    
    def _collect_system_stats(self):
        """Collect system statistics"""
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            memory = psutil.virtual_memory()
            
            disk = psutil.disk_usage('/')
            
            network = psutil.net_io_counters()
            
            self.system_stats = {
                "timestamp": time.time(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
            
        except Exception as e:
            print(f"Error collecting system stats: {e}")
    
    def _monitor_processes(self):
        """Monitor running processes"""
        if not PSUTIL_AVAILABLE:
            return
        
        try:
            current_processes = {}
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    info = proc.info
                    pid = info['pid']
                    
                    current_processes[pid] = {
                        "name": info['name'],
                        "cpu_percent": info['cpu_percent'],
                        "memory_percent": info['memory_percent'],
                        "create_time": info['create_time'],
                        "timestamp": time.time()
                    }
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            new_pids = set(current_processes.keys()) - set(self.tracked_processes.keys())
            for pid in new_pids:
                self.process_log.append({
                    "event": "process_started",
                    "pid": pid,
                    "name": current_processes[pid]["name"],
                    "timestamp": time.time()
                })
            
            terminated_pids = set(self.tracked_processes.keys()) - set(current_processes.keys())
            for pid in terminated_pids:
                self.process_log.append({
                    "event": "process_terminated",
                    "pid": pid,
                    "name": self.tracked_processes[pid]["name"],
                    "timestamp": time.time()
                })
            
            self.tracked_processes = current_processes
            
        except Exception as e:
            print(f"Error monitoring processes: {e}")
    
    def _monitor_file_system(self):
        """Monitor file system changes"""
        for file_path in list(self.tracked_files):
            try:
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    self.file_access_log.append({
                        "file": file_path,
                        "mtime": stat.st_mtime,
                        "size": stat.st_size,
                        "timestamp": time.time()
                    })
                else:
                    self.file_access_log.append({
                        "file": file_path,
                        "event": "deleted",
                        "timestamp": time.time()
                    })
                    self.tracked_files.remove(file_path)
                    
            except Exception as e:
                print(f"Error monitoring file {file_path}: {e}")
    
    def track_file(self, file_path: str):
        """Add file to monitoring"""
        self.tracked_files.add(os.path.abspath(file_path))
    
    def untrack_file(self, file_path: str):
        """Remove file from monitoring"""
        self.tracked_files.discard(os.path.abspath(file_path))
    
    def track_directory(self, directory: str, recursive: bool = False):
        """Track all files in a directory"""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return
        
        if recursive:
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    self.track_file(str(file_path))
        else:
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    self.track_file(str(file_path))
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        info = {
            "platform": os.name,
            "python_version": os.sys.version,
            "working_directory": os.getcwd(),
            "environment_variables": len(os.environ),
            "timestamp": time.time()
        }
        
        if PSUTIL_AVAILABLE:
            try:
                info.update({
                    "boot_time": psutil.boot_time(),
                    "cpu_count": psutil.cpu_count(),
                    "total_memory": psutil.virtual_memory().total,
                    "disk_usage": psutil.disk_usage('/').percent
                })
            except:
                pass
        
        return info
    
    def get_process_summary(self) -> Dict[str, Any]:
        """Get summary of process activity"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        
        try:
            top_cpu = sorted(
                self.tracked_processes.values(),
                key=lambda x: x.get('cpu_percent', 0),
                reverse=True
            )[:5]
            
            top_memory = sorted(
                self.tracked_processes.values(),
                key=lambda x: x.get('memory_percent', 0),
                reverse=True
            )[:5]
            
            return {
                "total_processes": len(self.tracked_processes),
                "top_cpu_processes": top_cpu,
                "top_memory_processes": top_memory,
                "recent_events": list(self.process_log)[-10:]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_file_activity(self) -> Dict[str, Any]:
        """Get file system activity summary"""
        return {
            "tracked_files": len(self.tracked_files),
            "recent_file_events": list(self.file_access_log)[-10:],
            "file_list": list(self.tracked_files)
        }
    
    def export_logs(self, filename: str):
        """Export monitoring logs to file"""
        try:
            logs = {
                "system_stats": self.system_stats,
                "process_log": list(self.process_log),
                "file_access_log": list(self.file_access_log),
                "tracked_files": list(self.tracked_files),
                "export_timestamp": time.time()
            }
            
            with open(filename, 'w') as f:
                json.dump(logs, f, indent=2, default=str)
            
            print(f"Logs exported to {filename}")
            
        except Exception as e:
            print(f"Error exporting logs: {e}")
    
    def analyze_usage_patterns(self) -> Dict[str, Any]:
        """Analyze system usage patterns"""
        patterns = {
            "peak_cpu_times": [],
            "peak_memory_times": [],
            "most_active_processes": {},
            "file_access_frequency": {}
        }
        
        process_activity = defaultdict(int)
        for event in self.process_log:
            if event.get("name"):
                process_activity[event["name"]] += 1
        
        patterns["most_active_processes"] = dict(
            sorted(process_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        file_activity = defaultdict(int)
        for event in self.file_access_log:
            if event.get("file"):
                file_activity[event["file"]] += 1
        
        patterns["file_access_frequency"] = dict(
            sorted(file_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return patterns
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        return {
            "monitoring_active": self.monitoring_active,
            "tracked_files": len(self.tracked_files),
            "tracked_processes": len(self.tracked_processes),
            "system_stats_available": bool(self.system_stats),
            "psutil_available": PSUTIL_AVAILABLE,
            "monitoring_interval": self.monitoring_interval,
            "log_entries": {
                "process_log": len(self.process_log),
                "file_access_log": len(self.file_access_log)
            }
        }
