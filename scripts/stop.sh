#!/bin/bash
PID=$(ps aux | grep '[s]can_bot_secure.py' | awk '{print $2}')
if [ -n "$PID" ]; then
  kill $PID
  echo "🛑 Sherlock terminato (PID: $PID)"
else
  echo "ℹ️ Nessun processo Sherlock trovato"
fi
