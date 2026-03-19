import sys
import os
import threading
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from utils.logger import Logger
from utils.config import config
from utils.panic import trigger_panic
from modules.recon import recon_module
from modules.exploit import exploit_module
from modules.stealth import stealth_module
from core.agent import agent
from core.memory import memory

# NEW IMPORTS
from core.advanced_agent import advanced_agent
from core.semantic_memory import semantic_memory
from core.mcp_router import mcp_router
from core.file_executor import file_executor

def print_banner():
    banner = """
    \033[36m
     █████╗ ██╗   ██╗██████╗  █████╗
    ██╔══██╗██║   ██║██╔══██╗██╔══██╗
    ███████║██║   ██║██████╔╝███████║
    ██╔══██║██║   ██║██╔══██╗██╔══██║
    ██║  ██║╚██████╔╝██║  ██║██║  ██║
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
    \033[37m[ Aura-Framework v2.0 - ADVANCED ]\033[0m
    \033[91m[!] AUTHORIZED PENETRATION TESTING ONLY\033[0m
    """
    print(banner)

def handle_background_scan(output, target):
    Logger.success(f"Background scan for {target} finished.")
    memory.store(target, "nmap_scan", output)
    # Automatically trigger AI analysis
    analysis = recon_module.analyze(output)
    Logger.success(f"AI Analysis for {target}:")
    print(analysis)
    memory.store(target, "ai_analysis", analysis)

def run_async(coro):
    """
    Helper function to run async coroutines from the synchronous CLI loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def main():
    print_banner()

    if not config.is_valid():
        Logger.warning("GROQ_API_KEY not set. Please update .env")

    commands = [
        'scan', 'agent', 'agent-semantic', 'exploit', 'stealth', 'memory',
        'memory-search', 'mcp', 'report', 'payload', 'panic', 'help', 'exit', 'clear'
    ]
    completer = WordCompleter(commands, ignore_case=True)
    session = PromptSession(completer=completer)

    while True:
        try:
            text = session.prompt("aura > ")
            if not text:
                continue

            parts = text.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == 'exit':
                break
            elif cmd == 'clear':
                os.system('clear')
            elif cmd == 'panic':
                trigger_panic()
            elif cmd == 'help':
                print("""
                Aura Framework Commands:
                  agent <objective>           : Start autonomous AI mission (Standard)
                  agent-semantic <objective>  : Advanced mission with Semantic Memory & MCP
                  scan <target>              : Run background Nmap & AI analysis
                  exploit <info>             : AI-assisted exploit search/payload
                  mcp query <query>          : Query context from NVD, GitHub, MITRE
                  memory <target>            : Show stored findings for target (SQL)
                  memory-search <pattern>    : Semantic search in past vulnerabilities
                  report <target>            : Generate HTML/JSON report from findings
                  payload <type> <ip> <port> : Generate obfuscated payload
                  stealth                    : Operational security tools
                  panic                      : Wipes keys and logs immediately
                  clear/exit                 : System commands
                """)
            elif cmd == 'scan':
                if not args:
                    Logger.error("Usage: scan <target>")
                    continue
                target = args[0]
                recon_module.scan(target, callback=lambda out: handle_background_scan(out, target))
            elif cmd == 'agent':
                if not args:
                    Logger.error("Usage: agent <objective>")
                    continue
                threading.Thread(target=agent.run, args=(" ".join(args),)).start()
            elif cmd == 'agent-semantic':
                if not args:
                    Logger.error("Usage: agent-semantic <objective>")
                    continue
                # For simplicity, running advanced agent in current thread but it's async
                run_async(advanced_agent.execute_mission(" ".join(args)))
            elif cmd == 'memory':
                if not args:
                    Logger.error("Usage: memory <target>")
                    continue
                results = memory.query(args[0])
                for r_type, data, ts in results:
                    print(f"[{ts}] {r_type}: {data[:100]}...")
            elif cmd == 'memory-search':
                if not args:
                    Logger.error("Usage: memory-search <pattern>")
                    continue
                results = run_async(semantic_memory.search(" ".join(args)))
                for res in results:
                    print(f"[{res['timestamp']}] {res['vulnerability']} at {res['target']}")
            elif cmd == 'mcp':
                if len(args) < 2 or args[0] != 'query':
                    Logger.error("Usage: mcp query <query>")
                    continue
                results = run_async(mcp_router.query(" ".join(args[1:])))
                print(json.dumps(results, indent=2))
            elif cmd == 'report':
                if not args:
                    Logger.error("Usage: report <target>")
                    continue
                target = args[0]
                sql_findings = memory.query(target)
                findings = [{"title": f_type, "description": data, "severity": "medium"} for f_type, data, ts in sql_findings]
                path = run_async(file_executor.generate_report(findings, target=target))
                print(f"Report available at: {path}")
            elif cmd == 'payload':
                if len(args) < 3:
                    Logger.error("Usage: payload <type> <ip> <port>")
                    continue
                p_info = {"target_ip": args[1], "target_port": args[2]}
                path = run_async(file_executor.create_payload(p_info, payload_type=args[0]))
                print(f"Payload available at: {path}")
            elif cmd == 'exploit':
                if not args:
                    Logger.error("Usage: exploit <service_info>")
                    continue
                print(exploit_module.search(" ".join(args)))
            elif cmd == 'stealth':
                stealth_module.clean_logs()
                Logger.info(f"Sandbox check: {stealth_module.check_sandbox()}")
            else:
                Logger.error(f"Unknown command: {cmd}")

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()
