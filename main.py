from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Amazon Afiliados Bot activo."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Mantener Flask vivo en un hilo
    Thread(target=run_flask, daemon=True).start()
    # Ejecutar el bot principal en el hilo principal
    from bot import run_estrategia
    run_estrategia()
