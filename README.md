# Bot Amazon Afiliados + Twitter

## Estrategia recomendada (2025)
- Publica 20–25 tuits/día:
  - 50–60% promocionales (con enlace afiliado Amazon).
  - 40–50% contenido valioso (tips, recursos, noticias).
  - Retweets e interacciones con influencers y seguidores.
- Programa los tuits en picos de audiencia: martes a jueves, 9 am–2 pm.
- Analiza y ajusta la frecuencia según el rendimiento (clics, retweets, conversiones).
- Mezcla tipos de contenido y usa multimedia para mayor engagement.

## ¿Qué hace este bot?
- Busca productos populares en Amazon según nichos configurables.
- Genera tuits atractivos con enlace de afiliado.
- Publica automáticamente tuits diarios en Twitter según la estrategia.
- Evita productos repetidos.
- Permite personalizar nichos y contenido valioso.

## Configuración

1. **Claves de Amazon Product Advertising API**
   - Regístrate en [Amazon Associates](https://affiliate-program.amazon.com/).
   - Solicita acceso a la [Product Advertising API](https://webservices.amazon.com/paapi5/documentation/register.html).
   - Obtén tu Access Key, Secret Key y Associate Tag.

2. **Claves de Twitter API v2**
   - Crea una app en [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard).
   - Genera las claves y tokens necesarios (Bearer Token, API Key, API Secret, Access Token, Access Token Secret).

3. **Configura el bot**
   - Copia `.env.example` a `.env` y completa tus claves.
   - Edita `config.json` para definir tus nichos.
   - Edita `contenido_valioso.json` para personalizar tips y recursos.

4. **Instala dependencias**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecución local/manual**
   ```bash
   python bot.py
   ```

6. **Ejecución 24/7**
   - **En VPS:** Usa `screen`, `tmux` o configura un servicio systemd.
   - **En Replit/Render:** Sube el proyecto y configura el arranque automático.
   - **Con cron:** Programa la ejecución diaria:
     ```bash
     0 9 * * * /ruta/a/python /ruta/a/bot.py
     0 18 * * * /ruta/a/python /ruta/a/bot.py
     ```

7. **Despliegue gratuito 24/7 en Replit**
   - Ve a https://replit.com/ y crea una cuenta gratuita.
   - Haz clic en "Create Repl" y selecciona "Import from GitHub" si tu proyecto está en GitHub, o sube los archivos manualmente.
   - Sube todos los archivos del bot, incluyendo `.env` (no lo hagas público si tu Repl es público).
   - En la pestaña "Shell" de Replit, instala las dependencias:
     ```bash
     pip install -r requirements.txt
     ```
   - En el archivo `.replit`, asegúrate de tener:
     ```ini
     run = "python bot.py"
     ```
   - Haz clic en el botón "Run" para iniciar el bot.
   - **Mantenerlo activo 24/7:**
     - Usa un servicio como https://uptimerobot.com/ para hacer ping cada 5 minutos a la URL web de tu Repl (agrega un archivo `main.py` con un pequeño servidor Flask si necesitas exponer un endpoint web).
     - Mientras el Repl reciba visitas, el bot seguirá corriendo.
   - Consulta la documentación oficial de Replit para detalles y límites del plan gratuito.

## Notas
- El bot guarda los productos y tuits ya publicados en `posted_products.json` y `posted_tweets.json`.
- Personaliza los nichos en `config.json` y el contenido útil en `contenido_valioso.json`.
- No compartas tus claves.
