import easyocr
import pandas as pd
import re
import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageOps

# CONFIG
arquivo_pdf = 'campanha.pdf'
saida_excel = 'ofertas_assai.xlsx'

# Inicializa leitor EasyOCR
reader = easyocr.Reader(['pt'])

def processar_pdf(pdf_path):
    print(f'--- Abrindo PDF: {pdf_path} ---')
    
    doc = fitz.open(pdf_path)
    todos_os_dados = []
    # Regex para capturar preços (ex: 10,99 ou 1.250,00)
    regex_preco = re.compile(r'(\d{1,3}(?:\.\d{3})*,\d{2})')

    for num_pagina in range(len(doc)):
        print(f'Processando página {num_pagina + 1}...')
        pagina = doc.load_page(num_pagina)
        
        # Aumentamos a qualidade (3.0 é um bom equilíbrio entre precisão e velocidade)
        pix = pagina.get_pixmap(matrix=fitz.Matrix(3, 3))
        
        # Converte para PIL e depois para Tons de Cinza (melhora MUITO o OCR)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_cinza = ImageOps.grayscale(img)
        imagem_np = np.array(img_cinza)
        
        # detail=1 retorna as coordenadas [x,y] de cada bloco de texto
        resultado = reader.readtext(imagem_np, detail=1)
        
        precos_detectados = []
        textos_detectados = []

        # Separar o que é preço e o que é texto/descrição
        for (bbox, texto, prob) in resultado:
            texto_limpo = texto.strip()
            if regex_preco.search(texto_limpo):
                # Guarda o preço e o centro da caixa dele
                centro_y = (bbox[0][1] + bbox[2][1]) / 2
                centro_x = (bbox[0][0] + bbox[1][0]) / 2
                precos_detectados.append({'texto': texto_limpo, 'y': centro_y, 'x': centro_x})
            else:
                # Guarda textos com mais de 3 caracteres que não sejam lixo
                if len(texto_limpo) > 3:
                    centro_y = (bbox[0][1] + bbox[2][1]) / 2
                    centro_x = (bbox[0][0] + bbox[1][0]) / 2
                    textos_detectados.append({'texto': texto_limpo, 'y': centro_y, 'x': centro_x})

        # Para cada preço, encontrar o texto mais próximo que esteja ACIMA dele
        for p in precos_detectados:
            melhor_nome = ""
            menor_distancia = float('inf')

            for t in textos_detectados:
                # Calcula a distância entre o preço e o texto
                dist = np.sqrt((p['x'] - t['x'])**2 + (p['y'] - t['y'])**2)
                
                # Regra: o produto geralmente está logo acima (y menor) ou muito perto lateralmente
                if t['y'] < p['y'] and dist < menor_distancia:
                    menor_distancia = dist
                    melhor_nome = t['texto']
            
            if melhor_nome:
                todos_os_dados.append({
                    'Página': num_pagina + 1,
                    'Produto': melhor_nome,
                    'Preço': p['texto']
                })

    doc.close()
    return todos_os_dados

def salvar_dados(dados):
    if not dados:
        print("Nenhum dado encontrado.")
        return

    df = pd.DataFrame(dados)
    # Remove duplicatas exatas de produto e preço
    df = df.drop_duplicates(subset=['Produto', 'Preço']).reset_index(drop=True)
    
    # Limpeza final: remove R$ se houver e garante formato numérico no Excel se desejar
    df['Preço'] = df['Preço'].str.replace('R$', '', regex=False).str.strip()
    
    df.to_excel(saida_excel, index=False)
    print(f'\n--- Sucesso! ---')
    print(f'Foram encontrados {len(df)} itens únicos. Planilha: {saida_excel}')

if __name__ == '__main__':
    try:
        produtos = processar_pdf(arquivo_pdf)
        salvar_dados(produtos)
    except Exception as e:
        print(f"Erro ao processar: {e}")