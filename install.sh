#!/bin/bash

echo "[*] Initializing Aura-Framework Installation for Termux..."

# Update and upgrade
pkg update -y && pkg upgrade -y

# Install dependencies
echo "[*] Installing system dependencies..."
pkg install -y python nmap ndk-sysroot clang make libffi openssl

# Install Python packages
echo "[*] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs data/db

# Check for .env file
if [ ! -f .env ]; then
    echo "[!] .env file not found. Creating a template..."
    cat <<EOF > .env
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
EOF
    echo "[+] .env template created. Please add your Groq API key."
fi

# Ensure executable permissions
chmod +x install.sh
chmod +x main.py

echo "[+] Installation complete! Run 'python3 main.py' to start."
