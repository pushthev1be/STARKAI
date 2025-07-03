import serial
import asyncio
from typing import Dict, List, Any, Optional
import json
import time

class HardwareInterface:
    def __init__(self):
        self.connections = {}
        self.device_configs = {}
        
    async def connect_device(self, device_name: str, port: str, baudrate: int = 9600) -> bool:
        """Connect to a serial device (Arduino, ESP32, etc.)"""
        try:
            connection = serial.Serial(port, baudrate, timeout=1)
            self.connections[device_name] = connection
            
            await asyncio.sleep(2)
            
            return True
        except Exception as e:
            print(f"Failed to connect to {device_name}: {e}")
            return False
            
    async def send_command(self, device_name: str, command: Dict[str, Any]) -> Optional[str]:
        """Send command to connected device"""
        if device_name not in self.connections:
            return None
            
        try:
            connection = self.connections[device_name]
            command_str = json.dumps(command) + '\n'
            connection.write(command_str.encode())
            
            await asyncio.sleep(0.1)
            if connection.in_waiting:
                response = connection.readline().decode().strip()
                return response
                
        except Exception as e:
            print(f"Command failed for {device_name}: {e}")
            
        return None
        
    async def read_sensors(self, device_name: str) -> Optional[Dict[str, Any]]:
        """Read sensor data from device"""
        response = await self.send_command(device_name, {"action": "read_sensors"})
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"raw_data": response}
        return None
        
    async def control_actuator(self, device_name: str, actuator: str, value: Any) -> bool:
        """Control an actuator on the device"""
        command = {
            "action": "control",
            "actuator": actuator,
            "value": value
        }
        
        response = await self.send_command(device_name, command)
        return response == "OK"
        
    def disconnect_device(self, device_name: str):
        """Disconnect from a device"""
        if device_name in self.connections:
            self.connections[device_name].close()
            del self.connections[device_name]
