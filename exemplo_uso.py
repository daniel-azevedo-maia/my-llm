"""
Arquivo de Exemplo e Demonstração
Este arquivo mostra como usar o Sistema LLM Local programaticamente
"""

from document_processor import DocumentProcessor
from llm_system import LocalLLM, LLMTrainer

def exemplo_basico():
    """Exemplo básico de uso do sistema"""
    print("🤖 Exemplo de Uso do Sistema LLM Local")
    print("=" * 40)
    
    # Inicializa sistema
    print("1. Inicializando sistema...")
    llm = LocalLLM()
    trainer = LLMTrainer(llm)
    
    # Adiciona documento
    print("2. Adicionando documento de teste...")
    success = trainer.train_with_document("documento_teste.txt")
    print(f"   Resultado: {'✅ Sucesso' if success else '❌ Falha'}")
    
    # Mostra estatísticas
    print("3. Estatísticas do conhecimento:")
    stats = llm.get_knowledge_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Simula perguntas (sem Ollama rodando, apenas mostra estrutura)
    print("4. Exemplos de perguntas que funcionariam:")
    perguntas = [
        "Qual é o tema principal do documento?",
        "Como usar o sistema?",
        "Quais formatos são suportados?",
        "Resuma as características principais"
    ]
    
    for pergunta in perguntas:
        print(f"   👤 {pergunta}")
        # Aqui seria: resposta = llm.generate_response(pergunta)
        print(f"   🤖 [Resposta seria gerada aqui com Ollama rodando]")
        print()

def exemplo_processamento_documentos():
    """Exemplo de processamento de múltiplos documentos"""
    print("\n📚 Exemplo de Processamento de Documentos")
    print("=" * 45)
    
    processor = DocumentProcessor("exemplo_kb")
    
    # Lista de documentos exemplo
    documentos = ["documento_teste.txt"]
    
    for doc in documentos:
        print(f"Processando: {doc}")
        
        def callback(msg):
            print(f"  📝 {msg}")
        
        success = processor.process_document(doc, callback)
        print(f"  {'✅' if success else '❌'} Resultado: {success}")
    
    # Testa busca
    print("\n🔍 Testando busca:")
    resultados = processor.search_knowledge("sistema LLM")
    
    for i, resultado in enumerate(resultados[:2]):  # Mostra apenas 2
        print(f"  Resultado {i+1}:")
        print(f"    Arquivo: {resultado['filename']}")
        print(f"    Relevância: {resultado['relevance_score']:.2f}")
        print(f"    Trecho: {resultado['content'][:100]}...")
        print()

def exemplo_interface_programatica():
    """Exemplo de como usar sem interface gráfica"""
    print("\n💻 Exemplo de Uso Programático")
    print("=" * 35)
    
    # Código que o usuário poderia usar
    codigo_exemplo = '''
# Importa o sistema
from llm_system import LocalLLM

# Inicializa
llm = LocalLLM()

# Configura sistema (primeira vez)
llm.setup_system()

# Adiciona documento
llm.add_document("meu_documento.pdf")

# Faz pergunta
resposta = llm.generate_response("Qual é o tema principal?")
print(resposta)

# Limpa conhecimento se necessário
llm.clear_knowledge()
'''
    
    print("Código de exemplo:")
    print(codigo_exemplo)

if __name__ == "__main__":
    try:
        exemplo_basico()
        exemplo_processamento_documentos()
        exemplo_interface_programatica()
        
        print("\n🎉 Todos os exemplos executados com sucesso!")
        print("\nPara usar com interface gráfica, execute: python main.py")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        print("Verifique se todas as dependências estão instaladas.")

