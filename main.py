import os
import shutil
import csv
import smtplib
from email.message import EmailMessage
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
    """Lê o arquivo de vendas e calcula o faturamento total com tratamento de erros"""
    total_faturado = 0.0
    total_itens = 0

    # O 'try' tenta executar o bloco. Se falhar, pula pro 'except'
    try:
        with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                quantidade = int(linha['Quantidade'])
                valor = float(linha['Valor'])
                total_itens += quantidade
                total_faturado += (quantidade * valor)
        
        resumo = f"Resumo do Dia: {total_itens} produtos vendidos | Faturamento: R$ {total_faturado:.2f}"
        print(resumo)
        return resumo
        
    except FileNotFoundError:
        erro_msg = "ALERTA: O arquivo de vendas não foi encontrado no sistema!"
        print(erro_msg)
        return erro_msg
    except Exception as e:
        # Captura qualquer outro erro inesperado
        erro_msg = f"ALERTA: Erro ao processar o relatório: {str(e)}"
        print(erro_msg)
        return erro_msg

def enviar_email(resumo):
    """Lê as credenciais e envia o resumo das vendas por e-mail"""
    print("Preparando para enviar o e-mail...")
    
    # Lê o e-mail e a senha do nosso arquivo seguro
    with open('credenciais.txt', 'r') as f:
        linhas = f.readlines()
        # O .strip() no Python remove espaços extras e a quebra de linha (\n) do final
        email_bot = linhas[0].strip()
        senha_bot = linhas[1].strip()

    # Montando a estrutura do e-mail
    msg = EmailMessage()
    msg['Subject'] = 'Relatório Automático de Vendas e Backup'
    msg['From'] = email_bot
    msg['To'] = email_bot # Vamos mandar para nós mesmos como teste
    
    # Corpo do e-mail
    corpo = f"""Olá, 

Aqui está o fechamento do seu negócio hoje:
{resumo}

O backup dos arquivos foi realizado com sucesso.
Sistema operando 100%.
"""
    msg.set_content(corpo)

    # Conectando no servidor do Gmail (porta 465 é a porta segura padrão)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_bot, senha_bot)
        smtp.send_message(msg)
        
    print("E-mail enviado com sucesso!")

# Ponto de entrada do nosso script (semelhante ao int main() do C)
if __name__ == "__main__":
    print("--- Iniciando Sistema ---")
    fazer_backup("dados_vendas", "backups_salvos")
    
    caminho_csv = os.path.join("dados_vendas", "vendas_hoje.csv")
    resumo_vendas = gerar_relatorio(caminho_csv)
    
    # Chamando a nova função e passando a variável do relatório
    enviar_email(resumo_vendas)
    
    print("--- Processo Finalizado ---")

