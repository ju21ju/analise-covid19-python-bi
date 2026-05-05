import os
import numpy as np
import pandas as pd
from google.cloud import bigquery

CREDENCIAIS = "projeto-1-483023-ff66011380ec.json"
CSV_SAIDA =  "dados_covid_limpos.csv"

def conectar_bigquery(credenciais: str) -> bigquery.Client:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credenciais
    return bigquery.Client()

def buscar_dados(client: bigquery.Client) -> pd.DataFrame:
    query = """
            SELECT
              state,
              DATE_TRUNC(date, MONTH) AS mes,
              SUM(cases)  AS total_casos,
              SUM(deaths) AS total_mortes,
              SAFE_DIVIDE(SUM(deaths), SUM(cases)) * 100 AS letalidade
            FROM `projeto-1-483023.covid19_brasil.brasil_covid19`
            GROUP BY state, mes
            ORDER BY mes, state
    """
    print("Aguarde... Conectando ao BigQuery")
    df = client.query(query).to_dataframe()
    print(f"Sucesso! {len(df)} registros carregados. \n")
    return df

def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    df['mes'] = pd.to_datetime(df['mes'])
    df_limpo = df.dropna(subset=['letalidade'])
    df_limpo = df_limpo[df_limpo['letalidade'] > 0].copy()

    print (f"--- DADOS APÓS A LIMPEZA: {len(df_limpo)} registros ---")

    df_limpo.to_csv(CSV_SAIDA, index=False, sep=';', encoding= 'utf-8-sig')
    print(f"Arquivo '{CSV_SAIDA}' gerado com sucesso!")
    return df_limpo

#Análise Brasil

def analisar_brasil(df_limpo: pd.DataFrame) -> pd.DataFrame:
    df_brasil = df_limpo.groupby('mes').agg(
        total_casos = ('total_casos', 'sum'),
        total_mortes = ('total_mortes', 'sum')
    ).reset_index()

    df_brasil['crescimento_casos_%'] = df_brasil['total_casos']. pct_change()* 100
    df_brasil['crescimento_mortes_%'] = df_brasil['total_mortes']. pct_change()* 100

    df_brasil.replace([np.inf, -np.inf], np.nan, inplace=True)

    print("\n --- EVOLUÇÃO MENSAL NO BRAIL (TAXA DE CRESCIMENTO---")
    print(df_brasil.head(5).to_string())
    return df_brasil

#ANALISAR ESTADOS

def analisar_estados(df_limpo: pd.DataFrame) -> None:
    print("\n---ANÁLISE DE IMPACTO POR ESTADO---")
    idx_pico_letalidade = df_limpo['letalidade'].idxmax()
    top_1_letalidade = df_limpo.loc[idx_pico_letalidade]

    print(f"\nMAIOR LETALIDADE (num único mês): {top_1_letalidade['state']}"
          f"em {top_1_letalidade['mes'].strftime('%d/%m')}")
    print(f" -> {top_1_letalidade['letalidade']:.2f}% de letalidade")

    top_5_letalidade = (
        df_limpo.groupby('state') ['letalidade']
        .mean()
        .sort_values(ascending=False)
        .head(5)
    )
    print('\nTOP 5 ESTADOS - Maior letalidade média:')
    for i, (estado,valor) in enumerate(top_5_letalidade.items(), 1):
        print(f" {i}. {estado}: {valor:.2f}%")

#CORRELAÇÂO

def analisar_correlacao(df_limpo: pd.DataFrame) -> None:
    correlacao = df_limpo['total_casos'].corr(df_limpo['total_mortes'])

    print(f"\n---ANÁLISE DE CORRELAÇÃO---")
    print(f"Correlação entre Casos e Mortes: {correlacao:.4f}")

    if correlacao > 0.9:
        print("Insight: Relação fortíssima. O aumento de casos previu quase diretamente o aumento de mortes.")
    else:
        print("Insight: Relação moderada/forte. Outros fatores também influenciaram as mortes.")

#MAIN

def main():

    try:
        client = conectar_bigquery(CREDENCIAIS)
        df_raw = buscar_dados(client)
        df_pronto = limpar_dados(df_raw)

        analisar_brasil(df_pronto)
        analisar_estados(df_pronto)
        analisar_correlacao(df_pronto)

        print("\nPronto! Agora é só abrir o power BI.")

    except Exception as e:
         print(f"\n[ERRO]: {e}")

if __name__ == "__main__":
    main()