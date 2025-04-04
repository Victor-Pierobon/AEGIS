#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A.E.G.I.S. - AI-Enhanced Guidance System
Ponto de entrada principal para a aplicação AEGIS
"""

import os
import sys
import logging
from pathlib import Path
from config import Config
from gui import AEGISInterface

def setup_logging():
    """Configura sistema de logs"""
    # Cria diretório de logs se não existir
    log_dir = Config.LOGS_DIR
    os.makedirs(log_dir, exist_ok=True)
    
    # Configura formato de log
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'aegis.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Sistema de logs inicializado")

def check_directories():
    """Verifica e cria diretórios necessários"""
    dirs = [
        Config.ASSETS_DIR,
        Config.LOGS_DIR,
        Config.Voice.PIPER_DIR,
        Config.Voice.PIPER_MODELS_DIR
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Diretório verificado: {directory}")

def main():
    """Função principal"""
    print("Iniciando A.E.G.I.S. - AI-Enhanced Guidance System...")
    
    # Configura logs
    setup_logging()
    
    # Verifica diretórios
    check_directories()
    
    # Valida configurações
    try:
        Config.validate_environment()
        logging.info("Configurações validadas com sucesso")
    except Exception as e:
        logging.warning(f"Aviso na validação de configurações: {str(e)}")
    
    try:
        # Inicia interface gráfica
        app = AEGISInterface()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Erro fatal: {str(e)}", exc_info=True)
        print(f"Erro fatal: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())