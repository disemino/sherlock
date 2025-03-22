#!/bin/bash
source ../venv/bin/activate
nohup python3 ../bot/scan_bot_secure.py > ../nohup.out 2>&1 &
echo "✅ Sherlock avviato in background (PID: $!)"
