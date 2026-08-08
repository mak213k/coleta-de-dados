# https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis
import pandas as pd
import matplotlib.pyplot as plt

caminho = r"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis"

print("Carregando arquivo...")
df = pd.read_csv(caminho, sep=";", encoding="iso-8859-1")

df.columns = df.columns.str.strip()

cidade = input("Digite o município: ").strip()
uf = input("Digite o estado (ex: SP): ").strip().upper()

resultado = df[(df["Municipio"].str.upper() == cidade.upper()) & (df["Estado - Sigla"].str.upper() == uf)]

if len(resultado) > 0:
    print(f"\nForam encontrados {len(resultado)} postos:")
    
    colunas = ["Revenda", "Bairro", "Produto", "Valor de Venda"]
    print(resultado[colunas].head(20))
else:
    print("\nNenhum resultado encontrado para essa cidade.")

#  Gráfico
df_cidade = df[(df["Municipio"].str.upper() == cidade.upper()) & (df["Estado - Sigla"].str.upper() == uf)].copy()
if not df_cidade.empty:

    df_cidade["Valor de Venda"] = df_cidade["Valor de Venda"].astype(str).str.replace(",", ".")
    df_cidade["Valor de Venda"] = pd.to_numeric(df_cidade["Valor de Venda"], errors="coerce")
    df_cidade = df_cidade.dropna(subset=["Valor de Venda"])

    medias = df_cidade.groupby("Produto")["Valor de Venda"].mean()

    medias.plot(kind="bar",color="pink")
    plt.title(f"Preço Médio - {cidade.title()}/{uf}")
    plt.ylabel("Preço (R$)")
    plt.xlabel("Produto")
    plt.show() 
else:
    print("\nNenhum dado encontrado para esta cidade.")