import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(nome_modulo=None):
    """
    Configura e retorna um logger padronizado S-Rank.
    Salva logs na pasta raiz do projeto (Logs/) e mostra no terminal.
    """
    # 1. O Jutsu de Localização: Descobre a raiz do projeto dinamicamente
    # __file__ é o logger.py. O parent dele é a pasta 'Src'. O parent do 'Src' é a raiz 'PythonProject'.
    caminho_atual = Path(__file__).resolve().parent
    raiz_projeto = caminho_atual.parent

    # 2. Define o caminho absoluto para a pasta de logs
    pasta_logs = raiz_projeto / 'Logs'
    pasta_logs.mkdir(exist_ok=True)  # Cria a pasta se não existir, sem dar erro

    arquivo_log = pasta_logs / 'logs_lr_model'

    # 3. Configura o formatador (Data - Nível - Modulo - LINHA DO ERRO - Mensagem)
    # Adicionei o %(lineno)d pra você saber exatamente qual linha do código deu B.O.
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s:%(lineno)d - %(message)s')

    # 4. Handler de Arquivo (Rotativo: max 5MB, guarda 3 arquivos antigos)
    file_handler = RotatingFileHandler(
        filename=arquivo_log,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 5. Handler de Console (Terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # 6. Obtém o logger e evita duplicação de handlers
    logger = logging.getLogger(nome_modulo if nome_modulo else __name__)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger