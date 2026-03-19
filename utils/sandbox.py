import os
import subprocess
import asyncio
import shlex
from typing import Dict, Any, List, Optional
from utils.logger import Logger
import datetime

class SafeExecutor:
    """
    Handles safe execution of scripts within the /space sandbox.
    Enforces directory limits, timeouts, and restricted commands.
    """
    def __init__(self, base_path: str = "space"):
        self.base_path = os.path.abspath(base_path)
        self.allowed_commands = {
            "python": "/usr/bin/python3",
            "python3": "/usr/bin/python3",
            "bash": "/bin/bash",
            "sh": "/bin/sh",
        }
        self.max_timeout = 30  # seconds
        self.audit_log_path = os.path.join(self.base_path, "audit.log")

    def _log_audit(self, command: str, status: str, output: str = ""):
        """
        Logs every execution for audit purposes.
        """
        timestamp = datetime.datetime.now().isoformat()
        try:
            with open(self.audit_log_path, "a") as f:
                f.write(f"[{timestamp}] STATUS: {status} | COMMAND: {command} | OUTPUT_LEN: {len(output)}\n")
        except Exception as e:
            Logger.error(f"Failed to write audit log: {e}")

    def validate_path(self, path: str) -> str:
        """
        Validates that a path is within the sandbox base_path.
        Prevents path traversal.
        """
        abs_path = os.path.abspath(os.path.join(self.base_path, path))
        if not abs_path.startswith(self.base_path):
            raise PermissionError(f"Access denied: Path {path} is outside of the sandbox.")
        return abs_path

    async def execute(self, command: str, script_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Safely executes a command or script in the sandbox.
        """
        try:
            # Command parsing and validation
            parts = shlex.split(command)
            if not parts:
                return {"error": "Empty command", "status": "failed"}

            executable = parts[0]
            if executable not in self.allowed_commands:
                self._log_audit(command, "blocked")
                return {"error": f"Command '{executable}' not allowed in sandbox.", "status": "blocked"}

            # If script_path is provided, validate it
            if script_path:
                validated_script = self.validate_path(script_path)
                if not os.path.exists(validated_script):
                    return {"error": f"Script {script_path} not found.", "status": "failed"}
                # Replace script path in command if necessary or append it
                # For simplicity, if script_path is given, we assume the command structure
                # like ['python3', 'script.py']

            # Use full path to executable for safety
            parts[0] = self.allowed_commands[executable]

            Logger.info(f"Sandbox executing: {' '.join(parts)}")

            # Start process with timeout
            process = await asyncio.create_subprocess_exec(
                *parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.base_path  # Always execute from /space
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.max_timeout)
                output = stdout.decode().strip()
                errors = stderr.decode().strip()

                status = "success" if process.returncode == 0 else "failed"
                self._log_audit(command, status, output + errors)

                return {
                    "output": output,
                    "errors": errors,
                    "exit_code": process.returncode,
                    "status": status
                }
            except asyncio.TimeoutError:
                process.kill()
                self._log_audit(command, "timeout")
                return {"error": "Execution timed out (30s limit)", "status": "timeout"}

        except Exception as e:
            Logger.error(f"Sandbox error: {e}")
            self._log_audit(command, "error", str(e))
            return {"error": str(e), "status": "error"}

# Global instance
safe_executor = SafeExecutor()
