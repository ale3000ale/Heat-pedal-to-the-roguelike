@echo off
cd /d "%~dp0"
aider --model ollama_chat/qwen2.5-coder:14b --restore-chat-history --multiline
pause