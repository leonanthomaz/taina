# app/assistant/assistant.py
from app.engine import Engine
from dotenv import load_dotenv
import os
from app.utils import get_greeting

load_dotenv()

class Assistant:
    def __init__(self):
        self.assistant_name = os.getenv("ASSISTANT_NAME", "Tainá")
        self.user_name = os.getenv("USER_NAME", "Leonan")
        self.engine = Engine(self.assistant_name, self.user_name)  # Instancia o Engine
        self.greeting_done = False  # Flag para controlar se a saudação foi feita

    def run(self):
        while True:  # A loop continuará até a flag should_stop ser True
            if not self.greeting_done:  # Se ainda não fez a saudação
                greeting = get_greeting()  # Saudação inicial
                self.engine.engine_speak(f"{greeting}, {self.user_name}. Me chamo {self.assistant_name}! Aguarde um momento.")
                self.greeting_done = True  # Marca que a saudação foi feita
            else:
                
                user_input = self.engine.engine_record_audio(f"Pode dar o comando, {self.user_name}!")
                
                if user_input:
                    print(f"Entrada recebida: {user_input}")
                    # Responder ao usuário
                    self.engine.engine_response(user_input)
                
                else:
                    print("Nada foi reconhecido.")

