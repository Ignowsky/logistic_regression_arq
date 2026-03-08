import os
import sys
from dotenv import load_dotenv, find_dotenv  # Adicionado o find_dotenv
from sqlalchemy import create_engine

# Importando os dados do Logger.py
try:
    from .logger import setup_logger
except ImportError:
    from logger import setup_logger

logger = setup_logger(__name__)

# O Radar S-Rank: Acha o arquivo .env independente de onde o script for rodado
load_dotenv(find_dotenv())


def connect_to_db():
    """
    Cria e retorna a engine de conexão com o banco de dados PostgreSQL Usando a lib SQLAlchemy.
    Lendo as configurações descritas no arquivo .env
    """
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")
    schema = os.getenv("DB_SCHEMA")

    if not all([user, password, host, port, dbname, schema]):
        logger.error("ERROR: Parâmetros de conexão incompletos. Verifique o arquivo .env na raiz do projeto.")
        sys.exit(1)

    url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    try:
        # O Selo de Limpeza S-Rank: Remove espaços invisíveis do .env
        schema_limpo = schema.strip()

        # Sintaxe blindada com o schema_limpo
        engine = create_engine(url, connect_args={"options": f"-c search_path={schema_limpo}"})

        logger.info(f"SUCESSO: Conexão criada com sucesso no banco '{dbname}' (Schema: {schema_limpo}).")
        return engine, schema_limpo

    except Exception as e:
        logger.error(f"ERROR: Erro ao conectar no Banco de dados especificado: {e}")
        sys.exit(1)