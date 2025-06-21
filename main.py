from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Amazon Afiliados Bot activo."

def run_flask():
    port = int(os.environ.get("PORT", 81))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Ejecuta Flask en un hilo para mantener el Repl activo
    threading.Thread(target=run_flask).start()
    # Aquí puedes importar y lanzar tu bot si quieres que corra junto al servidor
    # from bot import run_estrategia
    # run_estrategia()
    # O simplemente mantener el proceso vivo
    import time
    while True:
        time.sleep(60)