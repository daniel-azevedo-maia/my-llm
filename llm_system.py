"""
Sistema de LLM Local
Módulo responsável pela integração com Ollama/Llama e geração de respostas
"""

import requests
import json
import logging
import subprocess
import time
from typing import List, Dict, Any, Optional
from document_processor import DocumentProcessor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalLLM:
    """Classe para integração com LLM local via Ollama"""
    
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """
        Inicializa o sistema LLM
        
        Args:
            model_name: Nome do modelo Ollama
            base_url: URL base do servidor Ollama
        """
        self.model_name = model_name
        self.base_url = base_url
        self.document_processor = DocumentProcessor()
        self.conversation_history = []
        
    def check_ollama_installation(self) -> bool:
        """Verifica se Ollama está instalado"""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def install_ollama(self) -> bool:
        """Instala Ollama (Linux/Mac)"""
        try:
            logger.info("Instalando Ollama...")
            result = subprocess.run([
                'curl', '-fsSL', 'https://ollama.com/install.sh'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Executa o script de instalação
                subprocess.run(['sh'], input=result.stdout, text=True, timeout=120)
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao instalar Ollama: {e}")
            return False
    
    def start_ollama_server(self) -> bool:
        """Inicia o servidor Ollama"""
        try:
            # Verifica se já está rodando
            if self.is_server_running():
                return True
            
            logger.info("Iniciando servidor Ollama...")
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Aguarda o servidor iniciar
            for _ in range(30):  # 30 segundos timeout
                time.sleep(1)
                if self.is_server_running():
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor Ollama: {e}")
            return False
    
    def is_server_running(self) -> bool:
        """Verifica se o servidor Ollama está rodando"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def download_model(self, progress_callback=None) -> bool:
        """Baixa o modelo LLM"""
        try:
            if progress_callback:
                progress_callback("Verificando modelo...")
            
            # Verifica se modelo já existe
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if self.model_name in model.get('name', ''):
                        logger.info(f"Modelo {self.model_name} já está disponível")
                        return True
            
            if progress_callback:
                progress_callback("Baixando modelo... Isso pode demorar alguns minutos...")
            
            logger.info(f"Baixando modelo {self.model_name}...")
            result = subprocess.run([
                'ollama', 'pull', self.model_name
            ], capture_output=True, text=True, timeout=1800)  # 30 minutos timeout
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Erro ao baixar modelo: {e}")
            return False
    
    def setup_system(self, progress_callback=None) -> bool:
        """Configura todo o sistema LLM"""
        try:
            if progress_callback:
                progress_callback("Verificando Ollama...")
            
            # Verifica instalação do Ollama
            if not self.check_ollama_installation():
                if progress_callback:
                    progress_callback("Instalando Ollama...")
                if not self.install_ollama():
                    return False
            
            # Inicia servidor
            if progress_callback:
                progress_callback("Iniciando servidor...")
            if not self.start_ollama_server():
                return False
            
            # Baixa modelo
            if not self.download_model(progress_callback):
                return False
            
            if progress_callback:
                progress_callback("Sistema configurado com sucesso!")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na configuração do sistema: {e}")
            return False
    
    def generate_response(self, prompt: str, context: str = "", use_context: bool = True) -> str:
        """
        Gera resposta usando o modelo LLM
        
        Args:
            prompt: Pergunta do usuário
            context: Contexto adicional dos documentos
            use_context: Se deve usar contexto dos documentos
        
        Returns:
            Resposta gerada pelo modelo
        """
        try:
            # Busca contexto relevante se solicitado
            relevant_context = ""
            if use_context:
                search_results = self.document_processor.search_knowledge(prompt)
                if search_results:
                    relevant_context = "\n\n".join([
                        f"[{result['filename']}]: {result['content']}"
                        for result in search_results[:3]  # Top 3 resultados
                    ])
            
            # Constrói o prompt completo
            system_prompt = """Você é um assistente inteligente que responde perguntas baseado em documentos fornecidos pelo usuário. 

Instruções:
- Responda sempre em português brasileiro
- Use apenas as informações dos documentos fornecidos quando disponíveis
- Se não houver informação suficiente nos documentos, diga que não encontrou a informação
- Seja preciso e objetivo
- Cite a fonte quando possível (nome do arquivo)
"""
            
            full_prompt = system_prompt
            
            if relevant_context:
                full_prompt += f"\n\nContexto dos documentos:\n{relevant_context}"
            
            if context:
                full_prompt += f"\n\nContexto adicional:\n{context}"
            
            full_prompt += f"\n\nPergunta do usuário: {prompt}\n\nResposta:"
            
            # Faz requisição para Ollama
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()
                
                # Adiciona à história da conversa
                self.conversation_history.append({
                    'user': prompt,
                    'assistant': answer,
                    'context_used': bool(relevant_context)
                })
                
                return answer
            else:
                logger.error(f"Erro na requisição: {response.status_code}")
                return "Desculpe, ocorreu um erro ao gerar a resposta."
                
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta."
    
    def add_document(self, file_path: str, progress_callback=None) -> bool:
        """
        Adiciona documento à base de conhecimento
        
        Args:
            file_path: Caminho para o arquivo
            progress_callback: Função de callback para progresso
        
        Returns:
            True se adicionado com sucesso
        """
        return self.document_processor.process_document(file_path, progress_callback)
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da base de conhecimento"""
        return self.document_processor.get_document_stats()
    
    def clear_knowledge(self):
        """Limpa toda a base de conhecimento"""
        self.document_processor.clear_knowledge_base()
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Retorna histórico da conversa"""
        return self.conversation_history.copy()
    
    def clear_conversation(self):
        """Limpa histórico da conversa"""
        self.conversation_history = []


class LLMTrainer:
    """Classe para simular treinamento e mostrar progresso motivacional"""
    
    def __init__(self, llm: LocalLLM):
        self.llm = llm
        self.training_messages = [
            "Analisando documento...",
            "Extraindo conhecimento...",
            "Aprendendo conceitos importantes...",
            "Organizando informações...",
            "Criando conexões semânticas...",
            "Indexando conteúdo...",
            "Otimizando busca...",
            "Finalizando processamento...",
            "Que tal ir tomar um café? ☕",
            "Estou quase terminando...",
            "Absorvendo sabedoria...",
            "Conectando ideias...",
        ]
    
    def train_with_document(self, file_path: str, progress_callback=None) -> bool:
        """
        'Treina' o modelo com um documento (na verdade apenas processa)
        
        Args:
            file_path: Caminho para o arquivo
            progress_callback: Função de callback para progresso
        
        Returns:
            True se processado com sucesso
        """
        import random
        
        def enhanced_callback(message):
            if progress_callback:
                # Adiciona mensagens motivacionais aleatórias
                if random.random() < 0.3:  # 30% chance
                    motivational = random.choice(self.training_messages)
                    progress_callback(f"{message} - {motivational}")
                else:
                    progress_callback(message)
        
        # Simula tempo de processamento para dar sensação de "aprendizado"
        time.sleep(0.5)
        
        success = self.llm.add_document(file_path, enhanced_callback)
        
        if success and progress_callback:
            progress_callback("🎉 Obrigado! Já aprendi tudo sobre este documento!")
            time.sleep(1)
        
        return success


if __name__ == "__main__":
    # Teste básico
    llm = LocalLLM()
    print("Sistema LLM inicializado")
    print("Servidor rodando:", llm.is_server_running())
    print("Estatísticas:", llm.get_knowledge_stats())

