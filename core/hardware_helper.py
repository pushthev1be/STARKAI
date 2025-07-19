"""
Hardware Helper - Interfaces with serial devices (Arduino, ESP, etc.)
Provides unified interface for hardware communication and control
"""

import os
import time
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

class HardwareHelper:
    """Hardware interface for serial devices"""
    
    def __init__(self):
        self.connected_devices = {}
        self.device_configs = {}
        self.auto_reconnect = True
        
    def initialize(self):
        """Initialize hardware interface"""
        print("Initializing Hardware Helper...")
        
        if not SERIAL_AVAILABLE:
            print("⚠ PySerial library not available")
            return
        
        available_ports = self.scan_ports()
        print(f"Found {len(available_ports)} available serial ports")
        
        self._auto_connect_known_devices()
        
        print("✓ Hardware Helper initialized")
    
    def scan_ports(self) -> List[Dict[str, str]]:
        """Scan for available serial ports"""
        if not SERIAL_AVAILABLE:
            return []
        
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                "device": port.device,
                "name": port.name,
                "description": port.description,
                "manufacturer": port.manufacturer or "Unknown",
                "vid": port.vid,
                "pid": port.pid
            })
        
        return ports
    
    def connect_device(self, port: str, baudrate: int = 9600, timeout: float = 1.0) -> bool:
        """Connect to a serial device"""
        if not SERIAL_AVAILABLE:
            print("Serial library not available")
            return False
        
        try:
            device = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout
            )
            
            time.sleep(2)  # Wait for device to initialize
            
            device_id = f"device_{len(self.connected_devices)}"
            self.connected_devices[device_id] = {
                "serial": device,
                "port": port,
                "baudrate": baudrate,
                "connected_at": time.time(),
                "last_activity": time.time()
            }
            
            print(f"Connected to {port} as {device_id}")
            return True
            
        except Exception as e:
            print(f"Failed to connect to {port}: {e}")
            return False
    
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect a device"""
        if device_id not in self.connected_devices:
            return False
        
        try:
            device_info = self.connected_devices[device_id]
            device_info["serial"].close()
            del self.connected_devices[device_id]
            print(f"Disconnected {device_id}")
            return True
        except Exception as e:
            print(f"Error disconnecting {device_id}: {e}")
            return False
    
    def send_command(self, device_id: str, command: str) -> Optional[str]:
        """Send command to device and get response"""
        if device_id not in self.connected_devices:
            return None
        
        try:
            device_info = self.connected_devices[device_id]
            serial_device = device_info["serial"]
            
            command_bytes = (command + '\n').encode('utf-8')
            serial_device.write(command_bytes)
            serial_device.flush()
            
            time.sleep(0.1)
            response = ""
            
            while serial_device.in_waiting > 0:
                response += serial_device.read(serial_device.in_waiting).decode('utf-8')
                time.sleep(0.05)
            
            device_info["last_activity"] = time.time()
            
            return response.strip() if response else "OK"
            
        except Exception as e:
            print(f"Error sending command to {device_id}: {e}")
            return None
    
    def send_raw_data(self, device_id: str, data: bytes) -> bool:
        """Send raw bytes to device"""
        if device_id not in self.connected_devices:
            return False
        
        try:
            device_info = self.connected_devices[device_id]
            serial_device = device_info["serial"]
            
            serial_device.write(data)
            serial_device.flush()
            
            device_info["last_activity"] = time.time()
            return True
            
        except Exception as e:
            print(f"Error sending raw data to {device_id}: {e}")
            return False
    
    def read_data(self, device_id: str, timeout: float = 1.0) -> Optional[str]:
        """Read data from device"""
        if device_id not in self.connected_devices:
            return None
        
        try:
            device_info = self.connected_devices[device_id]
            serial_device = device_info["serial"]
            
            start_time = time.time()
            data = ""
            
            while time.time() - start_time < timeout:
                if serial_device.in_waiting > 0:
                    data += serial_device.read(serial_device.in_waiting).decode('utf-8')
                    time.sleep(0.01)
                else:
                    time.sleep(0.05)
            
            device_info["last_activity"] = time.time()
            return data.strip() if data else None
            
        except Exception as e:
            print(f"Error reading from {device_id}: {e}")
            return None
    
    def list_devices(self) -> List[str]:
        """List all available and connected devices"""
        devices = []
        
        available_ports = self.scan_ports()
        for port in available_ports:
            status = "Connected" if any(
                dev["port"] == port["device"] 
                for dev in self.connected_devices.values()
            ) else "Available"
            
            devices.append(f"{port['device']} - {port['description']} ({status})")
        
        for device_id, info in self.connected_devices.items():
            devices.append(f"{device_id} - {info['port']} (Active)")
        
        return devices
    
    def monitor_devices(self) -> Dict[str, Any]:
        """Monitor all connected devices for activity"""
        status = {}
        
        for device_id, device_info in self.connected_devices.items():
            try:
                serial_device = device_info["serial"]
                
                status[device_id] = {
                    "port": device_info["port"],
                    "connected": serial_device.is_open,
                    "bytes_waiting": serial_device.in_waiting,
                    "last_activity": device_info["last_activity"],
                    "uptime": time.time() - device_info["connected_at"]
                }
                
            except Exception as e:
                status[device_id] = {
                    "error": str(e),
                    "connected": False
                }
        
        return status
    
    def disconnect_all(self):
        """Disconnect all devices"""
        device_ids = list(self.connected_devices.keys())
        for device_id in device_ids:
            self.disconnect_device(device_id)
    
    def _auto_connect_known_devices(self):
        """Auto-connect to known device types"""
        if not SERIAL_AVAILABLE:
            return
        
        known_devices = [
            {"vid": 0x2341, "name": "Arduino"},  # Arduino
            {"vid": 0x10C4, "name": "ESP32"},    # ESP32
            {"vid": 0x1A86, "name": "CH340"},    # CH340 (common on clones)
        ]
        
        available_ports = self.scan_ports()
        
        for port in available_ports:
            for known in known_devices:
                if port["vid"] == known["vid"]:
                    print(f"Found {known['name']} device on {port['device']}")
                    if self.connect_device(port["device"]):
                        break
    
    def create_device_profile(self, device_id: str, profile: Dict[str, Any]):
        """Create a configuration profile for a device"""
        self.device_configs[device_id] = {
            "name": profile.get("name", "Unknown Device"),
            "type": profile.get("type", "generic"),
            "commands": profile.get("commands", {}),
            "baudrate": profile.get("baudrate", 9600),
            "init_sequence": profile.get("init_sequence", []),
            "created_at": time.time()
        }
    
    def execute_device_profile(self, device_id: str, action: str) -> Optional[str]:
        """Execute a predefined action from device profile"""
        if device_id not in self.device_configs:
            return None
        
        profile = self.device_configs[device_id]
        commands = profile.get("commands", {})
        
        if action in commands:
            command = commands[action]
            return self.send_command(device_id, command)
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get hardware interface status"""
        available_ports = self.scan_ports()
        
        return {
            "serial_available": SERIAL_AVAILABLE,
            "connected_devices": len(self.connected_devices),
            "available_ports": available_ports,
            "device_profiles": len(self.device_configs),
            "auto_reconnect": self.auto_reconnect
        }
