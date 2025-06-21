import os
import json
import time
import random
import requests
import base64
import hmac
import hashlib
import uuid
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from amazon_dynamic import is_valid_amazon_url, get_viral_product_for_niche

# Cargar variables de entorno
load_dotenv()

AMAZON_ACCESS_KEY = os.getenv('AMAZON_ACCESS_KEY')
AMAZON_SECRET_KEY = os.getenv('AMAZON_SECRET_KEY')
AMAZON_ASSOCIATE_TAG = os.getenv('AMAZON_ASSOCIATE_TAG')

# Credenciales para OAuth 1.0a (Twitter)
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

CONFIG_FILE = 'config.json'
POSTED_FILE = 'posted_products.json'
POSTED_TWEETS_FILE = 'posted_tweets.json'
CONTENIDO_VALIOSO_FILE = 'contenido_valioso.json'
TWEET_STATS_FILE = 'tweet_stats.json'

# Cargar nichos
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)
NICHES = config.get('niches', [])

# Cargar productos ya publicados
if os.path.exists(POSTED_FILE):
    with open(POSTED_FILE, 'r', encoding='utf-8') as f:
        posted_products = set(json.load(f))
else:
    posted_products = set()

# Cargar tuits ya publicados
if os.path.exists(POSTED_TWEETS_FILE):
    with open(POSTED_TWEETS_FILE, 'r', encoding='utf-8') as f:
        posted_tweets = json.load(f)
else:
    posted_tweets = {"promocionales": [], "valiosos": [], "retweets": []}

# Cargar contenido valioso
if os.path.exists(CONTENIDO_VALIOSO_FILE):
    with open(CONTENIDO_VALIOSO_FILE, 'r', encoding='utf-8') as f:
        contenido_valioso = json.load(f)
else:
    contenido_valioso = []

def save_posted_products():
    with open(POSTED_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(posted_products), f)

def save_posted_tweets():
    with open(POSTED_TWEETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(posted_tweets, f)

def save_tweet_stats(stats):
    with open(TWEET_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f)

def get_amazon_products(niche, max_results=10, fallback_niches=None):
    """
    Obtiene productos frescos y validados usando get_viral_product_for_niche.
    Si no hay producto válido en el nicho, prueba con nichos alternativos.
    """
    product = get_viral_product_for_niche(niche, fallback_niches=fallback_niches)
    return [product] if product else []

def generate_tweet(product):
    # Plantillas atractivas para tuits
    hooks = [
        "¡Descubre este top ventas!",
        "No te quedes sin el tuyo:",
        "Oferta recomendada:",
        "¡Ideal para tu día a día!",
        "Lo más vendido en Amazon:",
        "¿Buscas calidad? Mira esto:",
        "Haz tu vida más fácil con esto:",
        "¡Aprovecha antes de que se agote!",
        "Perfecto para regalar:",
        "Miles de personas ya lo usan:",
    ]
    desc = product.get('description') or product.get('title') or ''
    hook = random.choice(hooks)
    hashtags = ""
    # Añadir hashtags según el nicho si existe
    if 'fitness' in desc.lower():
        hashtags = "#Fitness #Salud"
    elif 'cocina' in desc.lower():
        hashtags = "#Cocina #Hogar"
    elif 'tecnolog' in desc.lower() or 'tech' in desc.lower():
        hashtags = "#Tecnología #Gadgets"
    elif 'mascota' in desc.lower():
        hashtags = "#Mascotas #PetLovers"
    tweet = f"{hook} {desc} {product['url']} {hashtags}".strip()
    if len(tweet) > 270:
        tweet = tweet[:267] + '...'
    return tweet

def generate_valioso_tweet():
    # Selecciona un tip/valor no repetido
    disponibles = [t for t in contenido_valioso if t not in posted_tweets['valiosos']]
    if not disponibles:
        posted_tweets['valiosos'] = []
        disponibles = contenido_valioso[:]
    tweet = random.choice(disponibles)
    posted_tweets['valiosos'].append(tweet)
    save_posted_tweets()
    return tweet

def post_tweet_v2_direct(text):
    """Publica tweet directamente con la API v2 usando OAuth 1.0a."""
    # Endpoint para publicar tweets (API v2)
    endpoint = "https://api.twitter.com/2/tweets"
    
    # Parámetros para OAuth 1.0a
    oauth_consumer_key = TWITTER_API_KEY
    oauth_token = TWITTER_ACCESS_TOKEN
    oauth_signature_method = "HMAC-SHA1"
    oauth_timestamp = str(int(time.time()))
    oauth_nonce = uuid.uuid4().hex
    oauth_version = "1.0"
    
    # Preparar el cuerpo de la solicitud
    request_body = json.dumps({"text": text})
    
    # Parámetros para la firma
    parameter_string = "&".join([
        f"oauth_consumer_key={oauth_consumer_key}",
        f"oauth_nonce={oauth_nonce}",
        f"oauth_signature_method={oauth_signature_method}",
        f"oauth_timestamp={oauth_timestamp}",
        f"oauth_token={oauth_token}",
        f"oauth_version={oauth_version}"
    ])
    
    # Base string para firmar
    base_string = f"POST&{urllib.parse.quote(endpoint, safe='')}&{urllib.parse.quote(parameter_string, safe='')}"
    
    # Clave para firmar
    signing_key = f"{urllib.parse.quote(TWITTER_API_SECRET, safe='')}&{urllib.parse.quote(TWITTER_ACCESS_TOKEN_SECRET, safe='')}"
    
    # Calcular firma
    signature = base64.b64encode(
        hmac.new(
            signing_key.encode(),
            base_string.encode(),
            hashlib.sha1
        ).digest()
    ).decode()
    
    # Cabecera de autorización
    auth_header = (
        f'OAuth oauth_consumer_key="{oauth_consumer_key}", '
        f'oauth_token="{oauth_token}", '
        f'oauth_signature_method="{oauth_signature_method}", '
        f'oauth_timestamp="{oauth_timestamp}", '
        f'oauth_nonce="{oauth_nonce}", '
        f'oauth_version="{oauth_version}", '
        f'oauth_signature="{urllib.parse.quote(signature, safe="")}"'
    )
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    # Enviar solicitud
    response = requests.post(endpoint, headers=headers, data=request_body)
    
    # Analizar respuesta
    if response.status_code == 201:
        return response.json().get('data', {}).get('id'), None
    else:
        return None, f"{response.status_code} - {response.text}"

def post_to_twitter(tweet, tipo="promocional"):
    import time
    max_retries = 3
    retry_wait = 60  # 1 minuto entre intentos normales
    backoff_429 = 15 * 60  # 15 minutos si hay error 429
    for attempt in range(max_retries):
        tweet_id, error = post_tweet_v2_direct(tweet)
        if tweet_id:
            print(f"Tuit publicado: {tweet}")
            print(f"URL: https://twitter.com/i/web/status/{tweet_id}")
            if tipo == "promocional":
                posted_tweets['promocionales'].append(tweet_id)
            elif tipo == "valioso":
                posted_tweets['valiosos'].append(tweet)
            save_posted_tweets()
            registrar_tweet_stat(tweet, tipo, tweet_id)
            return tweet_id
        else:
            print(f"Error al publicar tuit: {error}")
            if error and "429" in error:
                print("[Twitter] Límite alcanzado. Esperando 15 minutos antes de reintentar...")
                time.sleep(backoff_429)
            else:
                print(f"[Twitter] Esperando {retry_wait} segundos antes de reintentar...")
                time.sleep(retry_wait)
    print("[Twitter] No se pudo publicar el tuit tras varios intentos.")
    return None

def retweet_influencer(influencer_screen_name):
    print(f"Función de retweet no implementada para {influencer_screen_name}")
    print("Twitter API Free solo permite publicar tweets propios, no retweets")
    return None

def registrar_tweet_stat(texto, tipo, tweet_id):
    # Guarda un registro simple de cada tuit publicado
    if os.path.exists(TWEET_STATS_FILE):
        with open(TWEET_STATS_FILE, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    else:
        stats = []
    stats.append({
        "fecha": datetime.now().isoformat(),
        "tipo": tipo,
        "tweet_id": tweet_id,
        "texto": texto[:100]
    })
    save_tweet_stats(stats)

def publicar_batch_diario():
    # Determina cuántos tuits de cada tipo publicar
    # En plan Free estamos limitados a 500 escritos por mes, así que vamos a ser conservadores
    total = random.randint(10, 15)  # 10-15 tweets al día = 300-450 al mes (por debajo del límite de 500)
    n_promos = int(total * random.uniform(0.5, 0.6))
    n_valiosos = total - n_promos  # Eliminamos retweets ya que la API gratuita no los permite fácilmente
    
    print(f"Iniciando publicación diaria: {total} tuits ({n_promos} promocionales, {n_valiosos} valiosos)")
    
    # Publicar promocionales
    for i in range(n_promos):
        niche = random.choice(NICHES)
        fallback_niches = [n for n in NICHES if n != niche]
        products = get_amazon_products(niche, fallback_niches=fallback_niches)
        random.shuffle(products)
        
        # Buscar un producto válido que no se haya publicado aún
        valid_product_found = False
        for product in products:
            if product['asin'] not in posted_products:
                # Verificar que la URL de Amazon es válida
                if is_valid_amazon_url(product['url']):
                    tweet = generate_tweet(product)
                    post_to_twitter(tweet, tipo="promocional")
                    posted_products.add(product['asin'])
                    save_posted_products()
                    valid_product_found = True
                    break
                else:
                    print(f"Producto con ASIN {product['asin']} descartado - URL inválida")
        
        if not valid_product_found:
            print(f"No se encontró ningún producto válido para el nicho {niche}")
        
        if i < n_promos - 1:  # No esperar después del último
            time.sleep(random.randint(300, 900))  # Espaciar 5-15 minutos entre tweets
    
    # Publicar valiosos
    for i in range(n_valiosos):
        tweet = generate_valioso_tweet()
        post_to_twitter(tweet, tipo="valioso")
        if i < n_valiosos - 1:  # No esperar después del último
            time.sleep(random.randint(300, 900))  # Espaciar 5-15 minutos entre tweets
    
    print("Batch diario completado")

def main():
    publicar_batch_diario()

def run_estrategia():
    # Loop 24/7, ejecuta batch diario sin restricción de horario
    while True:
        main()
        # Espera 24 horas antes de volver a publicar
        print(f"Esperando 24 horas hasta el próximo batch... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(24 * 60 * 60)

def verify_amazon_url(url):
    """
    [OBSOLETO] Verifica si una URL de Amazon es válida (el producto existe).
    Ahora redirige a is_valid_amazon_url de amazon_dynamic.py para validación robusta.
    """
    return is_valid_amazon_url(url)

if __name__ == "__main__":
    print(f"Iniciando bot Amazon Afiliados + Twitter... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    run_estrategia()
