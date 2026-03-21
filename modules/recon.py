import subprocess
import threading
from utils.logger import Logger
from core.groq_client import groq_client

class ReconModule:
    def __init__(self):
        self.name = "recon"
        self._last_result = None

    def scan(self, target, options="-F -sV", callback=None):
        """
        Runs an Nmap scan with custom options. If a callback is provided, it runs in a background thread.
        """
        def _run():
            Logger.info(f"Running Nmap scan on {target} with options: {options}...")
            try:
                # Build command list
                cmd = ["nmap"] + options.split() + [target]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                output = result.stdout if result.returncode == 0 else f"Nmap Error: {result.stderr}"
                self._last_result = output
                if callback:
                    callback(output)
                return output
            except Exception as e:
                err = f"Execution Error: {str(e)}"
                if callback:
                    callback(err)
                return err

        if callback:
            thread = threading.Thread(target=_run)
            thread.start()
            return "Scan started in background..."
        else:
            return _run()

    def analyze(self, nmap_output):
        Logger.info("Analyzing Nmap output with Groq...")
        prompt = f"Identify critical vulnerabilities and exploit vectors in this Nmap output:\n\n{nmap_output}"
        return groq_client.chat(prompt)

recon_module = ReconModule()
