# app/system_controller.py
from app.assistant import Assistant
from dotenv import load_dotenv

class SystemController:
    def __init__(self):
        load_dotenv()  # Carregar variáveis de ambiente
        self.assistant = Assistant()  # Instanciar a assistente

    def start(self):
        print("Sistema iniciado. Bem-vindo!")
        try:
            self.assistant.run()  # Delegar o loop principal para a assistente
        except KeyboardInterrupt:
            print("Sistema interrompido.")
            self.assistant.stop()  # Encerra o loop caso o sistema seja interrompido
        
    def stop(self):
        # Chama o método stop da Assistente, que interromperá o loop
        print("Parando a assistente...")
        self.assistant.stop()  # Parar a execução do loop da assistente