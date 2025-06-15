#!/usr/bin/env python3
"""
Sistema LLM Local - Arquivo Principal
Integra todos os componentes do sistema para criar uma aplicação completa
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 7):
        print("❌ Erro: Python 3.7 ou superior é necessário")
        print(f"Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def install_package(package_name, import_name=None):
    """Instala um pacote Python se não estiver disponível"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} já está instalado")
        return True
    except ImportError:
        print(f"📦 Instalando {package_name}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package_name, "--user"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package_name} instalado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Erro ao instalar {package_name}")
            return False

def install_dependencies():
    """Instala todas as dependências necessárias"""
    print("🔧 Verificando e instalando dependências...")
    
    dependencies = [
        ("PyPDF2", "PyPDF2"),
        ("python-docx", "docx"),
        ("chromadb", "chromadb"),
        ("requests", "requests"),
    ]
    
    all_installed = True
    for package, import_name in dependencies:
        if not install_package(package, import_name):
            all_installed = False
    
    return all_installed

def check_ollama():
    """Verifica se Ollama está disponível"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama está instalado")
            return True
        else:
            print("❌ Ollama não está funcionando corretamente")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️ Ollama não está instalado")
        return False

def install_ollama():
    """Instala Ollama automaticamente (Linux/Mac)"""
    print("📦 Instalando Ollama...")
    try:
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            # Linux/Mac
            result = subprocess.run([
                'curl', '-fsSL', 'https://ollama.com/install.sh'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                subprocess.run(['sh'], input=result.stdout, text=True, timeout=300)
                print("✅ Ollama instalado com sucesso")
                return True
            else:
                print("❌ Erro ao baixar script de instalação do Ollama")
                return False
        else:
            # Windows
            print("⚠️ Para Windows, baixe Ollama manualmente de: https://ollama.com/download")
            print("Após instalar, execute este script novamente.")
            return False
    except Exception as e:
        print(f"❌ Erro ao instalar Ollama: {e}")
        return False

def setup_system():
    """Configura todo o sistema"""
    print("🚀 Configurando Sistema LLM Local...")
    print("=" * 50)
    
    # Verifica Python
    if not check_python_version():
        return False
    
    # Instala dependências Python
    if not install_dependencies():
        print("❌ Erro ao instalar dependências Python")
        return False
    
    # Verifica Ollama
    if not check_ollama():
        print("\n🤖 Ollama é necessário para executar a IA local")
        response = input("Deseja instalar Ollama automaticamente? (s/n): ").lower()
        
        if response in ['s', 'sim', 'y', 'yes']:
            if not install_ollama():
                print("❌ Falha na instalação do Ollama")
                print("Por favor, instale manualmente: https://ollama.com/download")
                return False
        else:
            print("Por favor, instale Ollama manualmente: https://ollama.com/download")
            return False
    
    print("\n✅ Sistema configurado com sucesso!")
    return True

def main():
    """Função principal"""
    print("🤖 Sistema LLM Local v1.0")
    print("=" * 30)
    
    # Verifica se é primeira execução
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        if setup_system():
            print("\n🎉 Configuração concluída!")
            print("Execute novamente sem --setup para iniciar a aplicação.")
        else:
            print("\n❌ Configuração falhou. Verifique os erros acima.")
        return
    
    # Verifica se dependências estão disponíveis
    try:
        # Importa módulos locais
        from gui_interface import MainApplication
        
        print("🚀 Iniciando aplicação...")
        app = MainApplication()
        app.run()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("\n💡 Execute primeiro com --setup para configurar o sistema:")
        print(f"python {sys.argv[0]} --setup")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print("\nSe o problema persistir, verifique se todas as dependências estão instaladas.")

if __name__ == "__main__":
    main()

