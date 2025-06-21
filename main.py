from flask import Flask
import os
import threading
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Amazon Afiliados Bot activo."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":

    # Ejecuta Flask en un hilo para mantener el Repl activo
    Thread(target=run_flask).start()
    # Aquí puedes importar y lanzar tu bot si quieres que corra junto al servidor
    # from bot import run_estrategia
    # run_estrategia()
    # O simplemente mantener el proceso vivo
    import time
    while True:

        time.sleep(60)

    # Mantener Flask vivo en un hilo
    Thread(target=run_flask, daemon=True).start()
    # Ejecutar el bot principal en el hilo principal
    from bot import run_estrategia
    run_estrategia()

