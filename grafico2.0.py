import matplotlib.pyplot as plt
import datetime
import os
import re
from collections import defaultdict
import pandas as pd

# Nome do arquivo de mensagens
filename = "_chat.txt"

group_name = input("Digite o nome do seu grupo: ")

# Alterar as datas para o intervalo desejado
start = input("Digite a data inicial para analise: ")  
end = input("Digite a data final para analise:  ")

start_date = datetime.datetime.strptime(start, "%d/%m/%Y")
end_date = datetime.datetime.strptime(end, "%d/%m/%Y")

# Lista para armazenar as mensagens formatadas
formatted_messages = []

# Expressão regular para capturar as partes da linha
pattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}), \d{2}:\d{2}:\d{2}\]\s*~?\s*(.+?):\s*(.+)")

# Processamento do arquivo para formatar as mensagens
with open(filename, 'r', encoding='utf-8') as file:
    for line in file:
        match = pattern.match(line)
        if match:
            date = match.group(1)  # Captura a data
            name = match.group(2).strip()  # Captura o nome da pessoa e remove espaços em branco
            message = match.group(3).strip()  # Captura a mensagem e remove espaços em branco

            # Formatação desejada
            formatted_message = f"{date} - {name}: {message}"
            formatted_messages.append(formatted_message)

# Nome do arquivo de saída
output_filename = "mensagens_formatadas.txt"

# Exemplo de como salvar as mensagens formatadas em um arquivo
with open(output_filename, 'w', encoding='utf-8') as output_file:
    for message in formatted_messages:
        output_file.write(message + '\n')

print(f"Mensagens formatadas salvas em {output_filename}")

# Contagem de mensagens por usuário no intervalo de datas especificado
counter = defaultdict(int)
for message in formatted_messages:
    try:
        # Extrair data e nome da pessoa
        date_str, rest = message.split(" - ", 1)
        name, _ = rest.split(": ", 1)
        message_date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
        if start_date <= message_date <= end_date:
            counter[name] += 1
    except ValueError:
        print("ERROR:", message)

# Converter o contador em um DataFrame
df = pd.DataFrame(list(counter.items()), columns=['Usuário', 'Quantidade de Mensagens'])

# Ordenar os usuários por quantidade de mensagens em ordem decrescente
df = df.sort_values(by='Quantidade de Mensagens', ascending=False)

# Salvar o DataFrame completo como um arquivo Excel
excel_filename = f"{group_name}_contagem_mensagens.xlsx"
df.to_excel(excel_filename, index=False)

print(f"Arquivo de contagem de mensagens salvo como {excel_filename}")

# Permitir ao usuário definir o número de usuários a exibir no gráfico
max_users = int(input("Quantos usuários você gostaria de exibir no gráfico? "))
df_limited = df.head(max_users)

# Plotar o gráfico com os usuários limitados
names = df_limited['Usuário']
values = df_limited['Quantidade de Mensagens']

fig, ax = plt.subplots()
fig.set_size_inches(15, 10)

bars = ax.bar(names, values)

ax.set_title(f'Os usuários que mais conversam de {start_date.strftime("%d/%m/%Y")} até {end_date.strftime("%d/%m/%Y")}')
ax.set_xticklabels(names, rotation=45, ha='right')

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 1), ha='center', va='bottom')

# Salvar o gráfico
output_filename = f"{group_name}_{start.replace('/', '')}_{end.replace('/', '')}.png"
output_path = os.path.join(os.path.expanduser('~'), 'Downloads', output_filename)
plt.savefig(output_path)

plt.show()
