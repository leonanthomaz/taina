# app/api/api.py
import wikipedia
import webbrowser
from translatepy import Translator
import yt_dlp
import openai
import os
import logging
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

class APIHandler:
    def __init__(self):
        wikipedia.set_lang('pt')
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
    
    def chat_with_gpt(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            logging.error(f"Erro ao se comunicar com o ChatGPT: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."

    def fetch_wikipedia_info(self, query):
        """
        Busca informações na Wikipedia.
        """
        try:
            return wikipedia.summary(query, sentences=2)
        except wikipedia.exceptions.DisambiguationError:
            return f"Há várias opções para '{query}'. Pode ser mais específico?"
        except wikipedia.exceptions.PageError:
            return f"Não encontrei informações sobre '{query}'."
        except Exception as e:
            print(f"Erro na Wikipedia: {e}")
            return "Desculpe, houve um problema com a Wikipedia."

    def play_music(song_name):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'extractaudio': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
                url = info['entries'][0]['webpage_url']
                webbrowser.open(url)
                return f"Reproduzindo {song_name} no YouTube."
        except Exception as e:
            logging.error(f"Erro ao tentar reproduzir música: {e}")
            return "Desculpe, não consegui reproduzir a música."


    def google_search(query):
        """
        Realiza pesquisa no Google.
        """
        try:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Buscando por: {query}"
        except Exception as e:
            print(f"Erro ao pesquisar no Google: {e}")
            return "Desculpe, houve um problema ao abrir o navegador."

    def translate(text, target_language='en'):
        """
        Traduz texto para o idioma alvo.
        """
        translator = Translator()
        try:
            translated = translator.translate(text, destination_language=target_language)
            return translated.result
        except Exception as e:
            print(f"Erro na tradução: {e}")
            return "Desculpe, ocorreu um problema na tradução."
