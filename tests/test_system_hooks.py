import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.system_hooks import SystemMonitor

class TestSystemMonitor:
    def setup_method(self):
        self.monitor = SystemMonitor()
        
    @patch('core.system_hooks.psutil.cpu_percent')
    @patch('core.system_hooks.psutil.virtual_memory')
    async def test_system_monitoring(self, mock_memory, mock_cpu):
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock()
        mock_memory.return_value._asdict.return_value = {"percent": 60.0}
        
        self.monitor.monitoring = True
        await self.monitor._monitor_system_resources()
        
        assert "cpu_percent" in self.monitor.system_state
        assert "memory" in self.monitor.system_state
        
    async def test_callback_registration(self):
        callback = Mock()
        self.monitor.register_callback(callback)
        
        assert callback in self.monitor.callbacks
        
    async def test_high_cpu_anomaly_detection(self):
        callback = Mock()
        self.monitor.register_callback(callback)
        self.monitor.system_state = {"cpu_percent": 85.0}
        
        await self.monitor._check_system_anomalies()
        
        callback.assert_called_once()
