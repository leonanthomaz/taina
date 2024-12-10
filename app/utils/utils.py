# app/utils/utils.py
import time
import re

def get_greeting():
    """
    Saudação baseada no horário
    """
    current_hour = int(time.strftime('%H'))

    if 6 <= current_hour < 12:
        return 'Bom dia'
    elif 12 <= current_hour < 18:
        return 'Boa tarde'
    else:
        return 'Boa noite'

def engine_check(terms, voice_data):
    """
    Função para identificar se o termo existe na fala do usuário
    """
    for term in terms:
        if term in voice_data:
            return True
    return False

def extract_domain(url):
    """
    Extrai o domínio de uma URL.
    """
    pattern = r"www\.(.*?)\.com"
    matches = re.findall(pattern, url)
    if matches:
        return matches[0]
    else:
        return url
