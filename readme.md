# 🤖 Sistema LLM Local - Projeto Pessoal de Daniel Maia

Este é meu projeto pessoal de Inteligência Artificial Local, construído para estudar e experimentar a construção de sistemas de IA privados, que funcionem 100% offline, com alta performance e controle total dos dados.

---

## 📌 O que o projeto faz?

O sistema permite carregar documentos pessoais (PDF, DOCX, TXT) e, a partir deles, o sistema "aprende" seu conteúdo, criando uma **base de conhecimento vetorial**.\
Com isso, posso fazer perguntas em linguagem natural e o sistema responde baseado nesses documentos.

Ou seja, é um sistema privado de **Perguntas e Respostas sobre documentos pessoais** com IA local.

---

## 📌 É RAG? É Fine-Tuning?

Este projeto implementa um sistema de **RAG (Retrieval Augmented Generation)** e **não usa Fine-Tuning**.

- 🔎 **RAG (Busca + Geração)**\
  Ele não altera o modelo de linguagem. Ao invés disso, recupera trechos relevantes dos documentos (usando embeddings vetoriais) e os injeta como contexto no prompt enviado ao modelo.\
  Assim o modelo responde de forma contextualizada.

- 🧪 **Fine-tuning (não utilizado)**\
  Não realizo nenhum ajuste no modelo LLM. O modelo permanece intacto.

Esta abordagem (RAG) é altamente eficiente para sistemas de perguntas e respostas baseados em documentos.

---

## 📌 Tecnologias e bibliotecas utilizadas

| Biblioteca                           | Função                                                      |
| ------------------------------------ | ----------------------------------------------------------- |
| **Python 3.7+**                      | Linguagem principal                                         |
| **Tkinter**                          | Interface gráfica desktop                                   |
| **Ollama**                           | Servidor local que executa o LLM                            |
| **Llama 3.1 (8B)**                   | Modelo de linguagem (LLM)                                   |
| **ChromaDB**                         | Banco de dados vetorial local (armazenamento de embeddings) |
| **PyPDF2**                           | Leitura de arquivos PDF                                     |
| **python-docx**                      | Leitura de arquivos DOCX                                    |
| **requests**                         | Comunicação HTTP com o Ollama                               |
| **subprocess / logging / threading** | Controle de processos, logs e execução paralela             |

---

## 📌 Estrutura de armazenamento

| Tipo de dado             | Local de armazenamento                                      |
| ------------------------ | ----------------------------------------------------------- |
| Código fonte             | Pasta do projeto                                            |
| Dependências Python      | Diretório padrão do pip (`--user`)                          |
| Base vetorial ChromaDB   | Subpasta local do projeto (`/chroma_db/`)                   |
| Modelo Llama 3.1 baixado | Diretório interno do Ollama (`C:\Users\<usuario>\.ollama\`) |
| Logs e histórico de chat | Em memória (não persistido em disco)                        |

---

## 📌 Fluxo completo de instalação e execução (ORDEM EXATA)

### 1️⃣ Pré-requisitos manuais iniciais

**A. Instalar Python 3.7+**

- Acesse: [https://python.org/downloads](https://python.org/downloads)
- Instale o Python.
- Marque a opção "Add Python to PATH" durante a instalação.

**B. Instalar Ollama (Windows)**

- Acesse: [https://ollama.com/download](https://ollama.com/download)
- Baixe e instale o Ollama para Windows.
- Este passo instala o servidor Ollama local.

**C. (Opcional) Criar a pasta do projeto**

Exemplo:

```
C:\MeusProjetos\SISTEMA_LLM_LOCAL\
```

---

### 2️⃣ Executar o script de instalação automática `.bat`

Agora execute o arquivo `instalador.bat` incluído no projeto:

```bat
@echo off
REM Script de instalação para Windows
echo 🤖 Sistema LLM Local - Instalação Windows

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
```

Esse script:

- Instala as dependências Python
- Verifica o Ollama
- Faz o download do modelo com:

```bash
ollama pull llama3.1
```

O modelo fica armazenado localmente no cache do Ollama.

---

### 3️⃣ Rodar o sistema normalmente

Depois da instalação, para iniciar o sistema execute:

```bash
python main.py
```

O sistema:

- Detecta que tudo está instalado.
- Inicializa o servidor Ollama.
- Abre a interface gráfica (Tkinter).
- Já está pronto para uso.

---

### 4️⃣ (Opcional) Reexecutar o setup completo via terminal

Se desejar rodar o setup direto pelo próprio código:

```bash
python main.py --setup
```

---

## 📌 Como funciona o sistema

1️⃣ O usuário adiciona documentos (PDF, DOCX, TXT).

2️⃣ O sistema:

- Lê o conteúdo.
- Divide em "chunks" (trechos).
- Gera embeddings vetoriais.
- Armazena localmente via ChromaDB.

3️⃣ Quando uma pergunta é feita:

- Busca vetorial local (via ChromaDB) encontra trechos relevantes.
- O contexto é injetado no prompt.
- O prompt é enviado ao modelo Llama 3.1 no Ollama.
- A resposta é gerada e exibida.

---

## 📌 Por que este projeto não usa LangChain ou LlamaIndex?

- Toda a lógica de ingestão de documentos e fluxo RAG foi implementada manualmente, para maior controle e aprendizado.
- O projeto não depende de frameworks externos.
- 100% open-source, didático e transparente.

---

## 📌 Possíveis melhorias futuras

- Melhorar o splitting dos documentos (divisão semântica).
- Utilizar embeddings ainda mais modernos.
- Implementar threads de conversa com memória.
- Adicionar backup automático da base vetorial.
- Melhorar ainda mais a interface gráfica.

---

✅ **Projeto 100% funcional, local, privativo e controlado.**

Desenvolvido e mantido por:

**Daniel Maia**

---

