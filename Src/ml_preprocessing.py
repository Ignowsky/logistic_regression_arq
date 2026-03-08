import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
import joblib # Pra salvar o nosso túnel de transformação

from .logger import setup_logger

logger = setup_logger(__name__)

def drop_leakage_columns(df):
    """
    Dropa todas as colunas que o modelo (regressão lógistica) não consegue ler (IDs, Datas puras e variaveis categoricas)

    :param df: dataframe
    :return: dataframe
    """
    logger.info("INICIANDO: Dropando colunas de identifica~çao e vazamento de dados (Data Leakage)...")
    df_clean = df.copy()

    # Colunas inuteis para o modelo de regressão
    colunas_para_dropar = [
        'colaborador_sk',
        'data_nascimento',
        'data_admissao',
        'data_demissao',
        'data_corte'
    ]

    # Dropa apenas se a coluna existir no dataframe
    colunas_presentes = [col for col in colunas_para_dropar if col in df_clean.columns]
    df_clean = df_clean.drop(columns=colunas_presentes)

    return df_clean

def split_train_test(df, target_name = 'target_pediu_demissao'):
    """
    Fatia o dataset em Treino (pra aprender) e Teste (pra validar),
    garantindo a mesma proporção de turnover nos dois (stratify).

    :param df: dataframe
    :param target_name: target_pediu_demissao
    :return: X_train, X_test, y_train, y_test
    """
    logger.info("INICIANDO: Fatiamento train_test_split (80/20)...")

    X = df.drop(columns=[target_name])
    y = df[target_name]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    logger.info(f"Shape do Treino: X = {X_train.shape}, y = {y_train.shape}")
    logger.info(f"Shape do TEste: X = {X_test.shape}, y = {y_test.shape}")

    return X_train, X_test, y_train, y_test


def build_preprocessor():
    """
    Constrói o Transformer S-Rank: Normaliza números e mantém flags binárias das Top Features.
    """
    logger.info("INICIANDO: Construção do ColumnTransformer (StandardScaler)...")

    # Colunas contínuas (precisam de escala)
    num_features = ['meses_de_casa', 'salario_contratual', 'idade', 'qtd_dependentes']

    preprocessor = ColumnTransformer(
        transformers=[
            ('scaler', StandardScaler(), num_features)
        ],
        remainder='passthrough'  # Mantém as colunas binárias (0 e 1) intactas
    )

    return preprocessor