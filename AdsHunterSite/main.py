import os
from datetime import datetime
from flask import request, jsonify, redirect, url_for, flash, render_template
from AdsHunterSite import app, get_db_connection  # Importa o app e a conexão do banco de dados do __init__.py


# Funções para interagir com o banco de dados
def salvar_assinatura(email, status):
    """Salva ou atualiza uma assinatura no banco de dados."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """O 
        INSERT INTassinaturas (email, status, updated_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO UPDATE
        SET status = EXCLUDED.status, updated_at = EXCLUDED.updated_at
        """,
        (email, status, datetime.utcnow())
    )
    conn.commit()
    cur.close()
    conn.close()


def verificar_acesso(email):
    """Verifica se o usuário tem uma assinatura ativa no banco de dados."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT status FROM assinaturas
        WHERE email = %s
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (email,)
    )
    resultado = cur.fetchone()
    cur.close()
    conn.close()

    if resultado and resultado["status"] == "active":
        return True
    return False


# Rotas da aplicação
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
    """Recebe os dados da Kiwify e atualiza o banco de dados."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400

        email = data.get("Customer", {}).get("email")
        status = data.get("Subscription", {}).get("status")

        if not email or not status:
            return jsonify({"error": "Campos obrigatórios ausentes"}), 400

        salvar_assinatura(email, status)
        return jsonify({"message": "Assinatura atualizada com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro no processamento: {str(e)}"}), 500
