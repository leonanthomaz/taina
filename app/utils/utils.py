# app/utils/utils.py
import logging
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

def engine_check(keywords, prompt):
    prompt = prompt.lower().strip()  # Remover espaços extras e converter para minúsculas
    for keyword in keywords:
        if keyword in prompt:
            logging.info(f"Encontrado termo chave: {keyword} na entrada: {prompt}")
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
