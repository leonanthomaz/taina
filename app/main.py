# app/main.py
from app.system_controller import SystemController

def main():
    controller = SystemController()  # Instanciar o controlador do sistema
    controller.start()  # Iniciar o sistema
