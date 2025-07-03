import psutil
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Dict, List, Any, Callable, Optional
import os
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.observers = []
        self.callbacks = []
        self.system_state = {}
        self.monitoring = False
        
    async def start_monitoring(self, paths: Optional[List[str]] = None):
        """Start monitoring system and file changes"""
        if paths is None:
            paths = [os.getcwd()]
            
        self.monitoring = True
        
        for path in paths:
            if os.path.exists(path):
                observer = Observer()
                observer.schedule(FileChangeHandler(self), path, recursive=True)
                observer.start()
                self.observers.append(observer)
                
        asyncio.create_task(self._monitor_system_resources())
        
    async def _monitor_system_resources(self):
        """Monitor CPU, memory, and process usage"""
        while self.monitoring:
            try:
                self.system_state = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory": psutil.virtual_memory()._asdict(),
                    "disk": psutil.disk_usage('/')._asdict(),
                    "processes": self._get_top_processes(),
                    "network": psutil.net_io_counters()._asdict()
                }
                
                await self._check_system_anomalies()
                
            except Exception as e:
                print(f"System monitoring error: {e}")
                
            await asyncio.sleep(30)
            
    def _get_top_processes(self) -> List[Dict[str, Any]]:
        """Get top CPU/memory consuming processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
        
    async def _check_system_anomalies(self):
        """Check for system performance anomalies"""
        if self.system_state['cpu_percent'] > 80:
            await self._trigger_callback('high_cpu', self.system_state)
        if self.system_state['memory']['percent'] > 85:
            await self._trigger_callback('high_memory', self.system_state)
            
    async def _trigger_callback(self, event_type: str, data: Dict[str, Any]):
        """Trigger registered callbacks for system events"""
        for callback in self.callbacks:
            try:
                await callback(event_type, data)
            except Exception as e:
                print(f"Callback error: {e}")
                
    def register_callback(self, callback: Callable):
        """Register callback for system events"""
        self.callbacks.append(callback)
        
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, monitor):
        self.monitor = monitor
        
    def on_modified(self, event):
        if not event.is_directory:
            asyncio.create_task(
                self.monitor._trigger_callback('file_modified', {
                    'path': event.src_path,
                    'timestamp': datetime.now().isoformat()
                })
            )
