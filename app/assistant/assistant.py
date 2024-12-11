# app/assistant/assistant.py
from app.engine import Engine
from app.api import APIHandler
from dotenv import load_dotenv
import os
from app.utils import get_greeting

load_dotenv()

class Assistant:
    def __init__(self):
        self.assistant_name = os.getenv("ASSISTANT_NAME", "Tainá")
        self.user_name = os.getenv("USER_NAME", "Leonan")
        self.engine = Engine(self.assistant_name, self.user_name)  # Instancia o Engine
        self.api_handler = APIHandler()  # Instancia o APIHandler
        self.greeting_done = False  # Flag para controlar se a saudação foi feita
        self.should_stop = False  # Flag para controle de parada

    def run(self):
        while not self.should_stop:  # A loop continuará até a flag should_stop ser True
            if not self.greeting_done:  # Se ainda não fez a saudação
                greeting = get_greeting()  # Saudação inicial
                self.engine.engine_speak(f"{greeting}, {self.user_name}. Me chamo {self.assistant_name}! Como posso ajudar?")
                self.greeting_done = True  # Marca que a saudação foi feita
            else:
                # Pergunta contínua após a saudação
                user_input = self.engine.engine_record_audio(f"Pode falar.")
                
                if user_input:
                    print(f"Entrada recebida: {user_input}")
                    # Responder ao usuário
                    self.engine.engine_response(user_input)
                    
                    # Se o comando for para sair, marque a flag de parada
                    if "sair" in user_input or "desligar" in user_input:
                        self.stop()  # Método para parar o loop

                else:
                    print("Nada foi reconhecido.")

    def stop(self):
        self.should_stop = True  # Muda a flag para parar o loop
