import os
import shutil
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

# Ponto de entrada do nosso script (semelhante ao int main() do C)
if __name__ == "__main__":
    fazer_backup("dados_vendas", "backups_salvos")

