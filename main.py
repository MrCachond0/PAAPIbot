from flask import Flask
import os
from threading import Thread
import time

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Amazon Afiliados Bot activo."

    app.run(host="0.0.0.0", port=port)

def run_bot():
    from bot import run_estrategia
    run_estrategia()

if __name__ == "__main__":
    # Inicia Flask en un hilo para mantener el Repl activo
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Inicia el bot en el hilo principal
    run_bot()
    # Si el bot termina, mantiene el proceso vivo
    while True:
        time.sleep(60)

