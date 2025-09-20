from typing import Any, Dict
from bigfix_universal_remote_qna.models.connection_profile import ConnectionProfile
import paramiko  

from bigfix_universal_remote_qna.models.os_type import OSType

class SSHManager:
    """Handles SSH connections and command execution"""
    
    def __init__(self):
        self.client = None
        self.connected = False
    
    def connect(self, profile: ConnectionProfile) -> bool:
        """Establish SSH connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.client.connect(
                hostname=profile.host,
                port=profile.port,
                username=profile.username,
                password=profile.password,
                timeout=30
            )
            
            self.connected = True
            return True
            
        except Exception as e:
            self.connected = False
            raise ConnectionError(f"Failed to connect: {str(e)}")
    
    def disconnect(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            self.client = None
        self.connected = False
    
    def execute_command(self, command: str, timeout: int = 60) -> Dict[str, Any]:
        """Execute command on remote machine"""
        if not self.connected or not self.client:
            raise RuntimeError("Not connected to remote machine")
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            
            output = stdout.read().decode()
            error = stderr.read().decode()
            exit_code = stdout.channel.recv_exit_status()
            
            return {
                'output': output,
                'error': error,
                'exit_code': exit_code,
                'success': exit_code == 0
            }
            
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {str(e)}")
    
    def test_file_exists(self, file_path: str, os_type: str) -> bool:
        """Test if file exists on remote machine"""
        if os_type == OSType.WINDOWS.value:
            test_cmd = f'if exist "{file_path}" echo EXISTS'
        else:
            test_cmd = f'test -f "{file_path}" && echo EXISTS'
        
        result = self.execute_command(test_cmd)
        return "EXISTS" in result['output']