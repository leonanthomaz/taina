# app/api/api.py
import wikipedia
import webbrowser
from translatepy import Translator
import yt_dlp

class APIHandler:
    def __init__(self):
        wikipedia.set_lang('pt')

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

    @staticmethod
    def play_music(song_name):
        """
        Reproduz música usando o YouTube.
        """
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
                return f"Tocando música: {song_name}"
        except Exception as e:
            print(f"Erro ao reproduzir música: {e}")
            return "Desculpe, ocorreu um problema ao reproduzir a música."

    @staticmethod
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

    @staticmethod
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
