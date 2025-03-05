import os
from flask import request, jsonify, redirect, url_for, flash, render_template
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
from AdsHunterSite import app  # Importa o app do __init__.py

# Configurações do Google Sheets (lidas das variáveis de ambiente)
GOOGLE_SHEETS_CREDENTIALS = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))  # Conteúdo do JSON
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")  # ID da planilha

# Autenticação no Google Sheets
def autenticar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEETS_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    return client

# Função para verificar o acesso
def verificar_acesso(email):
    """Verifica se o usuário tem uma assinatura ativa com base no último evento."""
    try:
        client = autenticar_google_sheets()
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        registros = sheet.get_all_records()

        # Filtra os registros pelo e-mail
        registros_usuario = [r for r in registros if r["Customer_email"] == email]

        if not registros_usuario:
            return False  # Usuário não encontrado

        # Ordena os registros pela data mais recente
        registros_usuario.sort(key=lambda x: datetime.strptime(x["updated_at"], "%Y-%m-%d %H:%M:%S"), reverse=True)

        # Pega o último evento
        ultimo_evento = registros_usuario[0]

        # Verifica se o último evento é válido
        if ultimo_evento["webhook_event_type"] in ["subscription_renewed", "order_approved"]:
            return True
        return False
    except Exception as e:
        print(f"Erro ao verificar acesso: {str(e)}")
        return False

# Rotas
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Verifica se o e-mail e a senha são iguais
        if email == senha:
            # Verifica se o e-mail está na planilha do Google Sheets
            if verificar_acesso(email):
                return redirect(url_for("produtos"))
            else:
                flash("Acesso negado. E-mail não encontrado ou sem assinatura ativa.", "danger")
        else:
            flash("E-mail e senha devem ser iguais.", "danger")

    return render_template("login.html")

@app.route("/produtos")
def produtos():
    return render_template("index.html")

@app.route("/logout")
def logout():
    return redirect(url_for("login"))
