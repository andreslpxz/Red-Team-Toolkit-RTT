import json
import re
from core.groq_client import groq_client
from utils.logger import Logger

RE_ACT_PROMPT = """
You are an autonomous Red Team AI Agent. Your goal is to achieve the objective using a "Thought-Action-Observation" loop.

Available Actions:
- nmap_scan[target]: Runs an Nmap scan on the target.
- analyze_vulns[output]: Analyzes Nmap output for vulnerabilities using AI.
- search_exploit[service]: Searches for known exploits for a given service.
- finalize[result]: Ends the loop and provides the final summary of findings.

Loop Format:
Thought: Your reasoning about the current state and what to do next.
Action: action_name[parameter]
Observation: The result of the action (this will be provided to you).

IMPORTANT: You must follow the format exactly. Only one action per turn.

Objective: {objective}
"""

class Agent:
    """
    Orchestrates the autonomous reasoning loop using the ReAct pattern.
    It manages state, interacts with the Groq LLM, and dispatches actions to modules.
    """
    def __init__(self):
        self.max_iterations = 5

    def run(self, objective):
        """
        Starts the execution loop for a given security objective.
        """
        Logger.info(f"Initiating autonomous agent for: {objective}")
        current_context = RE_ACT_PROMPT.format(objective=objective)

        for i in range(self.max_iterations):
            Logger.info(f"Iteration {i+1}/{self.max_iterations}")

            response = groq_client.chat(current_context)
            if "Error:" in response:
                Logger.error(f"Agent encountered a communication error: {response}")
                break

            # Robust parsing using Regex
            thought_match = re.search(r"Thought:\s*(.*)", response, re.IGNORECASE)
            action_match = re.search(r"Action:\s*(\w+)\[(.*?)\]", response, re.IGNORECASE)

            if thought_match:
                Logger.info(f"Agent Thought: {thought_match.group(1).strip()}")

            if not action_match:
                Logger.warning("No clear action identified by the agent. Response follows:")
                print(response)
                break

            action_name = action_match.group(1).lower()
            action_param = action_match.group(2).strip()

            if action_name == "finalize":
                Logger.success("Objective Finalized:")
                print(action_param)
                break

            Logger.info(f"Executing Action: {action_name}({action_param})")
            observation = self._dispatch_action(action_name, action_param)

            # Update context for next iteration
            current_context += f"\n{response}\nObservation: {observation}"

    def _dispatch_action(self, name, param):
        """
        Routes the action name to the corresponding module implementation.
        """
        try:
            if name == "nmap_scan":
                from modules.recon import recon_module
                return recon_module.scan(param)
            elif name == "analyze_vulns":
                from modules.recon import recon_module
                return recon_module.analyze(param)
            elif name == "search_exploit":
                from modules.exploit import exploit_module
                return exploit_module.search(param)
            else:
                return f"Error: Action '{name}' is not recognized by the system."
        except Exception as e:
            Logger.error(f"Execution Error in {name}: {str(e)}")
            return f"Action failed: {str(e)}"

agent = Agent()
