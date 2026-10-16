# Auto Backup & Relatório de Vendas 

Um sistema automatizado em Python focado em segurança de dados e inteligência de negócios para pequenas empresas.

## O que o sistema faz?
1. **Backup Automático:** Localiza a pasta de dados do sistema, faz uma cópia completa e salva em um diretório seguro com um carimbo de data e hora (`timestamp`).
2. **Processamento de Dados:** Lê os registros de vendas do dia (formato CSV) e calcula instantaneamente o total de itens vendidos e o faturamento bruto.
3. **Alerta por E-mail:** Envia o relatório gerado diretamente para o e-mail do gestor de forma autônoma e segura.

## Como configurar no seu computador (Linux/Windows)

1. Clone este repositório.
2. Crie um arquivo `credenciais.txt` na raiz do projeto (ele está no `.gitignore` para sua segurança).
3. Adicione seu e-mail na primeira linha e a Senha de Aplicativo na segunda.
4. Execute o arquivo principal:
   `python3 main.py`

## Tecnologias utilizadas
- Python 3
- Bibliotecas nativas: `os`, `shutil`, `datetime`, `csv`, `smtplib`.

## Empacotamento
Para gerar um executável deste script para o cliente final (dispensando a instalação do Python), utilize a biblioteca PyInstaller:
`pip install pyinstaller`
`pyinstaller --onefile main.py`