# app/engine/engine.py
import os
import pygame
from gtts import gTTS
import time
import speech_recognition as sr
from app.api import APIHandler
from app.utils import engine_check
import logging

logging.basicConfig(level=logging.INFO)

class Engine:
    def __init__(self, name, user_name):
        self.name = name
        self.user_name = user_name
        self.api_handler = APIHandler()
        pygame.mixer.init()
        logging.info("Engine inicializado com o nome da assistente: %s e nome do usuário: %s", self.name, self.user_name)

        # Cria a pasta temp na raiz do projeto, se não existir
        self.temp_folder = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

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
        if user_input:
            user_input = user_input.lower()

            if engine_check(["ajuda", "socorro"], user_input):
                self.engine_speak("Como posso ajudar?")
            elif engine_check(["tempo", "clima"], user_input):
                self.engine_speak("Desculpe, não consigo acessar dados do tempo.")
            elif engine_check(["sair", "desligar"], user_input):
                self.engine_speak("Encerrando o sistema. Até mais!")
                logging.info("Sistema sendo encerrado")
                pygame.quit()
                exit()

            elif "pesquisa" in user_input:
                query = user_input.replace("pesquisa", "").strip()
                result = self.api_handler.fetch_wikipedia_info(query)
                logging.info("Resultado da busca na Wikipedia: %s", result)
                self.engine_speak(result)

            elif "traduz" in user_input:
                text_to_translate = user_input.replace("traduz", "").strip()
                translated_text = self.api_handler.translate(text_to_translate)
                logging.info("Resultado da tradução: %s", translated_text)
                self.engine_speak(f"A tradução é: {translated_text}")

            elif "toca" in user_input:
                song_name = user_input.replace("toca", "").strip()
                music_message = self.api_handler.play_music(song_name)
                logging.info("Música encontrada: %s", music_message)
                self.engine_speak(music_message)

            else:
                self.engine_speak(f"Você disse: {user_input}")

            logging.info("Aguardando próxima entrada do usuário...")
