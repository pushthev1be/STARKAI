"""
Hardware Helper Module
Interfaces with serial devices (Arduino, ESP32, etc.) and manages hardware projects
"""

import serial
import serial.tools.list_ports
import yaml
import json
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class HardwareHelper:
    """Handles hardware project assistance and serial communication"""
    
    def __init__(self):
        self.active_connections = {}
        self.device_configs = {}
        self.project_descriptors = {}
        
    def list_serial_ports(self) -> List[Dict[str, str]]:
        """List all available serial ports"""
        ports = []
        
        try:
            for port in serial.tools.list_ports.comports():
                port_info = {
                    'device': port.device,
                    'name': port.name,
                    'description': port.description,
                    'hwid': port.hwid,
                    'manufacturer': getattr(port, 'manufacturer', 'Unknown'),
                    'product': getattr(port, 'product', 'Unknown')
                }
                ports.append(port_info)
        except Exception as e:
            ports.append({
                'device': 'error',
                'name': f'Error listing ports: {str(e)}',
                'description': 'Serial port enumeration failed'
            })
        
        return ports
    
    def connect_device(self, port: str, baudrate: int = 9600, timeout: float = 1.0) -> bool:
        """Connect to a serial device"""
        try:
            if port in self.active_connections:
                self.disconnect_device(port)
            
            connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout
            )
            
            self.active_connections[port] = {
                'connection': connection,
                'baudrate': baudrate,
                'connected_at': time.time(),
                'last_activity': time.time()
            }
            
            return True
            
        except Exception as e:
            print(f"Failed to connect to {port}: {str(e)}")
            return False
    
    def disconnect_device(self, port: str) -> bool:
        """Disconnect from a serial device"""
        try:
            if port in self.active_connections:
                connection = self.active_connections[port]['connection']
                if connection.is_open:
                    connection.close()
                del self.active_connections[port]
                return True
            return False
        except Exception as e:
            print(f"Error disconnecting from {port}: {str(e)}")
            return False
    
    def send_command(self, port: str, command: str, wait_response: bool = True) -> Optional[str]:
        """Send command to serial device and optionally wait for response"""
        if port not in self.active_connections:
            return None
        
        try:
            connection = self.active_connections[port]['connection']
            
            command_bytes = (command + '\n').encode('utf-8')
            connection.write(command_bytes)
            connection.flush()
            
            self.active_connections[port]['last_activity'] = time.time()
            
            if wait_response:
                response = connection.readline().decode('utf-8').strip()
                return response
            
            return "Command sent"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def read_data(self, port: str, timeout: float = 1.0) -> Optional[str]:
        """Read data from serial device"""
        if port not in self.active_connections:
            return None
        
        try:
            connection = self.active_connections[port]['connection']
            connection.timeout = timeout
            
            data = connection.readline().decode('utf-8').strip()
            
            if data:
                self.active_connections[port]['last_activity'] = time.time()
                return data
            
            return None
            
        except Exception as e:
            return f"Error reading: {str(e)}"
    
    def load_project_descriptor(self, yaml_path: str) -> Dict[str, Any]:
        """Load hardware project descriptor from YAML file"""
        try:
            with open(yaml_path, 'r') as f:
                descriptor = yaml.safe_load(f)
            
            required_fields = ['name', 'type', 'components']
            for field in required_fields:
                if field not in descriptor:
                    raise ValueError(f"Missing required field: {field}")
            
            self.project_descriptors[descriptor['name']] = descriptor
            return descriptor
            
        except Exception as e:
            return {'error': f"Failed to load descriptor: {str(e)}"}
    
    def create_project_template(self, project_name: str, project_type: str) -> Dict[str, Any]:
        """Create a hardware project template"""
        templates = {
            'arduino': {
                'name': project_name,
                'type': 'arduino',
                'platform': 'Arduino Uno',
                'components': [
                    {'name': 'LED', 'pin': 13, 'type': 'output'},
                    {'name': 'Button', 'pin': 2, 'type': 'input'}
                ],
                'libraries': ['Arduino.h'],
                'serial_config': {
                    'baudrate': 9600,
                    'timeout': 1.0
                },
                'code_template': '''
void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  pinMode(2, INPUT);
}

void loop() {
  if (digitalRead(2) == HIGH) {
    digitalWrite(13, HIGH);
    Serial.println("Button pressed - LED ON");
  } else {
    digitalWrite(13, LOW);
    Serial.println("Button released - LED OFF");
  }
  delay(100);
}
'''
            },
            'esp32': {
                'name': project_name,
                'type': 'esp32',
                'platform': 'ESP32 DevKit',
                'components': [
                    {'name': 'Built-in LED', 'pin': 2, 'type': 'output'},
                    {'name': 'WiFi', 'type': 'communication'}
                ],
                'libraries': ['WiFi.h', 'WebServer.h'],
                'serial_config': {
                    'baudrate': 115200,
                    'timeout': 2.0
                },
                'code_template': '''

const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";

void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi connected!");
}

void loop() {
  digitalWrite(2, HIGH);
  delay(1000);
  digitalWrite(2, LOW);
  delay(1000);
}
'''
            },
            'raspberry_pi': {
                'name': project_name,
                'type': 'raspberry_pi',
                'platform': 'Raspberry Pi 4',
                'components': [
                    {'name': 'GPIO LED', 'pin': 18, 'type': 'output'},
                    {'name': 'GPIO Button', 'pin': 24, 'type': 'input'}
                ],
                'libraries': ['RPi.GPIO', 'time'],
                'serial_config': {
                    'baudrate': 9600,
                    'timeout': 1.0
                },
                'code_template': '''
import RPi.GPIO as GPIO
import time

LED_PIN = 18
BUTTON_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("Button pressed - LED ON")
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            print("Button released - LED OFF")
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
'''
            }
        }
        
        return templates.get(project_type, {'error': f'Unknown project type: {project_type}'})
    
    def analyze_hardware_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze hardware project structure and provide insights"""
        analysis = {
            'project_path': project_path,
            'files_found': [],
            'project_type': 'unknown',
            'issues': [],
            'recommendations': []
        }
        
        try:
            project_path_obj = Path(project_path)
            
            if not project_path_obj.exists():
                analysis['issues'].append('Project path does not exist')
                return analysis
            
            for file_path in project_path_obj.rglob('*'):
                if file_path.is_file():
                    analysis['files_found'].append(str(file_path))
            
            arduino_files = [f for f in analysis['files_found'] if f.endswith('.ino')]
            python_files = [f for f in analysis['files_found'] if f.endswith('.py')]
            cpp_files = [f for f in analysis['files_found'] if f.endswith(('.cpp', '.c', '.h'))]
            
            if arduino_files:
                analysis['project_type'] = 'arduino'
                analysis['main_files'] = arduino_files
            elif python_files and any('gpio' in f.lower() or 'rpi' in f.lower() for f in python_files):
                analysis['project_type'] = 'raspberry_pi'
                analysis['main_files'] = python_files
            elif cpp_files:
                analysis['project_type'] = 'embedded_cpp'
                analysis['main_files'] = cpp_files
            
            if not analysis['main_files']:
                analysis['issues'].append('No main code files found')
            
            if analysis['project_type'] == 'arduino':
                analysis['recommendations'].extend([
                    'Ensure Arduino IDE is installed',
                    'Check board and port settings',
                    'Verify library dependencies'
                ])
            elif analysis['project_type'] == 'raspberry_pi':
                analysis['recommendations'].extend([
                    'Install required Python libraries (RPi.GPIO, etc.)',
                    'Check GPIO pin assignments',
                    'Ensure proper permissions for GPIO access'
                ])
            
        except Exception as e:
            analysis['issues'].append(f'Analysis error: {str(e)}')
        
        return analysis
    
    def get_device_status(self) -> Dict[str, Any]:
        """Get status of all connected devices"""
        status = {
            'connected_devices': len(self.active_connections),
            'devices': {}
        }
        
        for port, info in self.active_connections.items():
            connection = info['connection']
            status['devices'][port] = {
                'is_open': connection.is_open,
                'baudrate': info['baudrate'],
                'connected_duration': time.time() - info['connected_at'],
                'last_activity': time.time() - info['last_activity']
            }
        
        return status
    
    def auto_detect_devices(self) -> List[Dict[str, Any]]:
        """Auto-detect and identify connected hardware devices"""
        detected_devices = []
        ports = self.list_serial_ports()
        
        for port_info in ports:
            device_type = 'unknown'
            confidence = 0
            
            description = port_info.get('description', '').lower()
            manufacturer = port_info.get('manufacturer', '').lower()
            
            if 'arduino' in description or 'arduino' in manufacturer:
                device_type = 'arduino'
                confidence = 0.9
            elif 'esp32' in description or 'espressif' in manufacturer:
                device_type = 'esp32'
                confidence = 0.9
            elif 'ch340' in description or 'cp210' in description:
                device_type = 'generic_microcontroller'
                confidence = 0.7
            elif 'ftdi' in description or 'ftdi' in manufacturer:
                device_type = 'ftdi_device'
                confidence = 0.8
            
            detected_devices.append({
                'port': port_info['device'],
                'type': device_type,
                'confidence': confidence,
                'info': port_info
            })
        
        return detected_devices
    
    def generate_code_suggestions(self, project_type: str, components: List[Dict]) -> List[str]:
        """Generate code suggestions based on project components"""
        suggestions = []
        
        if project_type == 'arduino':
            suggestions.extend([
                "Use pinMode() to configure pin modes in setup()",
                "Add Serial.begin() for debugging output",
                "Consider using pull-up resistors for buttons",
                "Add delay() to prevent excessive loop execution"
            ])
            
            for component in components:
                if component.get('type') == 'sensor':
                    suggestions.append(f"Add calibration routine for {component.get('name')} sensor")
                elif component.get('type') == 'motor':
                    suggestions.append(f"Implement PWM control for {component.get('name')} motor")
        
        elif project_type == 'esp32':
            suggestions.extend([
                "Initialize WiFi connection in setup()",
                "Use FreeRTOS tasks for concurrent operations",
                "Implement deep sleep for power saving",
                "Add OTA update capability"
            ])
        
        return suggestions
