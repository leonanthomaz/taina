# app/engine/engine.py
import os
import random
import pygame
from gtts import gTTS
import time
import speech_recognition as sr
from app.api import APIHandler
from app.utils import engine_check
import logging
import json
import sys

# Configuração de logging com UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
    encoding='utf-8'
)

# Verifica se o terminal suporta UTF-8
if sys.stdout.encoding.lower() != 'utf-8':
    print("Aviso: O terminal pode não suportar UTF-8. Verifique sua configuração.")


class Engine:
    def __init__(self, name, user_name):
        self.name = name
        self.user_name = user_name
        self.api_handler = APIHandler()
        pygame.mixer.init()
        logging.info("Engine inicializado com o nome da assistente: %s e nome do usuário: %s", self.name, self.user_name)
        self.responses = self.load_responses()

        # Cria a pasta temp na raiz do projeto, se não existir
        self.temp_folder = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)
    
    def load_responses(self):
        try:
            with open('app/engine/keywords.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Erro ao carregar respostas do JSON: {e}")
            return {}

    def engine_speak(self, text):
        logging.info("Iniciando engine_speak com o texto: %s", text)

        # Tenta inicializar o pygame mixer se não estiver já inicializado
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                logging.info("pygame.mixer inicializado.")
        except pygame.error as e:
            logging.error("Falha ao inicializar o pygame mixer: %s", e)
            return

        # Salva o arquivo de áudio temporário na pasta temp do projeto
        temp_audio_path = os.path.join(self.temp_folder, f"temp_{int(time.time())}.mp3")
        
        try:
            tts = gTTS(text=text, lang='pt', slow=False)
            tts.save(temp_audio_path)
            logging.info("Arquivo de áudio criado em: %s", temp_audio_path)

            pygame.mixer.music.load(temp_audio_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

        finally:
            # Quando o áudio terminar, pare o mixer corretamente
            pygame.mixer.music.stop()
            pygame.mixer.quit()

            try:
                # Verifica se o arquivo existe antes de tentar excluir
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                    logging.info("Arquivo de áudio temporário removido: %s", temp_audio_path)
            except Exception as e:
                logging.error("Erro ao tentar remover o arquivo de áudio temporário: %s", e)

    def engine_record_audio(self, prompt):
        logging.info("Iniciando engine_record_audio com o prompt: %s", prompt)
        self.engine_speak(prompt)
        recognizer = sr.Recognizer()

        with sr.Microphone(device_index=0) as source:
            logging.info("Ajustando ambiente do microfone...")
            recognizer.adjust_for_ambient_noise(source, duration=2)

            logging.info("Esperando entrada do usuário...")
            print("Dispositivos de entrada disponíveis:", sr.Microphone.list_microphone_names())

            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Aumentei o timeout e o limite de tempo
                logging.info("Áudio capturado com sucesso")
                return recognizer.recognize_google(audio, language="pt-BR")
            except sr.WaitTimeoutError:
                logging.warning("Tempo esgotado para captura de áudio")
            except sr.UnknownValueError:
                logging.warning("Não foi possível entender o áudio")
            except sr.RequestError as e:
                logging.error("Erro no serviço de reconhecimento de fala: %s", e)
        return None

    def engine_response(self, user_input):
        logging.info("Processando entrada do usuário: %s", user_input)
        user_input = user_input.lower()
        
        # Busca por palavras-chave no JSON
        for category, entries in self.responses.items():
            for entry in entries:
                if any(keyword in user_input for keyword in entry['keywords']):
                    response = random.choice(entry['responses'])
                    self.engine_speak(response)
                    return

        # Integração com funcionalidades adicionais
        if "toca" in user_input:
            song_name = user_input.replace("toca", "").strip()
            response = self.api_handler.play_music(song_name)
            self.engine_speak(response)
            return

        if "pesquisa" in user_input:
            query = user_input.replace("pesquisa", "").strip()
            response = self.api_handler.google_search(query)
            self.engine_speak(response)
            return

        if "traduz" in user_input:
            text_to_translate = user_input.replace("traduz", "").strip()
            response = self.api_handler.translate(text_to_translate)
            self.engine_speak(f"Tradução: {response}")
            return

        if "wikipedia" in user_input:
            query = user_input.replace("wikipedia", "").strip()
            response = self.api_handler.fetch_wikipedia_info(query)
            self.engine_speak(response)
            return
        
        # Se não encontrar palavras-chave, usa ChatGPT
        chatgpt_response = self.api_handler.chat_with_gpt(user_input)
        self.engine_speak(chatgpt_response)
