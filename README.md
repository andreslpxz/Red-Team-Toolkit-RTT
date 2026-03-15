# Red-Team-Toolkit-RTT (Aura Framework)

An AI-powered autonomous red team framework for authorized security research and penetration testing. Built with Groq API integration for intelligent vulnerability analysis and exploitation guidance.

## ⚠️ CRITICAL LEGAL DISCLAIMER

**THIS TOOL IS PROVIDED EXCLUSIVELY FOR AUTHORIZED PENETRATION TESTING AND SECURITY RESEARCH PURPOSES.**

### Legal Requirements:
- **You MUST have explicit written authorization** from the system owner before running ANY scanning, exploitation, or analysis activities
- Unauthorized access to computer systems is **ILLEGAL** in most jurisdictions (Computer Fraud and Abuse Act in the US, Computer Misuse Act in the UK, and equivalent laws globally)
- The authors and contributors are **NOT responsible** for any misuse or illegal activities conducted with this toolkit
- Users assume **full legal responsibility** for their actions

### Permitted Uses Only:
✅ Authorized penetration testing with signed client agreements  
✅ Security research in controlled lab environments  
✅ Educational purposes in institutional settings with proper authorization  
✅ Red team exercises within your own organization with management approval  

### Prohibited Uses:
❌ Unauthorized network scanning or reconnaissance  
❌ Exploitation of systems without explicit permission  
❌ Testing on third-party systems without written consent  
❌ Any illegal or malicious activities  

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Command Reference](#command-reference)
- [Modules](#modules)
- [Security Considerations](#security-considerations)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### Autonomous Red Team Agent
- **ReAct Pattern Implementation**: Thought-Action-Observation loop for intelligent autonomous missions
- **AI-Powered Analysis**: Integrates Groq LLM for vulnerability identification and exploitation vectors
- **Multi-Module Architecture**: Modular design for scanning, exploitation, stealth, and memory management

### Core Capabilities

| Module | Purpose |
|--------|---------|
| **Recon** | Network scanning with Nmap + AI-driven vulnerability analysis |
| **Agent** | Autonomous execution of red team objectives |
| **Exploit** | Exploitation vector identification and payload generation |
| **Stealth** | Operational security tools and environment detection |
| **Memory** | Persistent data storage for findings and analysis |

### Intelligent Features
- 🤖 Autonomous agent reasoning with LLM guidance
- 🔍 Automated vulnerability analysis from Nmap output
- 🎯 Context-aware exploit recommendations
- 💾 Session persistence for multi-target campaigns
- 🛡️ Sandbox detection capabilities
- ⚡ Background scanning with real-time AI analysis

---

## 🏗️ Architecture

```
Red-Team-Toolkit-RTT/
├── core/
│   ├── agent.py          # Autonomous ReAct agent orchestrator
│   ├── groq_client.py    # Groq API integration
│   └── memory.py         # Session data persistence
├── modules/
│   ├── recon.py          # Network reconnaissance (Nmap)
│   ├── exploit.py        # Exploitation & payload generation
│   ├── stealth.py        # OPSEC & environment detection
│   └── remote.py         # Remote execution capabilities
├── utils/
│   ├── config.py         # Configuration management
│   ├── logger.py         # Colored logging system
│   └── panic.py          # Emergency data sanitization
├── main.py               # CLI interface
└── requirements.txt      # Python dependencies
```

### Data Flow

```
User Command
    ↓
CLI Parser (main.py)
    ↓
Module Router (agent.py / specific modules)
    ↓
Groq LLM (vulnerability analysis)
    ↓
Memory System (persistence)
    ↓
CLI Output
```

---

## 📦 Installation

### Prerequisites
- **Python 3.9+**
- **Nmap** (for reconnaissance module)
- **Groq API Key** (free tier available at [console.groq.com](https://console.groq.com))
- Linux/macOS/Windows with WSL2

### Step 1: Clone Repository
```bash
git clone https://github.com/andreslpxz/Red-Team-Toolkit-RTT.git
cd Red-Team-Toolkit-RTT
```

### Step 2: Install Nmap (if not installed)

**macOS:**
```bash
brew install nmap
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install nmap
```

**Windows:**
Download from [nmap.org](https://nmap.org/download.html)

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
# or for Python 3-specific:
pip3 install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Create .env file
nano .env

# Add the following:
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
```

**Get your Groq API Key:**
1. Go to [console.groq.com](https://console.groq.com)
2. Create a free account
3. Generate API key in the API Keys section
4. Add to `.env` file

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: Groq API Key (get free at console.groq.com)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx

# Optional: LLM Model (default: llama-3.3-70b-versatile)
MODEL_NAME=mllama-3.3-70b-versatile

# Optional: Max iterations for autonomous agent
MAX_ITERATIONS=5

# Optional: Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### Configuration Files

**utils/config.py** - Application settings
```python
# Modify these defaults as needed
config = {
    "max_agent_iterations": 5,
    "nmap_timeout": 300,
    "sandbox_check_enabled": True,
}
```

---

## 🚀 Usage

### Starting the Framework

```bash
python3 main.py
```

You'll see:
```
    ╔════════════════════════════════════╗
    │  Aura-Framework v1.0               │
    │  [!] AUTHORIZED PENETRATION        │
    │      TESTING ONLY                  │
    ╚════════════════════════════════════╝

aura > 
```

### Interactive Commands

```bash
aura > help
```

Shows available commands:
```
Aura Framework Commands:
  agent <objective>     : Start autonomous AI mission
  scan <target>        : Run background Nmap & AI analysis
  exploit <info>       : AI-assisted exploit search
  stealth              : Operational security tools
  memory <target>      : Show stored findings
  panic                : Emergency data wipe
  clear/exit           : System commands
```

---

## 📖 Command Reference

### 1. Network Scanning with AI Analysis

**Basic scan:**
```bash
aura > scan 192.168.1.100
```

**What happens:**
- Launches Nmap fast scan (`-F -sV`)
- Sends output to Groq for vulnerability analysis
- Stores results in memory system
- Displays AI-generated recommendations

**Output example:**
```
[INFO] Running Nmap scan on 192.168.1.100...
[INFO] Analyzing Nmap output with Groq...
[SUCCESS] AI Analysis for 192.168.1.100:

Found potential vulnerabilities:
- Apache 2.4.41: CVE-2021-3156 buffer overflow
- OpenSSH 7.4: User enumeration possible
- MySQL 5.7.30: Weak authentication bypass...
```

### 2. Autonomous Agent Missions

**Start autonomous red team agent:**
```bash
aura > agent identify vulnerable services on 192.168.1.100
```

**Agent reasoning loop:**
```
[INFO] Iteration 1/5

Agent Thought: I need to scan the target first to identify services

Executing Action: nmap_scan(192.168.1.100)
[Receives Nmap output]

Agent Thought: Now I'll analyze the vulnerabilities in these services

Executing Action: analyze_vulns([Nmap output])
[Receives vulnerability analysis]

Agent Thought: Found Apache with CVE-2021-3156, let me search for exploits

Executing Action: search_exploit(Apache 2.4.41)
[Receives exploit information]

Agent Thought: I have sufficient information for the objective

Executing Action: finalize([Summary of findings])
```

### 3. Exploit Vector Search

**Find exploitation paths:**
```bash
aura > exploit Apache 2.4.41 on Windows Server 2019
```

**Output:**
```
[INFO] Searching exploits for: Apache 2.4.41 on Windows Server 2019
Apache 2.4.41 CVE-2021-3156 Buffer Overflow:
- CVSS Score: 9.8 (Critical)
- Attack Vector: Network
- Required Privileges: None
- Affected Versions: 2.4.0 - 2.4.49
...
```

### 4. Operational Security

**Check environment:**
```bash
aura > stealth
```

**Output:**
```
[WARNING] Initiating log cleaning sequence...
[INFO] Sandbox check: Environment appears to be a standard OS/Termux.
```

### 5. Session Memory Management

**View findings for a target:**
```bash
aura > memory 192.168.1.100
```

**Output:**
```
[2024-01-15 14:32:45] nmap_scan: Nmap scan report for 192.168.1.100...
[2024-01-15 14:33:12] ai_analysis: Found 3 high-risk vulnerabilities...
[2024-01-15 14:34:01] exploit_search: Apache 2.4.41 - CVE-2021-3156...
```

### 6. Emergency Data Sanitization

**Wipe all sensitive data immediately:**
```bash
aura > panic
```

**⚠️ WARNING:** This will:
- Delete `.env` file (API keys)
- Clear `aura.log` file
- Remove session database
- Exit the application immediately

---

## 🔧 Modules Deep Dive

### Recon Module (`modules/recon.py`)

**Methods:**
```python
# Run Nmap scan with optional callback
recon_module.scan(target, callback=None)

# Analyze Nmap output with Groq
recon_module.analyze(nmap_output)
```

**Nmap Parameters Used:**
- `-F`: Fast scan (most common 100 ports)
- `-sV`: Service version detection
- Timeout: 5 minutes (300s)

**Vulnerability Analysis:**
- Sends raw Nmap output to Groq
- LLM identifies CVEs and attack vectors
- Returns actionable exploit recommendations

### Exploit Module (`modules/exploit.py`)

**Methods:**
```python
# Search for known exploits
exploit_module.search(service_info)

# Generate obfuscated payloads
exploit_module.generate_payload(task)

# Apply polymorphic obfuscation
exploit_module.obfuscate_python(code)
```

**Payload Generation:**
- Requests Python code from Groq
- Applies Base64 encoding
- Randomizes variable names
- Creates polymorphic wrapper

⚠️ **Note:** Generated payloads are for educational/authorized testing ONLY

### Stealth Module (`modules/stealth.py`)

**Methods:**
```python
# Clean operational traces
stealth_module.clean_logs()

# Detect restricted environments
stealth_module.check_sandbox()
```

**Log Targets (simulated):**
- `~/.bash_history`
- `/var/log/` directories
- Application-specific logs

**Sandbox Detection:**
- Docker environment detection (`.dockerenv`)
- Virtualization checks (`/proc/vz`)
- Container runtime identification

### Agent Module (`core/agent.py`)

**ReAct Loop Implementation:**

The agent uses a standardized loop:
1. **Thought**: Reasoning about current state
2. **Action**: Dispatching a task to modules
3. **Observation**: Processing results
4. **Iteration**: Updating context and continuing

**Available Actions:**
- `nmap_scan[target]`: Network scanning
- `analyze_vulns[output]`: Vulnerability analysis
- `search_exploit[service]`: Exploit identification
- `finalize[result]`: Mission completion

**Max Iterations:** 5 (configurable)

### Memory Module (`core/memory.py`)

**Data Persistence:**
```python
# Store findings
memory.store(target, "nmap_scan", output_data)

# Query by target
results = memory.query("192.168.1.100")

# Retrieved as: (type, data, timestamp)
```

**Storage Backend:** SQLite (in `data/db/aura.db`)

---

## 🛡️ Security Considerations

### Defense-in-Depth Recommendations

#### 1. API Key Management
```bash
# ✅ DO: Use environment variables
export GROQ_API_KEY="your_key"

# ❌ DON'T: Commit keys to git
# Add to .gitignore:
echo ".env" >> .gitignore
```

#### 2. Network Isolation
- Run only in isolated lab networks
- Use VPN for remote authorized testing
- Implement firewall rules restricting scanner IP

#### 3. Logging & Audit Trail
- All activities logged to `logs/aura.log`
- Maintain audit trail for compliance
- Store logs securely if required by contract

#### 4. Credential Management
```bash
# Never hardcode credentials
# Use .env with proper permissions
chmod 600 .env

# Rotate API keys regularly
```

#### 5. Post-Engagement Cleanup
```bash
# After authorized testing:
aura > panic  # Wipe all session data

# Verify deletion
ls -la .env   # Should not exist
```

### Recommended Practices

1. **Authorization Documentation**
   - Obtain signed Rules of Engagement (RoE)
   - Define scope clearly (IP ranges, systems, timeframes)
   - Get approval from multiple stakeholders

2. **Safe Testing Environment**
   - Use dedicated lab network
   - Isolate targets from production systems
   - Use dedicated VPN/proxy infrastructure

3. **Monitoring & Logging**
   - Monitor all tool activity
   - Keep detailed logs of all scanning/exploitation
   - Document findings chronologically

4. **Responsible Disclosure**
   - Report vulnerabilities to vendor first
   - Allow reasonable time for patching
   - Follow coordinated disclosure timeline

5. **Legal Review**
   - Have legal review authorization documents
   - Understand jurisdiction-specific laws
   - Know escalation procedures

---

## 📚 Requirements

### System Requirements
- Python 3.9 or higher
- 4GB RAM minimum (8GB recommended)
- 500MB disk space
- Linux, macOS, or Windows with WSL2

### Python Dependencies
```
groq              # Groq API client
python-dotenv     # Environment variable management
prompt_toolkit    # Interactive CLI
aiohttp          # Async HTTP requests
requests         # HTTP library
colorama         # Terminal colors
```

### External Tools
- **Nmap** 7.80+ (for reconnaissance)

### API Requirements
- **Groq API Key** (free tier: 30 requests/minute)
- Internet connection for LLM calls

---

## 🧪 Testing & Validation

### Dry-Run (No Authorization Required)
```bash
# Test CLI without scanning
aura > help
aura > memory test_target
aura > clear
aura > exit
```

### Lab Testing (With Lab Authorization)
```bash
# On isolated network only
aura > scan 10.0.0.100  # Lab IP only

# Test exploitation vectors
aura > exploit Apache 2.4.1

# Start autonomous mission
aura > agent scan 10.0.0.0/24 for vulnerabilities
```

---

## 🤝 Contributing

We welcome contributions from security researchers, but with strict guidelines:

### Contribution Areas
- ✅ Bug fixes and stability improvements
- ✅ Better LLM prompting for analysis
- ✅ Enhanced logging and audit trails
- ✅ Documentation improvements
- ✅ Defensive tools and detection methods

### Not Accepted
- ❌ Code to bypass authorization checks
- ❌ Evasion techniques for IDS/AV
- ❌ Obfuscation improvements
- ❌ Features to hide/delete evidence
- ❌ Anti-forensics enhancements

### Pull Request Process
1. Fork the repository
2. Create feature branch: `git checkout -b feature/improvement`
3. Add comprehensive documentation
4. Ensure legal compliance of changes
5. Submit PR with detailed description

---

## 📜 License

This project is released under the **Apache-2.0 license**. See `LICENSE` file for details.

### License Terms
- ✅ Free to use for authorized testing
- ✅ Free to modify and distribute
- ⚠️ User assumes all legal responsibility
- ⚠️ Authors provide NO WARRANTY

**By using this software, you agree to:**
- Only use for authorized purposes
- Comply with all applicable laws
- Assume full legal responsibility
- Hold authors harmless from misuse

---

## ⚖️ Legal References

### United States
- **Computer Fraud and Abuse Act (CFAA)** - 18 U.S.C. § 1030
- Unauthorized access to computer systems is federal crime
- Penalties: Up to 10 years imprisonment, $250,000+ fines

### United Kingdom
- **Computer Misuse Act 1990** (updated 2015)
- Unauthorized access and modification are criminal offenses
- Penalties: Up to 10 years imprisonment

### European Union
- **NIS Directive** (2016/1148) - Cybersecurity requirements
- **GDPR Article 32** - Security of processing
- Various national laws implementing EU directives

### Other Jurisdictions
- Australia: Computer Crime Act
- Canada: Criminal Code sections 342-342.2
- India: Information Technology Act 2000

**You are responsible for understanding laws in YOUR jurisdiction.**

---

## 🆘 Support & Troubleshooting

### Common Issues

**Problem: "Groq API Key not found"**
```bash
# Solution: Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

# Verify
cat .env
```

**Problem: "Nmap command not found"**
```bash
# Solution: Install Nmap
# macOS:
brew install nmap

# Ubuntu/Debian:
sudo apt-get install nmap

# Verify:
nmap --version
```

**Problem: "Connection timeout on scan"**
- Check network connectivity: `ping 192.168.1.1`
- Verify Nmap has permission to scan
- Check firewall rules
- Increase timeout in `config.py`

**Problem: "Groq API rate limit exceeded"**
- Free tier: 30 requests/minute
- Wait before making new requests
- Consider upgrading Groq plan for more quota

**Problem: "ModuleNotFoundError: No module named groq"**
```bash
# Solution: Install missing dependencies
pip3 install -r requirements.txt

# Or individually:
pip3 install groq python-dotenv prompt_toolkit
```

### Getting Help

1. Check this README first
2. Review error messages carefully
3. Check Groq API status: https://status.groq.com
4. Verify network connectivity
5. Check file permissions on `.env`

---

## 📊 Project Statistics

- **Lines of Code:** ~1,500
- **Modules:** 7 core modules
- **Python Version:** 3.9+
- **Dependencies:** 6
- **License:** Apache-2.0
- **Status:** Active Development

---

## 🔮 Roadmap

### Planned Features
- [ ] Multi-target batch processing
- [ ] Custom LLM integration (Ollama, local models)
- [ ] OSINT module for passive reconnaissance
- [ ] Web application testing module
- [ ] Social engineering vector analysis
- [ ] Persistence mechanism research
- [ ] C2 framework integration
- [ ] Encrypted report generation

### Community Requests
- Better Windows support
- Integration with Burp Suite API
- Slack/Discord notification system
- Web UI dashboard

---

## 📧 Contact & Attribution

**Original Author:** andreslpxz  
**GitHub:** https://github.com/andreslpxz  
**Repository:** https://github.com/andreslpxz/Red-Team-Toolkit-RTT

### Contributors
- Welcome to contribute under our guidelines

### Acknowledgments
- Groq for providing the API
- Nmap project for reconnaissance tools
- Python community for excellent libraries

---

## ⚡ Quick Start (TL;DR)

```bash
# 1. Clone
git clone https://github.com/andreslpxz/Red-Team-Toolkit-RTT.git
cd Red-Team-Toolkit-RTT

# 2. Get API key at console.groq.com

# 3. Configure
echo "GROQ_API_KEY=your_key" > .env

# 4. Install
pip3 install -r requirements.txt

# 5. Run (with authorization ONLY)
python3 main.py

# 6. Use
aura > scan 192.168.1.100
aura > agent find critical vulnerabilities on target_ip
aura > exploit Apache 2.4.41
```

---

**REMEMBER: Unauthorized access is ILLEGAL. Ensure you have written permission before using this tool.**

---

*Last Updated: January 2025*  
*Disclaimer Version: 2.0*  
*Maintained by: Security Research Community*
