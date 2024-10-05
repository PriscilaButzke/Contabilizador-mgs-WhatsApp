from flask import Flask, request, render_template, redirect, url_for, send_file
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Página inicial que exibe o formulário
@app.route('/')
def index():
    return render_template('form.html')  # Renderiza o formulário HTML

# Rota que processa os dados enviados pelo formulário
@app.route('/process', methods=['POST'])
def process():
    # Receber os dados do formulário
    group_name = request.form['group_name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    max_users = int(request.form['user_quantity'])

    # Receber o arquivo de chat .txt
    file = request.files['file']
    if file and file.filename.endswith('.txt'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)  # Salva o arquivo no diretório especificado

        # Processar o chat e gerar gráfico e Excel
        graph_url, excel_url = process_chat(file_path, group_name, start_date, end_date, max_users)

        # Renderizar result.html com os links para download
        return render_template('result.html', graph_url=graph_url, excel_url=excel_url)
    else:
        return "<h1>Erro: O arquivo enviado não é um .txt válido.</h1>"

def process_chat(filename, group_name, start, end, max_users):
    # Conversão das datas do formulário
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d")

    # Lista para armazenar as mensagens formatadas
    formatted_messages = []

    # Expressão regular para capturar as partes da linha do arquivo
    pattern = re.compile(r"\[(\d{2}/\d{2}/\d{4}), \d{2}:\d{2}:\d{2}\]\s*~?\s*(.+?):\s*(.+)")

    # Processamento do arquivo para formatar as mensagens
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            match = pattern.match(line)
            if match:
                date = match.group(1)  # Captura a data
                name = match.group(2).strip()  # Captura o nome da pessoa e remove espaços
                message = match.group(3).strip()  # Captura a mensagem e remove espaços

                # Formatação desejada
                formatted_message = f"{date} - {name}: {message}"
                formatted_messages.append(formatted_message)

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

    # Filtrar o número máximo de usuários
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
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    plt.savefig(output_path)

    # Links para os arquivos gerados
    graph_url = url_for('download_file', filename=output_filename)

    # Salvar o Excel
    excel_filename = f"{group_name}_contagem_mensagens.xlsx"
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
    df.to_excel(excel_path, index=False)

    excel_url = url_for('download_file', filename=excel_filename)

    return graph_url, excel_url

# Rota para download de arquivos
@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
