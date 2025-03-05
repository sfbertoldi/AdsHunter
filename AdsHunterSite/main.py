from flask import Flask, render_template, redirect, url_for, request, flash

app = Flask(__name__)

# Rota da tela de login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        if email == senha:  # Simples verificação
            return redirect(url_for("produtos"))
        else:
            flash("Acesso negado. Verifique seu email.", "danger")

    return render_template("login.html")

# Página de produtos
@app.route("/produtos")
def produtos():
    return render_template("index.html")

# Logout apenas redireciona para login
@app.route("/logout")
def logout():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
