from flask import Flask
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SECRET_KEY"] = "da80480a59b1f71b360ea403dcd0aa90"

# Configuração do banco de dados
app.config["DATABASE_URL"] = "postgresql://ads_hunter_db_user:XnmbyzihE4aKpHHRGbqQUYME0AsGL7Gb@dpg-cv4tv952ng1s73fns530-a/ads_hunter_db"  # Substitua pelo Internal Database URL do Render

# Função para conectar ao banco de dados
def get_db_connection():
    conn = psycopg2.connect(app.config["DATABASE_URL"])
    return conn

# Função para criar a tabela se ela não existir
def criar_tabela_assinaturas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS assinaturas (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_email ON assinaturas (email);")
    conn.commit()
    cur.close()
    conn.close()

# Cria a tabela ao iniciar a aplicação
criar_tabela_assinaturas()

# Importe o main.py para registrar as rotas
from AdsHunterSite import main