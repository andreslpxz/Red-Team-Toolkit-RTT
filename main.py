import sys
import os
import threading
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

def print_banner():
    banner = """
    \033[36m
     █████╗ ██╗   ██╗██████╗  █████╗
    ██╔══██╗██║   ██║██╔══██╗██╔══██╗
    ███████║██║   ██║██████╔╝███████║
    ██╔══██║██║   ██║██╔══██╗██╔══██║
    ██║  ██║╚██████╔╝██║  ██║██║  ██║
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
    \033[37m[ Aura-Framework v1.0 ]\033[0m
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

def main():
    print_banner()

    if not config.is_valid():
        Logger.warning("GROQ_API_KEY not set. Please update .env")

    commands = ['scan', 'agent', 'exploit', 'stealth', 'memory', 'panic', 'help', 'exit', 'clear']
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
                  agent <objective>  : Start autonomous AI mission
                  scan <target>     : Run background Nmap & AI analysis
                  exploit <info>    : AI-assisted exploit search/payload
                  stealth           : Operational security tools
                  memory <target>   : Show stored findings for target
                  panic             : Wipes keys and logs immediately
                  clear/exit        : System commands
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
            elif cmd == 'memory':
                if not args:
                    Logger.error("Usage: memory <target>")
                    continue
                results = memory.query(args[0])
                for r_type, data, ts in results:
                    print(f"[{ts}] {r_type}: {data[:100]}...")
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
