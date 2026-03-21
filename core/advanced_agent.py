import json
import re
import asyncio
import os
from core.agent import Agent, RE_ACT_PROMPT
from core.semantic_memory import semantic_memory
from core.mcp_router import mcp_router
from core.file_executor import file_executor
from core.groq_client import groq_client
from utils.logger import Logger
from utils.config import config
from typing import Dict, Any, List, Optional

ADVANCED_RE_ACT_PROMPT = """
You are an ADVANCED autonomous Red Team AI Agent. Your goal is to achieve the objective using a "Thought-Action-Observation" loop.

Available Actions:
- nmap_scan[target, options]: Runs an Nmap scan. Options are optional (e.g., -Pn, -sV, -p80).
- analyze_vulns[output]: Analyzes Nmap output for vulnerabilities using AI.
- search_exploit[service]: Searches for known exploits for a given service.
- semantic_search[query]: Searches past experiences in semantic memory.
- mcp_query[query]: Queries external APIs (NVD, GitHub, MITRE) for context.
- create_payload[payload_type, target_ip, target_port]: Generates an obfuscated payload (types: reverse_shell, bind_shell, data_exfil, dropper, persistence).
- execute_script[script_path]: Executes a python script safely in the /space sandbox.
- run_command[command]: Runs a shell command (curl, wget, ping, etc.) in the /space sandbox.
- write_file[filename, content]: Writes content to a file in the /space sandbox.
- install_tool[tool_name, type]: Installs a tool using 'pkg' or 'pip' (e.g., install_tool[sqlmap, pkg]).
- finalize[result]: Ends the loop and provides the final summary of findings.

Loop Format:
Thought: Your reasoning about the current state, what you've learned from memory or MCP, and what to do next.
Action: action_name[parameter1, parameter2, ...]
Observation: The result of the action (this will be provided to you).

IMPORTANT: You must follow the format exactly. Only one action per turn.
Be PERSISTENT. If a scan fails, try different options or tools. If a host is down, try to verify with ping or curl.
Use multiple tools (nmap, curl, etc.) to gather comprehensive information.
If you encounter a web service, try to explore it using curl or by writing custom python scripts for directory brute-forcing or vulnerability testing.
Always check semantic_search or mcp_query when you encounter a new service or potential vulnerability to gather more context.
Don't give up easily; if one approach fails, reflect on the reason and try a different one.

Objective: {objective}
"""

class AdvancedAgent(Agent):
    """
    Enhanced autonomous agent with Semantic Memory, MCP Router, and File Executor.
    """
    def __init__(self):
        super().__init__()
        self.max_iterations = 15  # Increased for better autonomy
        self.current_mission_data = []

    async def execute_mission(self, objective: str):
        """
        Starts the advanced execution loop for a security objective.
        """
        Logger.info(f"Initiating ADVANCED autonomous agent for: {objective}")
        current_context = ADVANCED_RE_ACT_PROMPT.format(objective=objective)
        self.current_mission_data = []

        for i in range(self.max_iterations):
            Logger.info(f"Iteration {i+1}/{self.max_iterations}")

            # Get thought and action from LLM
            response = groq_client.chat(current_context)
            if "Error:" in response:
                Logger.error(f"Agent communication error: {response}")
                break

            # Robust parsing using Regex
            thought_match = re.search(r"Thought:\s*(.*)", response, re.IGNORECASE)
            action_match = re.search(r"Action:\s*(\w+)\[(.*?)\]", response, re.IGNORECASE)

            if thought_match:
                Logger.info(f"Agent Thought: {thought_match.group(1).strip()}")

            if not action_match:
                Logger.warning("No clear action identified. Response follows:")
                print(response)
                # Try to finalize if the agent is stuck or providing a long summary
                if "finalize" in response.lower():
                    Logger.success("Agent seems to be trying to finalize without proper format.")
                break

            action_name = action_match.group(1).lower()
            action_params_raw = action_match.group(2).strip()
            # Split parameters by comma, handling potential spaces
            action_params = [p.strip() for p in action_params_raw.split(',')]

            if action_name == "finalize":
                Logger.success("Mission Finalized:")
                print(action_params_raw)
                # Store the final result in semantic memory
                await semantic_memory.store("mission_final", objective, {"result": action_params_raw})
                # Auto-generate report if configured (default to True for AdvancedAgent)
                report_path = await file_executor.generate_report(self.current_mission_data, target=objective[:20])
                Logger.success(f"Final report generated at: {report_path}")
                break

            Logger.info(f"Executing Action: {action_name}({', '.join(action_params)})")
            observation = await self._dispatch_action_async(action_name, action_params)

            # Store iteration results for reporting
            self.current_mission_data.append({
                "iteration": i + 1,
                "thought": thought_match.group(1).strip() if thought_match else "",
                "action": action_name,
                "params": action_params,
                "observation": str(observation)[:500] + "..." if len(str(observation)) > 500 else str(observation)
            })

            # Update context for next iteration
            current_context += f"\n{response}\nObservation: {observation}"

    async def _dispatch_action_async(self, name: str, params: List[str]):
        """
        Async routing of agent actions to specialized modules.
        """
        try:
            if name == "nmap_scan":
                from modules.recon import recon_module
                target = params[0]
                options = params[1] if len(params) > 1 else "-F -sV"
                return recon_module.scan(target, options=options)
            elif name == "analyze_vulns":
                from modules.recon import recon_module
                return recon_module.analyze(params[0])
            elif name == "search_exploit":
                from modules.exploit import exploit_module
                return exploit_module.search(params[0])
            elif name == "semantic_search":
                results = await semantic_memory.search(params[0])
                return json.dumps(results) if results else "No similar patterns found in memory."
            elif name == "mcp_query":
                results = await mcp_router.query(params[0])
                return json.dumps(results)
            elif name == "create_payload":
                if len(params) < 3:
                    return "Error: create_payload requires [type, target_ip, target_port]"
                payload_info = {"target_ip": params[1], "target_port": params[2]}
                path = await file_executor.create_payload(payload_info, payload_type=params[0])
                return f"Payload generated at: {path}"
            elif name == "execute_script":
                result = await file_executor.execute_script(params[0])
                return json.dumps(result)
            elif name == "run_command":
                from utils.sandbox import safe_executor
                cmd = params[0]
                # Map allowed commands for run_command
                allowed = ["curl", "wget", "ping", "dig", "nslookup", "whois", "nc", "netcat"]
                executable = cmd.split()[0]
                if executable in allowed:
                    # Check if the tool is installed and where
                    import shutil
                    exec_path = shutil.which(executable)
                    if not exec_path:
                        return f"Error: Command '{executable}' not found in the system. Try install_tool first."

                    # Temporarily allow this in safe_executor for this action
                    original_allowed = safe_executor.allowed_commands.copy()
                    safe_executor.allowed_commands[executable] = exec_path

                    result = await safe_executor.execute(cmd)
                    safe_executor.allowed_commands = original_allowed
                    return json.dumps(result)
                else:
                    return f"Error: Command '{executable}' not allowed via run_command."
            elif name == "write_file":
                from utils.sandbox import safe_executor
                filename = params[0]
                content = params[1] if len(params) > 1 else ""
                try:
                    path = safe_executor.validate_path(filename)
                    def _write():
                        with open(path, "w") as f:
                            f.write(content)
                    await asyncio.to_thread(_write)
                    return f"File written to {filename}"
                except PermissionError as e:
                    return str(e)
            elif name == "install_tool":
                tool = params[0]
                install_type = params[1].lower() if len(params) > 1 else "pkg"
                if install_type == "pkg":
                    cmd = f"pkg install -y {tool}"
                elif install_type == "pip":
                    cmd = f"pip install {tool}"
                else:
                    return f"Error: Unknown install type '{install_type}'"

                # We run this outside sandbox as it needs system access
                import subprocess
                process = subprocess.run(cmd.split(), capture_output=True, text=True)
                return f"Installation result: {process.stdout} {process.stderr}"

            else:
                return f"Error: Action '{name}' is not recognized."
        except Exception as e:
            Logger.error(f"Execution Error in {name}: {str(e)}")
            return f"Action failed: {str(e)}"

# Global instance
advanced_agent = AdvancedAgent()
