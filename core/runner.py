import subprocess
import shutil
import os
import signal
import time
import threading
from typing import Optional, Callable
import logging

class V2RayRunner:
    def __init__(self, v2ray_path: str, config_path: str):
        self.v2ray_path = v2ray_path
        self.config_path = config_path
        self.process: Optional[subprocess.Popen] = None
        self.logger = logging.getLogger(__name__)
        self._stop_event = threading.Event()
        self._output_thread: Optional[threading.Thread] = None

    def _find_v2ray_binary(self) -> str:
        """Find v2ray binary in common locations"""
        # Check if path is absolute and exists
        if os.path.isabs(self.v2ray_path) and os.path.isfile(self.v2ray_path):
            return self.v2ray_path
        
        # Check current directory
        current_dir = os.path.join(os.getcwd(), self.v2ray_path)
        if os.path.isfile(current_dir):
            return current_dir
        
        # Check bin directory
        bin_dir = os.path.join(os.getcwd(), "bin", self.v2ray_path)
        if os.path.isfile(bin_dir):
            return bin_dir
        
        # Check if v2ray is in PATH
        v2ray_in_path = shutil.which("v2ray")
        if v2ray_in_path:
            return v2ray_in_path
        
        raise FileNotFoundError(f"v2ray binary not found. Tried: {self.v2ray_path}, {current_dir}, {bin_dir}")

    def _output_monitor(self):
        """Monitor v2ray output in background thread"""
        if not self.process:
            return
        
        try:
            while not self._stop_event.is_set() and self.process.poll() is None:
                # Read stdout
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        print(f"[V2Ray] {line.strip()}")
                
                # Read stderr
                if self.process.stderr:
                    line = self.process.stderr.readline()
                    if line:
                        print(f"[V2Ray Error] {line.strip()}")
                
                time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Output monitor error: {e}")

    def start(self) -> subprocess.Popen:
        """Start v2ray process"""
        if self.process and self.process.poll() is None:
            raise RuntimeError("V2Ray already running")
        
        # Find v2ray binary
        v2ray_binary = self._find_v2ray_binary()
        
        # Check config file
        if not os.path.isfile(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        # Start v2ray process
        try:
            self.process = subprocess.Popen([
                v2ray_binary, "run", "-c", self.config_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
               text=True, bufsize=1, universal_newlines=True)
            
            # Start output monitoring
            self._stop_event.clear()
            self._output_thread = threading.Thread(target=self._output_monitor, daemon=True)
            self._output_thread.start()
            
            # Wait a bit to see if it starts successfully
            time.sleep(1)
            if self.process.poll() is not None:
                # Process failed to start
                stdout, stderr = self.process.communicate()
                raise RuntimeError(f"V2Ray failed to start. Exit code: {self.process.returncode}\n"
                                f"Stdout: {stdout}\nStderr: {stderr}")
            
            self.logger.info(f"V2Ray started with PID {self.process.pid}")
            return self.process
            
        except Exception as e:
            if self.process:
                self.process.kill()
                self.process = None
            raise RuntimeError(f"Failed to start V2Ray: {e}")

    def stop(self, timeout: int = 10):
        """Stop v2ray process gracefully"""
        if not self.process:
            return
        
        self.logger.info("Stopping V2Ray...")
        self._stop_event.set()
        
        try:
            # Try graceful shutdown first
            self.process.send_signal(signal.SIGTERM)
            self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.logger.warning("V2Ray didn't stop gracefully, forcing kill")
            self.process.kill()
            self.process.wait()
        except Exception as e:
            self.logger.error(f"Error stopping V2ray: {e}")
            if self.process.poll() is None:
                self.process.kill()
        finally:
            self.process = None
            if self._output_thread and self._output_thread.is_alive():
                self._output_thread.join(timeout=1)

    def restart(self):
        """Restart v2ray process"""
        self.logger.info("Restarting V2Ray...")
        self.stop()
        time.sleep(1)  # Wait a bit before restarting
        return self.start()

    def is_running(self) -> bool:
        """Check if v2ray is running"""
        return bool(self.process and self.process.poll() is None)

    def get_status(self) -> dict:
        """Get current status"""
        if not self.process:
            return {"status": "not_started"}
        
        if self.process.poll() is None:
            return {"status": "running", "pid": self.process.pid}
        else:
            return {"status": "stopped", "exit_code": self.process.returncode}
    
    def test_connection(self, timeout: int = 10) -> dict:
        """Test if the proxy connection is working"""
        import socket
        
        if not self.is_running():
            return {"status": "error", "message": "V2Ray not running"}
        
        try:
            # Test SOCKS proxy connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect(("127.0.0.1", 1080))
            sock.close()
            
            return {"status": "success", "message": "SOCKS proxy is accessible"}
        except Exception as e:
            return {"status": "error", "message": f"Connection test failed: {e}"}

    def wait_for_exit(self, timeout: Optional[int] = None):
        """Wait for v2ray process to exit"""
        if not self.process:
            return
        
        try:
            self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            pass

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()