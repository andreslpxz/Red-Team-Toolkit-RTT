import json
import sys
import os
import threading
import asyncio
from types import ModuleType

# --- [ SHIELD: TERMUX COMPATIBILITY PATCH ] ---
# Engañamos a ChromaDB para saltar dependencias pesadas y errores de compilación en ARM64.
fake_modules = [
    "onnxruntime", 
    "tokenizers",
    "opentelemetry.exporter.otlp.proto.grpc.trace_exporter",
    "opentelemetry.exporter.otlp.proto.grpc.metrics_exporter",
    "opentelemetry.exporter.otlp"
]

for module_name in fake_modules:
    if module_name not in sys.modules:
        m = ModuleType(module_name)
        if "trace_exporter" in module_name: m.OTLPSpanExporter = type("OTLPSpanExporter", (), {})
        if "metrics_exporter" in module_name: m.OTLPMetricExporter = type("OTLPMetricExporter", (), {})
        if module_name == "tokenizers": m.Tokenizer = type("Tokenizer", (), {})
        sys.modules[module_name] = m

# --- HNSWLIB ATTR PATCH ---
try:
    import hnswlib
    if not hasattr(hnswlib.Index, 'file_handle_count'):
        hnswlib.Index.file_handle_count = 0
except Exception:
    h = ModuleType("hnswlib")
    h.Index = type("Index", (), {"file_handle_count": 0})
    sys.modules["hnswlib"] = h
# ----------------------------------------------

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

# Aura v2.0 Advanced Core
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
    Logger.success(f"Escaneo para {target} finalizado.")
    memory.store(target, "nmap_scan", output)
    analysis = recon_module.analyze(output)
    Logger.success(f"Análisis IA para {target}:")
    print(analysis)
    memory.store(target, "ai_analysis", analysis)

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def main():
    print_banner()

    if not config.is_valid():
        Logger.warning("GROQ_API_KEY no detectada en .env")

    commands = [
        'scan', 'agent', 'agent-semantic', 'exploit', 'stealth', 'memory',
        'memory-search', 'mcp', 'report', 'payload', 'panic', 'help', 'exit', 'clear'
    ]
    completer = WordCompleter(commands, ignore_case=True)
    session = PromptSession(completer=completer)

    while True:
        try:
            text = session.prompt("aura > ")
            if not text: continue

            parts = text.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == 'exit': break
            elif cmd == 'clear': os.system('clear')
            elif cmd == 'panic': trigger_panic()
            elif cmd == 'help':
                print("""
                Comandos de Aura Framework:
                  agent <meta>                : Misión IA estándar
                  agent-semantic <meta>       : Misión avanzada (Memoria + MCP)
                  scan <target>               : Nmap + Análisis IA
                  exploit <info>              : Búsqueda de exploits
                  mcp query <query>           : Consultar NVD/GitHub/MITRE
                  memory <target>             : Ver hallazgos SQL
                  memory-search <pattern>     : Búsqueda semántica (ChromaDB)
                  report <target>             : Generar reporte técnico
                  payload <type> <ip> <port>  : Crear payload ofuscado
                  stealth                     : Limpieza de logs y OPSEC
                  panic                       : Borrado de emergencia
                """)

            elif cmd == 'scan':
                if not args: continue
                target = args[0]
                recon_module.scan(target, callback=lambda out: handle_background_scan(out, target))

            elif cmd == 'agent':
                if not args: continue
                threading.Thread(target=agent.run, args=(" ".join(args),)).start()

            elif cmd == 'agent-semantic':
                if not args: continue
                run_async(advanced_agent.execute_mission(" ".join(args)))

            elif cmd == 'memory':
                if not args: continue
                results = memory.query(args[0])
                for r_type, data, ts in results:
                    print(f"[{ts}] {r_type}: {data[:80]}...")

            elif cmd == 'memory-search':
                if not args: continue
                results = run_async(semantic_memory.search(" ".join(args)))
                for res in results:
                    print(f"[{res['timestamp']}] {res['vulnerability']} en {res['target']}")

            elif cmd == 'mcp':
                if len(args) < 2: continue
                results = run_async(mcp_router.query(" ".join(args[1:])))
                print(json.dumps(results, indent=2))

            elif cmd == 'report':
                if not args: continue
                sql_findings = memory.query(args[0])
                findings = [{"title": t, "description": d, "severity": "med"} for t, d, ts in sql_findings]
                path = run_async(file_executor.generate_report(findings, target=args[0]))
                print(f"Reporte en: {path}")

            elif cmd == 'payload':
                if len(args) < 3: continue
                p_info = {"target_ip": args[1], "target_port": args[2]}
                path = run_async(file_executor.create_payload(p_info, payload_type=args[0]))
                print(f"Payload en: {path}")

            elif cmd == 'exploit':
                if not args: continue
                print(exploit_module.search(" ".join(args)))

            elif cmd == 'stealth':
                stealth_module.clean_logs()
                Logger.info(f"Sandbox check: {stealth_module.check_sandbox()}")

            else:
                Logger.error(f"Comando no reconocido: {cmd}")

        except KeyboardInterrupt: continue
        except EOFError: break
        except Exception as e:
            Logger.error(f"Error en ejecución: {e}")

if __name__ == "__main__":
    main()
