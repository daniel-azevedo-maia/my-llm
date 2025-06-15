# Pesquisa sobre LLMs Open Source

## Principais LLMs Open Source Identificadas

### 1. Llama 3.1 (Meta) - ESCOLHIDA
- **Parâmetros**: 8B, 70B, 405B
- **Contexto**: 128.000 tokens
- **Idiomas**: Português, Inglês, Espanhol, Alemão, Francês, Italiano, Hindi, Thai
- **Vantagens**: 
  - Mais moderna (lançada em julho 2024)
  - Suporte nativo ao português
  - Excelente performance
  - Fácil instalação via Ollama
  - Comunidade ativa
- **Instalação**: Via Ollama (ollama pull llama3.1)
- **Requisitos**: Python 3.7+, 8GB+ RAM para modelo 8B

### 2. BLOOM
- **Parâmetros**: 176B
- **Idiomas**: 46 idiomas incluindo português
- **Vantagens**: Muito transparente, colaborativo
- **Desvantagens**: Mais pesado, menos otimizado

### 3. BERT
- **Tipo**: Encoder-only (não ideal para geração)
- **Uso**: Melhor para análise, não para chat

### 4. Falcon 180B
- **Parâmetros**: 180B
- **Desvantagens**: Muito pesado para uso local

## Decisão: Llama 3.1 8B via Ollama

**Justificativa**:
1. Melhor balance entre performance e recursos
2. Suporte nativo ao português
3. Instalação simplificada via Ollama
4. Comunidade ativa e documentação excelente
5. Modelo 8B roda bem em hardware comum (8-16GB RAM)

## Arquitetura do Sistema

### Componentes Principais:
1. **LLM**: Llama 3.1 8B via Ollama
2. **Processamento de Documentos**: PyPDF2, python-docx, embeddings
3. **Base de Conhecimento**: ChromaDB (vetorial local)
4. **Interface**: Tkinter (nativo Python)
5. **Persistência**: SQLite + arquivos locais

