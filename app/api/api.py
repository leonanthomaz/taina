# app/api/api.py
import wikipedia
import webbrowser
from translatepy import Translator
import yt_dlp
import logging
from dotenv import load_dotenv
import openai
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
logging.info(f"CHAVE CHATGPT: {openai.api_key}")

class APIHandler:
    def __init__(self):
        wikipedia.set_lang('pt')
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
        
    def chat_with_gpt(self, prompt):
        try:
            response = openai.completions.create(
                model="gpt-4",  # Ou qualquer modelo que você queira usar
                prompt=prompt,  # Passando o prompt diretamente
                max_tokens=150
            )
            logging.info(f"RESPOSTA CHATGPT: {response}")
            return response['choices'][0]['text'].strip()  # Acessando a resposta correta
        except Exception as e:
            logging.error(f"Erro ao se comunicar com o ChatGPT: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."
    
    def fetch_wikipedia_info(self, query):
        try:
            response = wikipedia.summary(query, sentences=2)
            logging.info(f"RESPOSTA WIKIPEDIA: {response}")
            return response
        except wikipedia.exceptions.DisambiguationError:
            return f"Há várias opções para '{query}'. Pode ser mais específico?"
        except wikipedia.exceptions.PageError:
            return f"Não encontrei informações sobre '{query}'."
        except Exception as e:
            logging.error(f"Erro na Wikipedia: {e}")
            return "Desculpe, houve um problema com a Wikipedia."

    def play_music(self, song_name):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
                url = info['entries'][0]['webpage_url']
                webbrowser.open(url)
                logging.info(f"MUSICA TOCANDO: {song_name}")
                return f"Tocando música: {song_name}"
        except Exception as e:
            logging.error(f"Erro ao reproduzir música: {e}")
            return "Desculpe, ocorreu um problema ao reproduzir a música."

    def google_search(self, query):
        try:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            logging.info(f"TERMO PESQUISADO: {query}")
            return f"Buscando por: {query}"
        except Exception as e:
            logging.error(f"Erro ao pesquisar no Google: {e}")
            return "Desculpe, houve um problema ao abrir o navegador."

    def translate(self, text):
        try:
            translator = Translator()
            translation = translator.translate(text, destination_language='pt')
            logging.info(f"TRADUÇÃO: {translation.result}")
            return translation.result
        except Exception as e:
            logging.error(f"Erro ao traduzir texto: {e}")
            return "Desculpe, houve um problema ao tentar traduzir o texto."
