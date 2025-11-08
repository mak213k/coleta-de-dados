import requests
import pandas as pd

regioes = {
    "norte": ["AC","AP","AM","PA","RO","RR","TO"],
    "nordeste": ["AL","BA","CE","MA","PB","PE","PI","RN","SE"],
    "centro-oeste": ["DF","GO","MT","MS"],
    "sudeste": ["ES","MG","RJ","SP"],
    "sul": ["PR","RS","SC"]
}
print("Escolha uma região:")
print("1 - Norte")
print("2 - Nordeste")
print("3 - Centro-Oeste")
print("4 - Sudeste")
print("5 - Sul")

opcao = input("Digite o número da região desejada: ")
map_opcao = {
    "1":"norte",
    "2":"nordeste",
    "3":"centro-oeste",
    "4":"sudeste",
    "5":"sul"
}

regiao_escolhida = map_opcao.get(opcao)

if not regiao_escolhida:
    print("Opção inválida! Execute o programa novamente.")
    exit()

ufs = regioes[regiao_escolhida]
print(f"Estados: {', '.join(ufs)}\n")

dados_final = []

for uf in ufs:
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    response = requests.get(url)

    if response.status_code == 200:
        cidades = response.json()

        for cidade in cidades:
            dados_final.append({
                "Região": regiao_escolhida.upper(),
                "Estado": uf,
                "Cidade": cidade["nome"],
                "Código IBGE": cidade["id"]
            })
    else:
        print(f"Erro ao acessar dados do estado: {uf}")


df = pd.DataFrame(dados_final)

nome_arquivo = f"IBGE_{regiao_escolhida}.xlsx"
df.to_excel(nome_arquivo, index=False)
print(f" {nome_arquivo}")

