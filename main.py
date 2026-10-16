import os
import shutil
import csv
from datetime import datetime

def fazer_backup(pasta_origem, pasta_destino):
    """Função que copia os dados e gera um backup com data e hora"""
    
    # Verifica se a pasta de origem existe antes de tentar copiar
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não foi encontrada.")
        return

    # Garante que a pasta principal de backups exista
    os.makedirs(pasta_destino, exist_ok=True)

    # datetime.now() pega o momento atual. strftime formata isso para texto (String)
    data_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # No C usaríamos sprintf. No Python, o 'f' antes das aspas permite colocar variáveis dentro de chaves {}
    nome_pasta_backup = f"backup_{data_atual}"
    
    # os.path.join monta o caminho correto independente se é Linux ou Windows (ex: backups_salvos/backup_2026...)
    caminho_final = os.path.join(pasta_destino, nome_pasta_backup)

    # shutil.copytree faz todo o trabalho pesado de copiar a pasta e tudo que tem dentro
    shutil.copytree(pasta_origem, caminho_final)
    
    print(f"Sucesso! Backup salvo em: {caminho_final}")

def gerar_relatorio(caminho_arquivo):
    """Lê o arquivo de vendas e calcula o faturamento total"""
    
    total_faturado = 0.0
    total_itens = 0

    # No C, esquecer um fclose() causa vazamento de memória. 
    # O 'with open' do Python abre o arquivo, lê e fecha automaticamente no final.
    with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo:
        # O DictReader lê a primeira linha e transforma as colunas em "chaves" (como um índice customizado)
        leitor = csv.DictReader(arquivo)
        
        # O laço 'for' no Python lê linha por linha sem precisarmos controlar um contador (i++)
        for linha in leitor:
            # O Python lê tudo do arquivo como texto (string). Precisamos converter:
            quantidade = int(linha['Quantidade'])
            valor = float(linha['Valor'])
            
            total_itens += quantidade
            total_faturado += (quantidade * valor)
            
    # O '.2f' formata o número para ter apenas 2 casas decimais, igual no C (%0.2f)
    resumo = f"Resumo do Dia: {total_itens} produtos vendidos | Faturamento: R$ {total_faturado:.2f}"
    print(resumo)
    
    # A função devolve o texto pronto para usarmos no e-mail depois
    return resumo

# Ponto de entrada do nosso script (semelhante ao int main() do C)
if __name__ == "__main__":
    print("--- Iniciando Sistema ---")
    
    # 1. Faz a cópia de segurança
    fazer_backup("dados_vendas", "backups_salvos")
    
    # 2. Gera a matemática das vendas passando o caminho correto do arquivo
    caminho_csv = os.path.join("dados_vendas", "vendas_hoje.csv")
    resumo_vendas = gerar_relatorio(caminho_csv)
    
    print("--- Processo Finalizado ---")

