import serial
import time

class SerialClient:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            print(f"Serial connection established on {port}")
        except serial.SerialException as e:
            print(f"Failed to open serial port {port}: {e}")

    def sendData(self, data):
        if self.ser is None or not self.ser.is_open:
            print("Serial port not open")
            return
            
        try:
            # Convert integer to string, add newline and encode to bytes
            if isinstance(data, int):
                data_bytes = f"{data}\n".encode()
            elif isinstance(data, str):
                data_bytes = f"{data}\n".encode()
            else:
                data_bytes = f"{str(data)}\n".encode()
                
            self.ser.write(data_bytes)
            print(f"Data sent: {data}")
            self.ser.flush()
        except serial.SerialException as e:
            print(f"Serial error: {e}")
    
    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial connection closed")