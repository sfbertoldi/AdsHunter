import os
import json
from flask import request, jsonify, redirect, url_for, flash, render_template
from AdsHunterSite import app  # Importa o app do __init__.py

# Caminho do arquivo JSON onde armazenaremos os assinantes
ASSINATURAS_PATH = os.path.join(os.path.dirname(__file__), "assinaturas.json")


def carregar_assinaturas():
    """Carrega os assinantes do JSON."""
    if not os.path.exists(ASSINATURAS_PATH):
        return []
    with open(ASSINATURAS_PATH, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def salvar_assinaturas(assinaturas):
    """Salva os assinantes no JSON."""
    with open(ASSINATURAS_PATH, "w", encoding="utf-8") as file:
        json.dump(assinaturas, file, indent=4, ensure_ascii=False)


def verificar_acesso(email):
    """Verifica se o usuário tem uma assinatura ativa no JSON."""
    assinaturas = carregar_assinaturas()
    for ass in assinaturas:
        if ass["email"] == email and ass["status"] == "active":
            return True
    return False


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        if email == senha:  # Exigimos que e-mail e senha sejam iguais
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


@app.route("/webhook", methods=["POST"])
def receber_webhook():
    """Recebe os dados da Kiwify e atualiza o JSON de assinaturas."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400

        email = data.get("Customer", {}).get("email")
        status = data.get("Subscription", {}).get("status")

        if not email or not status:
            return jsonify({"error": "Campos obrigatórios ausentes"}), 400

        assinaturas = carregar_assinaturas()

        # Atualiza ou adiciona o assinante
        email_encontrado = False
        for ass in assinaturas:
            if ass["email"] == email:
                ass["status"] = status  # Atualiza o status
                email_encontrado = True
                break

        if not email_encontrado:
            assinaturas.append({"email": email, "status": status})

        salvar_assinaturas(assinaturas)
        return jsonify({"message": "Assinatura atualizada com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro no processamento: {str(e)}"}), 500
