from AdsHunterSite import app  # Importa o app corretamente
from flask import render_template, redirect, url_for, request, flash

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        if email == senha:
            return redirect(url_for("produtos"))
        else:
            flash("Acesso negado. Verifique seu email.", "danger")

    return render_template("login.html")

@app.route("/produtos")
def produtos():
    return render_template("index.html")

@app.route("/logout")
def logout():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

