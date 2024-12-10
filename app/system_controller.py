from app.assistant import Assistant
from dotenv import load_dotenv

class SystemController:
    def __init__(self):
        load_dotenv()  # Carregar variáveis de ambiente
        self.assistant = Assistant()  # Instanciar a assistente

    def start(self):
        print("Sistema iniciado. Bem-vindo!")
        self.assistant.run()  # Delegar o loop principal para a assistente
