@echo off
REM Script de instalação para Windows
echo 🤖 Sistema LLM Local - Instalação Windows
echo =====================================

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo Por favor, instale Python 3.7+ de: https://python.org/downloads
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Instala dependências
echo 📦 Instalando dependências Python...
python -m pip install --user PyPDF2 python-docx chromadb requests

REM Verifica Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Ollama não encontrado
    echo Por favor, baixe e instale Ollama de: https://ollama.com/download
    echo Após instalar, execute este script novamente
    pause
    exit /b 1
)

echo ✅ Ollama encontrado

REM Baixa modelo
echo 🧠 Baixando modelo Llama 3.1 (isso pode demorar)...
ollama pull llama3.1

echo ✅ Instalação concluída!
echo Para iniciar: python main.py
pause

