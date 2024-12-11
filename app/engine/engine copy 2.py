# app/engine/engine.py
import os
import random
import pygame
from gtts import gTTS
import time
import speech_recognition as sr
from app.api import APIHandler
import logging
from app.utils import engine_check

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

    def engine_response(self, prompt):
        """
        Responde à entrada de voz com base nas palavras-chave detectadas.
        """
        actions = {
            'saudacao': {
                'keywords': ['bom dia', 'boa tarde', 'boa noite', 'oi', 'olá', 'hello'],
                'responses': [
                    f'Fala {self.user_name}, tranquilo?',
                    f'Beleza, {self.user_name}? Como você está hoje?',
                    f'De boinha, {self.user_name}?',
                    f'Oi chefe {self.user_name}! Bom te ver de novo!',
                    f'Olá {self.user_name}! Estou disponível!',
                    f'Como vai, senhor? Tem algo que eu possa fazer?',
                ]
            },
            'estado': {
                'keywords': ['tô', 'estou'],
                'responses': {
                    'boa': 'Que beleza, senhor! Aguarde um instante...',
                    'bem': 'Que bom chefe! Vamos em frente! Aguarde um instante...',
                    'mal': 'Relaxa senhor, vai melhorar... Vamos prosseguir? Aguarde um instante...',
                    'pensando': 'Ok, estou aguardando...'
                }
            },
            'parar': {
                'keywords': ['parar', 'pausar', 'encerrar', 'fechar', 'acabar'],
                'responses': ['Certo, senhor...']
            },
            'continuar': {
                'keywords': ['quero continuar', 'continue', 'prossiga', 'vamos continuar'],
                'responses': ['Ok, senhor. Vamos continuar...']
            },
            'continuar_conversa': {
                'keywords': ['vamos continuar'],
                'responses': ['Pode falar, chefe...']
            },
            'desligar': {
                'keywords': ['sair', 'desligar', 'finalizar', 'cala a boca', 'ja deu', 'pode dormir'],
                'responses': ['Desligando o sistema...'],
            },
            'tocar_musica': {
                'keywords': ['toque', 'pedrada', 'hino'],
                'action': lambda song: self.api_handler.play_music(song)
            },
            'acessar_site': {
                'keywords': ['site'],
                'action': lambda site: self.api_handler.webbrowser.get().open(f'https://www.{"-".join(site.split())}.com')
            },
            'pesquisa_youtube': {
                'keywords': ['youtube', 'YouTube'],
                'action': lambda video: self.api_handler.youtube_search(prompt.split('youtube')[-1])
            },
            'pesquisa_google': {
                'keywords': ['google', 'Google'],
                'action': lambda search: self.api_handler.google_search(search)
            },
            'pesquisa_wikipedia': {
                'keywords': ['wikipedia', 'Wikipédia'],
                'action': lambda word: self.api_handler.wikipedia_search(word)
            },
            'traducao': {
                'keywords': ['traduza'],
                'action': lambda phrase: self.api_handler.translate(phrase)
            }
        }

        for action, data in actions.items():
            if engine_check(data['keywords'], prompt):
                if 'responses' in data:
                    if isinstance(data['responses'], list):
                        response = random.choice(data['responses'])
                    else:
                        state_response = prompt.split(data['keywords'][0])[1].strip().lower()
                        response = data['responses'].get(state_response, 'Desculpe, não entendi.')
                    self.engine_speak(response)
                if 'action' in data:
                    if not self.actions:
                        term = prompt.split(data['keywords'][-1])[-1].strip()  # Obtém o texto após o último keyword
                        self.engine_speak(data['action'](term))
                        self.actions = True
                    else:
                        self.engine_speak('Limpando dados de pesquisa...')
                        data.clear()
                        self.actions = False
                        return
                if action == 'saudacao':
                    self.greeting_exists = True
                if action == 'desligar':
                    logging.info("Sistema sendo encerrado")
                    pygame.quit()
                    exit()
                break

            logging.info("Aguardando próxima entrada do usuário...")
