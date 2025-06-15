"""
Sistema de Processamento de Documentos
Módulo responsável por extrair texto de diferentes formatos de arquivo
"""

import os
import sqlite3
import hashlib
from typing import List, Dict, Any
from pathlib import Path
import logging

# Imports para processamento de documentos
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Classe para processamento de documentos e gerenciamento de conhecimento"""
    
    def __init__(self, db_path: str = "knowledge_base"):
        """
        Inicializa o processador de documentos
        
        Args:
            db_path: Caminho para o banco de dados de conhecimento
        """
        self.db_path = db_path
        self.setup_database()
        self.setup_vector_db()
    
    def setup_database(self):
        """Configura o banco de dados SQLite"""
        os.makedirs(self.db_path, exist_ok=True)
        self.db_file = os.path.join(self.db_path, "documents.db")
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Tabela para metadados dos documentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                file_type TEXT NOT NULL,
                processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                chunk_count INTEGER DEFAULT 0
            )
        ''')
        
        # Tabela para chunks de texto
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_index INTEGER,
                content TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_vector_db(self):
        """Configura o banco de dados vetorial ChromaDB"""
        if chromadb is None:
            logger.warning("ChromaDB não instalado. Funcionalidade de busca semântica limitada.")
            self.chroma_client = None
            return
        
        try:
            # Configuração para persistência local
            self.chroma_client = chromadb.PersistentClient(
                path=os.path.join(self.db_path, "chroma_db")
            )
            
            # Coleção para embeddings
            self.collection = self.chroma_client.get_or_create_collection(
                name="document_chunks",
                metadata={"description": "Chunks de documentos para busca semântica"}
            )
        except Exception as e:
            logger.error(f"Erro ao configurar ChromaDB: {e}")
            self.chroma_client = None
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calcula hash MD5 do arquivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrai texto de arquivo PDF"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 não está instalado. Execute: pip install PyPDF2")
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF {file_path}: {e}")
            raise
        
        return text.strip()
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extrai texto de arquivo DOCX"""
        if Document is None:
            raise ImportError("python-docx não está instalado. Execute: pip install python-docx")
        
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            logger.error(f"Erro ao extrair texto do DOCX {file_path}: {e}")
            raise
        
        return text.strip()
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extrai texto de arquivo TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Tenta com encoding latin-1 se UTF-8 falhar
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Divide o texto em chunks menores para processamento
        
        Args:
            text: Texto a ser dividido
            chunk_size: Tamanho máximo de cada chunk
            overlap: Sobreposição entre chunks
        
        Returns:
            Lista de chunks de texto
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Tenta quebrar em uma frase completa
            if end < len(text):
                # Procura pelo último ponto, exclamação ou interrogação
                last_sentence = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                
                if last_sentence > start:
                    end = last_sentence + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def process_document(self, file_path: str, progress_callback=None) -> bool:
        """
        Processa um documento e adiciona ao banco de conhecimento
        
        Args:
            file_path: Caminho para o arquivo
            progress_callback: Função de callback para progresso
        
        Returns:
            True se processado com sucesso, False caso contrário
        """
        try:
            # Verifica se arquivo existe
            if not os.path.exists(file_path):
                logger.error(f"Arquivo não encontrado: {file_path}")
                return False
            
            # Calcula hash do arquivo
            file_hash = self.calculate_file_hash(file_path)
            filename = os.path.basename(file_path)
            file_ext = Path(file_path).suffix.lower()
            
            # Verifica se já foi processado
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM documents WHERE file_hash = ?", (file_hash,))
            existing = cursor.fetchone()
            
            if existing:
                logger.info(f"Documento {filename} já foi processado anteriormente")
                conn.close()
                return True
            
            if progress_callback:
                progress_callback("Extraindo texto do documento...")
            
            # Extrai texto baseado na extensão
            if file_ext == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_ext == '.docx':
                text = self.extract_text_from_docx(file_path)
            elif file_ext == '.txt':
                text = self.extract_text_from_txt(file_path)
            else:
                logger.error(f"Formato de arquivo não suportado: {file_ext}")
                conn.close()
                return False
            
            if not text.strip():
                logger.warning(f"Nenhum texto extraído do arquivo: {filename}")
                conn.close()
                return False
            
            if progress_callback:
                progress_callback("Dividindo texto em chunks...")
            
            # Divide em chunks
            chunks = self.chunk_text(text)
            
            # Salva no banco de dados
            cursor.execute('''
                INSERT INTO documents (filename, file_hash, file_type, chunk_count)
                VALUES (?, ?, ?, ?)
            ''', (filename, file_hash, file_ext, len(chunks)))
            
            document_id = cursor.lastrowid
            
            # Salva chunks
            for i, chunk in enumerate(chunks):
                cursor.execute('''
                    INSERT INTO chunks (document_id, chunk_index, content)
                    VALUES (?, ?, ?)
                ''', (document_id, i, chunk))
            
            conn.commit()
            
            if progress_callback:
                progress_callback("Criando embeddings para busca...")
            
            # Adiciona ao banco vetorial se disponível
            if self.chroma_client and self.collection:
                try:
                    chunk_ids = [f"{document_id}_{i}" for i in range(len(chunks))]
                    metadatas = [
                        {
                            "document_id": document_id,
                            "filename": filename,
                            "chunk_index": i
                        }
                        for i in range(len(chunks))
                    ]
                    
                    self.collection.add(
                        documents=chunks,
                        metadatas=metadatas,
                        ids=chunk_ids
                    )
                except Exception as e:
                    logger.warning(f"Erro ao adicionar embeddings: {e}")
            
            conn.close()
            logger.info(f"Documento {filename} processado com sucesso ({len(chunks)} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar documento {file_path}: {e}")
            return False
    
    def search_knowledge(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca conhecimento relevante baseado na query
        
        Args:
            query: Texto da consulta
            max_results: Número máximo de resultados
        
        Returns:
            Lista de chunks relevantes com metadados
        """
        results = []
        
        # Busca semântica com ChromaDB se disponível
        if self.chroma_client and self.collection:
            try:
                search_results = self.collection.query(
                    query_texts=[query],
                    n_results=max_results
                )
                
                if search_results['documents'] and search_results['documents'][0]:
                    for i, doc in enumerate(search_results['documents'][0]):
                        metadata = search_results['metadatas'][0][i]
                        distance = search_results['distances'][0][i] if 'distances' in search_results else 0
                        
                        results.append({
                            'content': doc,
                            'filename': metadata.get('filename', 'Unknown'),
                            'chunk_index': metadata.get('chunk_index', 0),
                            'relevance_score': 1 - distance  # Converte distância em score
                        })
                
                return results
                
            except Exception as e:
                logger.warning(f"Erro na busca semântica: {e}")
        
        # Busca por palavra-chave como fallback
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Busca simples por palavras-chave
        query_words = query.lower().split()
        search_pattern = '%' + '%'.join(query_words) + '%'
        
        cursor.execute('''
            SELECT c.content, d.filename, c.chunk_index
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE LOWER(c.content) LIKE ?
            ORDER BY c.id
            LIMIT ?
        ''', (search_pattern, max_results))
        
        for row in cursor.fetchall():
            results.append({
                'content': row[0],
                'filename': row[1],
                'chunk_index': row[2],
                'relevance_score': 0.5  # Score padrão para busca por palavra-chave
            })
        
        conn.close()
        return results
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de conhecimento"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chunks")
        chunk_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT file_type, COUNT(*) FROM documents GROUP BY file_type")
        file_types = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_documents': doc_count,
            'total_chunks': chunk_count,
            'file_types': file_types
        }
    
    def clear_knowledge_base(self):
        """Limpa toda a base de conhecimento"""
        # Limpa banco SQLite
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chunks")
        cursor.execute("DELETE FROM documents")
        conn.commit()
        conn.close()
        
        # Limpa banco vetorial
        if self.chroma_client and self.collection:
            try:
                self.chroma_client.delete_collection("document_chunks")
                self.collection = self.chroma_client.get_or_create_collection(
                    name="document_chunks",
                    metadata={"description": "Chunks de documentos para busca semântica"}
                )
            except Exception as e:
                logger.warning(f"Erro ao limpar banco vetorial: {e}")
        
        logger.info("Base de conhecimento limpa com sucesso")


# Função utilitária para instalar dependências
def install_dependencies():
    """Instala as dependências necessárias"""
    import subprocess
    import sys
    
    packages = [
        "PyPDF2",
        "python-docx", 
        "chromadb",
        "ollama"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} instalado com sucesso")
        except subprocess.CalledProcessError:
            print(f"✗ Erro ao instalar {package}")


if __name__ == "__main__":
    # Teste básico
    processor = DocumentProcessor()
    print("Sistema de processamento de documentos inicializado")
    print("Estatísticas:", processor.get_document_stats())

