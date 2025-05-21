from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave_secreta_simples'
SENHA_MANICURE = "unhas123"

HORARIOS_DISPONIVEIS = [
    "09:00", "10:00", "11:00", "12:00", 
    "13:00", "14:00", "15:00", "16:00", "17:00"
]

def init_db():
    conn = sqlite3.connect('agendamentos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data TEXT NOT NULL,
            horario TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    data_hoje = datetime.today().strftime('%Y-%m-%d')
    return render_template('index.html', horarios=HORARIOS_DISPONIVEIS, data_hoje=data_hoje)

@app.route('/agendar', methods=['POST'])
def agendar():
    nome = request.form['nome']
    data = request.form['data']
    horario = request.form['horario']

    conn = sqlite3.connect('agendamentos.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM agendamentos WHERE data = ? AND horario = ?", (data, horario))
    existente = cursor.fetchone()

    if existente:
        flash("Este horário já está agendado. Por favor, escolha outro.")
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("INSERT INTO agendamentos (nome, data, horario) VALUES (?, ?, ?)", (nome, data, horario))
    conn.commit()
    conn.close()
    flash("Agendamento realizado com sucesso!")
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        senha = request.form['senha']
        if senha != SENHA_MANICURE:
            flash("Senha incorreta!")
            return redirect(url_for('admin'))

    conn = sqlite3.connect('agendamentos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agendamentos ORDER BY data, horario")
    agendamentos = cursor.fetchall()
    conn.close()
    return render_template('admin.html', agendamentos=agendamentos)

@app.route('/deletar/<int:id>', methods=['GET', 'POST'])
def deletar(id):
    if request.method == 'POST':
        senha = request.form['senha']
        if senha != SENHA_MANICURE:
            flash("Senha incorreta!")
            return redirect(url_for('admin'))

        conn = sqlite3.connect('agendamentos.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agendamentos WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        flash("Agendamento cancelado com sucesso!")
        return redirect(url_for('admin'))

    return render_template('confirm_delete.html', id=id)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)