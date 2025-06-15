"""
Interface Gráfica do Sistema LLM Local
Interface principal usando Tkinter para interação com o usuário
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
from typing import List, Optional
import webbrowser
from llm_system import LocalLLM, LLMTrainer

class ProgressWindow:
    """Janela de progresso com mensagens motivacionais"""
    
    def __init__(self, parent, title="Processando..."):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centraliza a janela
        self.window.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label de status
        self.status_label = ttk.Label(main_frame, text="Iniciando...", font=("Arial", 10))
        self.status_label.pack(pady=(0, 10))
        
        # Barra de progresso indeterminada
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        self.progress.start()
        
        # Botão cancelar (opcional)
        self.cancel_button = ttk.Button(main_frame, text="Cancelar", command=self.cancel)
        self.cancel_button.pack()
        
        self.cancelled = False
    
    def update_status(self, message: str):
        """Atualiza mensagem de status"""
        self.status_label.config(text=message)
        self.window.update()
    
    def cancel(self):
        """Cancela operação"""
        self.cancelled = True
        self.close()
    
    def close(self):
        """Fecha janela de progresso"""
        self.progress.stop()
        self.window.destroy()


class ChatInterface:
    """Interface de chat com histórico"""
    
    def __init__(self, parent, llm_system):
        self.parent = parent
        self.llm = llm_system
        self.setup_ui()

    
    def setup_ui(self):
        """Configura interface do chat"""
        # Frame principal do chat
        chat_frame = ttk.LabelFrame(self.parent, text="💬 Chat com IA", padding="10")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Área de conversa
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            height=15, 
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configurar tags para formatação
        self.chat_display.tag_config("user", foreground="blue", font=("Arial", 10, "bold"))
        self.chat_display.tag_config("assistant", foreground="green", font=("Arial", 10))
        self.chat_display.tag_config("system", foreground="gray", font=("Arial", 9, "italic"))
        
        # Frame para entrada
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)
        
        # Campo de entrada
        self.message_entry = tk.Text(input_frame, height=3, wrap=tk.WORD, font=("Arial", 10))
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Botão enviar
        self.send_button = ttk.Button(input_frame, text="Enviar", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind Enter para enviar
        self.message_entry.bind("<Control-Return>", lambda e: self.send_message())
        
        # Frame para botões de ação
        action_frame = ttk.Frame(chat_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="Limpar Chat", command=self.clear_chat).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="Copiar Última Resposta", command=self.copy_last_response).pack(side=tk.LEFT, padx=(10, 0))
        
        self.last_response = ""
    
    def add_message(self, sender: str, message: str, tag: str = None):
        """Adiciona mensagem ao chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Adiciona timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        if sender == "Você":
            self.chat_display.insert(tk.END, f"[{timestamp}] {sender}: ", "user")
        elif sender == "IA":
            self.chat_display.insert(tk.END, f"[{timestamp}] {sender}: ", "assistant")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] {sender}: ", "system")
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        if sender == "IA":
            self.last_response = message
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        """Envia mensagem para a IA"""
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
        
        # Limpa campo de entrada
        self.message_entry.delete("1.0", tk.END)
        
        # Adiciona mensagem do usuário
        self.add_message("Você", message)
        
        # Desabilita botão durante processamento
        self.send_button.config(state=tk.DISABLED, text="Pensando...")
        
        # Callback para processar resposta
        def process_response():
            try:
                # Aqui seria chamada a função da IA
                # Por enquanto, resposta simulada
                response = self.llm.generate_response(message)
                
                # Adiciona resposta da IA
                self.parent.after(0, lambda: self.add_message("IA", response))
            except Exception as e:
                self.parent.after(0, lambda e=e: self.add_message("Sistema", f"Erro: {str(e)}"))

            finally:
                # Reabilita botão
                self.parent.after(0, lambda: self.send_button.config(state=tk.NORMAL, text="Enviar"))
        
        # Executa em thread separada
        threading.Thread(target=process_response, daemon=True).start()
    
    def clear_chat(self):
        """Limpa histórico do chat"""
        if messagebox.askyesno("Confirmar", "Deseja limpar todo o histórico do chat?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.last_response = ""
    
    def copy_last_response(self):
        """Copia última resposta para clipboard"""
        if self.last_response:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(self.last_response)
            messagebox.showinfo("Sucesso", "Resposta copiada para a área de transferência!")
        else:
            messagebox.showwarning("Aviso", "Nenhuma resposta para copiar.")


class DocumentManager:
    """Gerenciador de documentos com upload e progresso"""
    
    def __init__(self, parent, llm_system):
        self.parent = parent
        self.llm_system = llm_system
        self.trainer = LLMTrainer(llm_system)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura interface de gerenciamento de documentos"""
        # Frame principal
        doc_frame = ttk.LabelFrame(self.parent, text="📚 Gerenciamento de Documentos", padding="10")
        doc_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para botões
        button_frame = ttk.Frame(doc_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botões de ação
        ttk.Button(button_frame, text="📁 Adicionar Documentos", 
                  command=self.add_documents).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📊 Ver Estatísticas", 
                  command=self.show_stats).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🗑️ Recomeçar do Zero", 
                  command=self.reset_knowledge).pack(side=tk.LEFT, padx=(0, 10))
        
        # Área de status
        self.status_text = scrolledtext.ScrolledText(doc_frame, height=6, wrap=tk.WORD, 
                                                   font=("Arial", 9), state=tk.DISABLED)
        self.status_text.pack(fill=tk.X)
        
        self.add_status("Sistema iniciado. Pronto para receber documentos!")
    
    def add_status(self, message: str):
        """Adiciona mensagem ao status"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.config(state=tk.DISABLED)
        self.status_text.see(tk.END)
    
    def add_documents(self):
        """Adiciona documentos à base de conhecimento"""
        file_types = [
            ("Todos os suportados", "*.pdf;*.docx;*.txt"),
            ("PDF", "*.pdf"),
            ("Word", "*.docx"),
            ("Texto", "*.txt"),
            ("Todos os arquivos", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Selecione os documentos para adicionar",
            filetypes=file_types
        )
        
        if not files:
            return
        
        # Processa arquivos em thread separada
        def process_files():
            progress_window = ProgressWindow(self.parent, "Aprendendo com documentos...")
            
            try:
                for i, file_path in enumerate(files):
                    filename = os.path.basename(file_path)
                    
                    def progress_callback(message):
                        progress_window.update_status(f"[{i+1}/{len(files)}] {filename}: {message}")
                    
                    self.parent.after(0, lambda f=filename: self.add_status(f"Processando: {f}"))
                    
                    success = self.trainer.train_with_document(file_path, progress_callback)
                    
                    if success:
                        self.parent.after(0, lambda f=filename: self.add_status(f"✅ {f} processado com sucesso!"))
                    else:
                        self.parent.after(0, lambda f=filename: self.add_status(f"❌ Erro ao processar {f}"))
                
                progress_window.update_status("🎉 Todos os documentos foram processados!")
                self.parent.after(2000, progress_window.close)
                
            except Exception as e:
                progress_window.update_status(f"Erro: {str(e)}")
                self.parent.after(3000, progress_window.close)
        
        threading.Thread(target=process_files, daemon=True).start()
    
    def show_stats(self):
        """Mostra estatísticas da base de conhecimento"""
        try:
            stats = self.llm_system.get_knowledge_stats()
            
            message = f"""📊 Estatísticas da Base de Conhecimento:

📄 Total de documentos: {stats['total_documents']}
📝 Total de chunks: {stats['total_chunks']}

📁 Tipos de arquivo:"""
            
            for file_type, count in stats.get('file_types', {}).items():
                message += f"\n  • {file_type}: {count} arquivo(s)"
            
            if stats['total_documents'] == 0:
                message += "\n\n💡 Dica: Adicione alguns documentos para começar a conversar!"
            
            messagebox.showinfo("Estatísticas", message)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter estatísticas: {str(e)}")
    
    def reset_knowledge(self):
        """Reseta toda a base de conhecimento"""
        result = messagebox.askyesnocancel(
            "⚠️ Confirmar Reset",
            "Deseja deletar toda a base de conhecimento?\n\n"
            "⚠️ Esta operação NÃO pode ser desfeita!\n\n"
            "Todos os documentos processados serão removidos e você precisará "
            "adicioná-los novamente."
        )
        
        if result:  # Yes
            try:
                self.llm_system.clear_knowledge()
                self.add_status("🗑️ Base de conhecimento limpa com sucesso!")
                messagebox.showinfo("Sucesso", "Base de conhecimento resetada!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao resetar: {str(e)}")


class MainApplication:
    """Aplicação principal"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Sistema LLM Local - Chat Inteligente")
        self.root.geometry("900x700")
        
        # Configura ícone (se disponível)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Inicializa sistema LLM
        self.llm = LocalLLM()
        self.setup_system()
        
        # Configura interface
        self.setup_ui()
        
        # Configura fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_system(self):
        """Configura sistema LLM em background"""
        def setup():
            try:
                # Verifica se sistema já está configurado
                if not self.llm.is_server_running():
                    progress_window = ProgressWindow(self.root, "Configurando Sistema...")
                    
                    def progress_callback(message):
                        progress_window.update_status(message)
                    
                    success = self.llm.setup_system(progress_callback)
                    
                    if success:
                        progress_window.update_status("✅ Sistema configurado com sucesso!")
                        self.root.after(2000, progress_window.close)
                    else:
                        progress_window.update_status("❌ Erro na configuração")
                        self.root.after(3000, progress_window.close)
                        
            except Exception as e:
                messagebox.showerror("Erro", f"Erro na configuração: {str(e)}")
        
        # Executa configuração em thread separada
        threading.Thread(target=setup, daemon=True).start()
    
    def setup_ui(self):
        """Configura interface principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🤖 Sistema LLM Local", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, 
                                  text="Converse com seus documentos usando IA local e gratuita",
                                  font=("Arial", 10))
        subtitle_label.pack(pady=(0, 20))
        
        # Gerenciador de documentos
        self.doc_manager = DocumentManager(main_frame, self.llm)
        
        # Interface de chat
        self.chat_interface = ChatInterface(main_frame, self.llm)
        
        # Frame para informações
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = ("💡 Dica: Adicione documentos PDF, DOCX ou TXT e depois faça perguntas sobre eles! "
                    "Use Ctrl+Enter para enviar mensagens.")
        ttk.Label(info_frame, text=info_text, font=("Arial", 9), 
                 foreground="gray", wraplength=800).pack()
        
        # Menu
        self.setup_menu()
    
    def setup_menu(self):
        """Configura menu da aplicação"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Adicionar Documentos", command=self.doc_manager.add_documents)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.on_closing)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="Estatísticas", command=self.doc_manager.show_stats)
        tools_menu.add_command(label="Limpar Chat", command=self.chat_interface.clear_chat)
        tools_menu.add_command(label="Resetar Conhecimento", command=self.doc_manager.reset_knowledge)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Como usar", command=self.show_help)
        help_menu.add_command(label="Sobre", command=self.show_about)
    
    def show_help(self):
        """Mostra ajuda"""
        help_text = """🤖 Como usar o Sistema LLM Local:

1. 📁 Adicionar Documentos:
   • Clique em "Adicionar Documentos"
   • Selecione arquivos PDF, DOCX ou TXT
   • Aguarde o processamento (aparecerá "Obrigado! Já aprendi tudo!")

2. 💬 Conversar:
   • Digite sua pergunta na caixa de texto
   • Clique "Enviar" ou use Ctrl+Enter
   • A IA responderá baseada nos documentos

3. 🔧 Gerenciar:
   • "Ver Estatísticas": mostra quantos documentos foram processados
   • "Recomeçar do Zero": apaga toda a base de conhecimento
   • "Limpar Chat": limpa apenas o histórico da conversa

4. 💡 Dicas:
   • Faça perguntas específicas sobre o conteúdo dos documentos
   • A IA citará a fonte quando possível
   • Use "Copiar Última Resposta" para copiar respostas longas"""
        
        messagebox.showinfo("Como usar", help_text)
    
    def show_about(self):
        """Mostra informações sobre o sistema"""
        about_text = """🤖 Sistema LLM Local v1.0

Desenvolvido com:
• Python + Tkinter (Interface)
• Ollama + Llama 3.1 (IA)
• ChromaDB (Busca semântica)
• PyPDF2, python-docx (Processamento)

Características:
✅ 100% Local e Offline
✅ Gratuito e Open Source  
✅ Suporte ao Português
✅ Persistência de dados
✅ Interface amigável

Criado para aprender com seus documentos
e responder perguntas de forma inteligente!"""
        
        messagebox.showinfo("Sobre", about_text)
    
    def on_closing(self):
        """Trata fechamento da aplicação"""
        if messagebox.askokcancel("Sair", "Deseja fechar o sistema?"):
            self.root.destroy()
    
    def run(self):
        """Executa aplicação"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainApplication()
    app.run()

