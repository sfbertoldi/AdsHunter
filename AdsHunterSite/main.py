import hmac
import hashlib
import logging
from datetime import datetime
from flask import request, jsonify, redirect, url_for, flash, render_template
from AdsHunterSite import app, get_db_connection  # Importa o app e a conexão do banco de dados do __init__.py

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token da Kiwify (substitua pelo seu Token)
KIWIFY_TOKEN = "atoqc0xb7vf"

# Funções para interagir com o banco de dados
def salvar_assinatura(email, status):
    """Salva ou atualiza uma assinatura no banco de dados."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO assinaturas (email, status, updated_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO UPDATE
            SET status = EXCLUDED.status, updated_at = EXCLUDED.updated_at
            """,
            (email, status, datetime.utcnow())
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar assinatura: {str(e)}")
        raise
    finally:
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


# Função para validar a assinatura HMAC
def validar_webhook(payload, signature, token):
    """
    Valida a assinatura HMAC enviada pela Kiwify.
    """
    # Gera a assinatura HMAC usando o Token e o payload
    hmac_digest = hmac.new(token.encode(), payload, hashlib.sha256).hexdigest()

    # Compara a assinatura gerada com a assinatura recebida
    return hmac.compare_digest(hmac_digest, signature)


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
        # Obtém a assinatura do cabeçalho
        signature = request.headers.get("X-Kiwify-Signature")
        if not signature:
            return jsonify({"error": "Assinatura ausente"}), 400

        # Obtém o corpo da requisição (payload)
        payload = request.get_data()

        # Valida a assinatura HMAC
        if not validar_webhook(payload, signature, KIWIFY_TOKEN):
            return jsonify({"error": "Assinatura inválida"}), 403

        # Converte o payload para JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400

        # Extrai os campos obrigatórios
        email = data.get("Customer", {}).get("email")
        status = data.get("Subscription", {}).get("status")

        if not email or not status:
            return jsonify({"error": "Campos obrigatórios ausentes"}), 400

        # Salva os dados no banco de dados
        salvar_assinatura(email, status)
        return jsonify({"message": "Assinatura atualizada com sucesso!"}), 200

    except Exception as e:
        logger.error(f"Erro no processamento: {str(e)}")
        return jsonify({"error": f"Erro no processamento: {str(e)}"}), 500