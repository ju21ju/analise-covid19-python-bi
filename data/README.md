# Fontes de Dados

Os dados brutos foram obtidos a partir de repositórios públicos globais, garantindo a transparência e fidedignidade da análise:
*   **Our World in Data (OWID)**: Dataset completo sobre casos, mortes e vacinação.
*   **Johns Hopkins University**: Dados históricos para validação de séries temporais.

**Tratamento de Dados:**
Foram aplicadas técnicas de limpeza para lidar com dados ausentes (NaN) e normalização de nomes de países para garantir a precisão dos cruzamentos geográficos.

## Estrutura de Arquivos nesta pasta

*   **`dados_covid_limpos.csv`**: Base de dados final estruturada após o processo de limpeza (limpeza de valores nulos e padronização).
*   **`projeto-1-483023...json`**: Arquivo de configuração/credenciais utilizado para a integração com a API de coleta de dados.
