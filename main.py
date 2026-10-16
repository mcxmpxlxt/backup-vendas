import os
import shutil
import csv
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime

def carregar_configuracoes():
    """Lê o arquivo config.txt e retorna um dicionário com os valores"""
    config = {}
    try:
        with open('config.txt', 'r', encoding='utf-8') as f:
            for linha in f:
                # Ignora linhas em branco
                if not linha.strip():
                    continue
                
                # O split('=') divide "pasta=dados" em ['pasta', 'dados']
                partes = linha.strip().split('=')
                if len(partes) == 2:
                    chave = partes[0].strip()
                    valor = partes[1].strip()
                    config[chave] = valor
        return config
    except FileNotFoundError:
        print("ERRO: Arquivo config.txt não encontrado! O sistema não pode continuar.")
        return None

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

def atualizar_historico_mensal(faturamento_dia, itens_dia):
    """Salva e acumula os dados do mês. Se mudar o mês, zera a contagem."""
    arquivo_historico = 'historico_mensal.json'
    
    # Pega o ano e o mês atual no formato "2026-10"
    mes_atual = datetime.now().strftime("%Y-%m")
    
    # Estrutura base caso seja a primeira vez rodando ou um mês novo
    dados_historico = {
        "mes": mes_atual,
        "faturamento_acumulado": 0.0,
        "itens_acumulados": 0
    }

    # Tenta ler o caderninho anterior (se o arquivo existir)
    if os.path.exists(arquivo_historico):
        try:
            with open(arquivo_historico, 'r', encoding='utf-8') as f:
                dados_salvos = json.load(f)
                
                # Se o mês salvo for igual ao mês de hoje, nós mantemos os dados anteriores para somar
                if dados_salvos.get("mes") == mes_atual:
                    dados_historico = dados_salvos
        except Exception as e:
            print(f"Erro ao ler histórico: {e}")

    # Agora somamos o resultado de HOJE com o que já estava acumulado
    dados_historico["faturamento_acumulado"] += faturamento_dia
    dados_historico["itens_acumulados"] += itens_dia
    dados_historico["mes"] = mes_atual # Garante que estamos no mês correto

    # Salva o caderninho atualizado de volta no HD do cliente
    with open(arquivo_historico, 'w', encoding='utf-8') as f:
        json.dump(dados_historico, f, ensure_ascii=False, indent=4)

    return dados_historico

def gerar_relatorio(caminho_arquivo):
    """Lê o arquivo de vendas, calcula o faturamento e estatísticas dos produtos"""
    total_faturado = 0.0
    total_itens = 0
    
    # Dicionário para guardar estatísticas de cada produto (como um Array de Structs no C)
    produtos = {}

    try:
        with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                nome = linha['Produto']
                quantidade = int(linha['Quantidade'])
                valor = float(linha['Valor'])
                receita = quantidade * valor
                
                total_itens += quantidade
                total_faturado += receita
                
                # Se o produto já está no dicionário, soma as quantidades e receitas
                if nome in produtos:
                    produtos[nome]['quantidade'] += quantidade
                    produtos[nome]['receita'] += receita
                # Se é a primeira vez que vemos o produto, cria o registro dele
                else:
                    produtos[nome] = {'quantidade': quantidade, 'receita': receita}
        
        # Se a planilha estiver vazia
        if not produtos:
            return "Nenhuma venda registrada no arquivo."

        # -- AQUI ENTRA A NOSSA NOVA INTELIGÊNCIA MENSAL --
        historico = atualizar_historico_mensal(total_faturado, total_itens)
        faturamento_mes = historico['faturamento_acumulado']
        itens_mes = historico['itens_acumulados']
        # ------------------------------------------------

        # O max() e min() acham o maior e menor. 
        # O "key=lambda p:" é o jeito do Python dizer: "compare usando este critério específico"
        produto_mais_vendido = max(produtos, key=lambda p: produtos[p]['quantidade'])
        produto_menos_vendido = min(produtos, key=lambda p: produtos[p]['quantidade'])
        produto_maior_renda = max(produtos, key=lambda p: produtos[p]['receita'])

        # Montando o texto do resumo formatado. As 3 aspas duplas permitem pular linha livremente!
        resumo = f"""Resumo do Dia: {total_itens} produtos vendidos | Faturamento Geral: R$ {total_faturado:.2f}

DESEMPENHO MENSAL ACUMULADO:
- Total de Itens Vendidos no Mês: {itens_mes}
- Faturamento Total do Mês: R$ {faturamento_mes:.2f}

Destaques do dia:
- Mais vendido (Quantidade): {produto_mais_vendido} ({produtos[produto_mais_vendido]['quantidade']} unidades)
- Menos vendido (Quantidade): {produto_menos_vendido} ({produtos[produto_menos_vendido]['quantidade']} unidades)
- Maior Geração de Renda: {produto_maior_renda} (R$ {produtos[produto_maior_renda]['receita']:.2f})"""
        
        print(resumo)
        return resumo
        
    except FileNotFoundError:
        return "ALERTA: O arquivo de vendas não foi encontrado no sistema!"
    except Exception as e:
        return f"ALERTA: Erro ao processar o relatório: {str(e)}"

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
    
    # 1. Carrega as configurações do cliente
    config = carregar_configuracoes()
    
    # Se o arquivo não existir, encerra o programa antecipadamente
    if not config:
        print("--- Processo Abortado ---")
        # Encerra o script com erro (exit code 1)
        exit(1)
        
    # 2. Extraindo as variáveis do dicionário
    pasta_dados = config.get('pasta_origem', 'dados_vendas')
    pasta_backups = config.get('pasta_destino', 'backups_salvos')
    arquivo_vendas = config.get('nome_arquivo_vendas', 'vendas_hoje.csv')
    
    # 3. Executando o fluxo com as configurações dinâmicas
    fazer_backup(pasta_dados, pasta_backups)
    
    caminho_csv = os.path.join(pasta_dados, arquivo_vendas)
    resumo_vendas = gerar_relatorio(caminho_csv)
    
    # Se o relatório não for erro, envia o e-mail
    if not "ALERTA" in resumo_vendas:
         enviar_email(resumo_vendas)
    
    print("--- Processo Finalizado ---")