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

def verify_amazon_url(url):
    """
    Verifica si una URL de Amazon es válida (el producto existe)
    Retorna True si es válida, False si no lo es
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        
        # Si la respuesta es 200, el producto existe
        if response.status_code == 200:
            return True
        # Si la respuesta es 404, el producto no existe
        elif response.status_code == 404:
            print(f"⚠️ URL inválida (404): {url}")
            return False
        # Para otros códigos, asumimos un error y continuamos
        else:
            print(f"⚠️ Código de estado desconocido para {url}: {response.status_code}")
            return True  # Seguimos para no bloquear el bot
    except Exception as e:
        print(f"Error al verificar URL {url}: {e}")
        return True  # Seguimos para no bloquear el bot

def get_amazon_products(niche, max_results=10):
    """
    Genera productos de Amazon con URLs reales para cada nicho.
    En la versión final esto debería usar la API de Amazon, pero por ahora usamos
    URLs reales predefinidas.
    """
    # Catálogo de productos reales por nicho
    catalogo = {
        "fitness": [
            {
                'asin': 'B084P72GYX',
                'title': 'Bandas Elásticas de Resistencia',
                'url': f'https://www.amazon.com/dp/B084P72GYX/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': '¡Mejora tu entrenamiento en casa con estas bandas de resistencia de alta calidad! Ideales para todo tipo de ejercicios 💪 #Fitness'
            },
            {
                'asin': 'B07G8TTRDZ',
                'title': 'Pulsera de Actividad Inteligente',
                'url': f'https://www.amazon.com/dp/B07G8TTRDZ/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Monitoriza tu actividad diaria, ritmo cardíaco y sueño con esta pulsera fitness. ¡La motivación que necesitas para estar en forma! 🏃‍♀️ #Fitness'
            },
            {
                'asin': 'B07VFPYNPG',
                'title': 'Guantes de Entrenamiento Premium',
                'url': f'https://www.amazon.com/dp/B07VFPYNPG/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Protege tus manos y mejora tu agarre con estos guantes de entrenamiento transpirables. Perfectos para pesas y crossfit 🏋️‍♂️ #Fitness'
            },
            {
                'asin': 'B093LGSVGM',
                'title': 'Mancuernas Ajustables Profesionales',
                'url': f'https://www.amazon.com/dp/B093LGSVGM/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Entrena con diferentes pesos usando estas mancuernas ajustables. Ahorra espacio y dinero con este sistema todo en uno 💯 #Fitness'
            },
            {
                'asin': 'B08HVZRYB3',
                'title': 'Colchoneta de Ejercicios Premium',
                'url': f'https://www.amazon.com/dp/B08HVZRYB3/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Colchoneta antideslizante para yoga, pilates y ejercicios en casa. Máxima comodidad para tus entrenamientos diarios 🧘‍♀️ #Fitness'
            },
        ],
        "cocina": [
            {
                'asin': 'B08L73XC6W',
                'title': 'Olla Programable Multifunción',
                'url': f'https://www.amazon.com/dp/B08L73XC6W/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Prepara deliciosas recetas en minutos con esta olla programable. 10 funciones en un solo aparato para revolucionar tu cocina 🍲 #Cocina'
            },
            {
                'asin': 'B08TWW58LH',
                'title': 'Sartén Antiadherente de Titanio',
                'url': f'https://www.amazon.com/dp/B08TWW58LH/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Cocina más saludable con esta sartén de última tecnología. Sin PFOA, resistente a rayones y compatible con inducción 🍳 #Cocina'
            },
            {
                'asin': 'B07S3NP4H1',
                'title': 'Set de Cuchillos Profesionales',
                'url': f'https://www.amazon.com/dp/B07S3NP4H1/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Set de cuchillos de acero inoxidable con hoja afilada y mango ergonómico. El compañero perfecto para tus creaciones culinarias 🔪 #Cocina'
            },
            {
                'asin': 'B07WNLQ1FX',
                'title': 'Procesador de Alimentos Compacto',
                'url': f'https://www.amazon.com/dp/B07WNLQ1FX/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Pica, tritura y mezcla en segundos con este procesador potente y compacto. Ideal para preparaciones rápidas en tu día a día 🥗 #Cocina'
            },
            {
                'asin': 'B089DNGYJ8',
                'title': 'Báscula Digital de Precisión',
                'url': f'https://www.amazon.com/dp/B089DNGYJ8/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Mide con precisión tus ingredientes con esta báscula digital. Imprescindible para repostería y dietas controladas ⚖️ #Cocina'
            },
        ],
        "gaming": [
            {
                'asin': 'B07NSSZCZQ',
                'title': 'Auriculares Gaming con Micrófono',
                'url': f'https://www.amazon.com/dp/B07NSSZCZQ/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Sumérgete en tus juegos con estos auriculares con sonido envolvente y micrófono de alta definición. ¡Escucha cada detalle! 🎮 #Gaming'
            },
            {
                'asin': 'B08L5CKPF3',
                'title': 'Ratón Gaming RGB Programable',
                'url': f'https://www.amazon.com/dp/B08L5CKPF3/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Mejora tu precisión con este ratón gaming de alta sensibilidad. 8 botones programables y luces RGB personalizables 🖱️ #Gaming'
            },
            {
                'asin': 'B08FMNXX68',
                'title': 'Teclado Mecánico RGB para Gaming',
                'url': f'https://www.amazon.com/dp/B08FMNXX68/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Disfruta de la respuesta táctil de este teclado mecánico con retroiluminación RGB. Perfecto para gaming y trabajo 💻 #Gaming'
            },
            {
                'asin': 'B08DRQ966G',
                'title': 'Alfombrilla Gaming XXL con RGB',
                'url': f'https://www.amazon.com/dp/B08DRQ966G/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Alfombrilla extra grande con iluminación RGB para tu setup gaming. Superficie óptima para máxima precisión en tus juegos 🔥 #Gaming'
            },
            {
                'asin': 'B07TB94DR3',
                'title': 'Silla Gaming Ergonómica Premium',
                'url': f'https://www.amazon.com/dp/B07TB94DR3/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Juega cómodamente durante horas con esta silla gaming ergonómica. Soporte lumbar, reposabrazos ajustables y materiales premium 👑 #Gaming'
            },
        ],
        "mascotas": [
            {
                'asin': 'B07X2RJ96V',
                'title': 'Cama Ortopédica para Perros',
                'url': f'https://www.amazon.com/dp/B07X2RJ96V/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Dale a tu perro el descanso que merece con esta cama ortopédica. Alivia dolores articulares y mejora el sueño de tu mascota 🐕 #Mascotas'
            },
            {
                'asin': 'B07DKW95JC',
                'title': 'Juguete Interactivo para Gatos',
                'url': f'https://www.amazon.com/dp/B07DKW95JC/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Mantén a tu gato activo y entretenido con este juguete interactivo. Estimula su instinto cazador y reduce el estrés 🐱 #Mascotas'
            },
            {
                'asin': 'B08FR3SVS9',
                'title': 'Transportín Plegable para Mascotas',
                'url': f'https://www.amazon.com/dp/B08FR3SVS9/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Transportín seguro y cómodo para llevar a tu mascota al veterinario o de viaje. Fácil de montar y guardar 🧳 #Mascotas'
            },
            {
                'asin': 'B08MTXZH1J',
                'title': 'Bebedero Automático para Mascotas',
                'url': f'https://www.amazon.com/dp/B08MTXZH1J/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Mantén a tu mascota hidratada con este bebedero automático de gran capacidad. Filtro incluido para agua siempre fresca y limpia 💧 #Mascotas'
            },
            {
                'asin': 'B08NFK98H8',
                'title': 'Cortauñas Profesional para Mascotas',
                'url': f'https://www.amazon.com/dp/B08NFK98H8/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Cortauñas seguro con sensor para evitar cortes excesivos. Cuida las patas de tu mascota como un profesional ✂️ #Mascotas'
            },
        ],
        "tecnología": [
            {
                'asin': 'B094DQPQP8',
                'title': 'Auriculares Inalámbricos con Cancelación de Ruido',
                'url': f'https://www.amazon.com/dp/B094DQPQP8/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Disfruta de tu música favorita sin distracciones con estos auriculares con cancelación de ruido. 30h de batería y sonido premium 🎧 #Tecnología'
            },
            {
                'asin': 'B08L5W6Y8N',
                'title': 'Power Bank 20000mAh de Carga Rápida',
                'url': f'https://www.amazon.com/dp/B08L5W6Y8N/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Nunca te quedes sin batería con este power bank de alta capacidad y carga rápida. Compatible con todos tus dispositivos 🔋 #Tecnología'
            },
            {
                'asin': 'B096BJLMGC',
                'title': 'Smartwatch con Monitor de Salud',
                'url': f'https://www.amazon.com/dp/B096BJLMGC/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Controla tu actividad, sueño y salud con este smartwatch completo. Notificaciones, GPS y más de 100 modos deportivos ⌚ #Tecnología'
            },
            {
                'asin': 'B0B2CP8BNK',
                'title': 'Altavoz Bluetooth Portátil Resistente al Agua',
                'url': f'https://www.amazon.com/dp/B0B2CP8BNK/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Lleva tu música a todas partes con este altavoz bluetooth resistente al agua. 24h de autonomía y sonido envolvente 360° 🔊 #Tecnología'
            },
            {
                'asin': 'B09FKGJ1TB',
                'title': 'Cargador Inalámbrico Rápido 15W',
                'url': f'https://www.amazon.com/dp/B09FKGJ1TB/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Carga tus dispositivos sin cables con este cargador rápido compatible con iOS y Android. Diseño elegante y compacto ⚡ #Tecnología'
            },
        ],
        "salud": [
            {
                'asin': 'B08FC5L3RG',
                'title': 'Masajeador de Cuello con Calor',
                'url': f'https://www.amazon.com/dp/B08FC5L3RG/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Alivia dolores y tensiones con este masajeador cervical con función de calor. Ideal tras largas jornadas de trabajo o estudio 💆‍♂️ #Salud'
            },
            {
                'asin': 'B0877CXHNF',
                'title': 'Báscula Inteligente con Análisis Corporal',
                'url': f'https://www.amazon.com/dp/B0877CXHNF/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Controla tu peso y composición corporal con esta báscula smart. Sincroniza con tu smartphone y analiza 17 métricas diferentes ⚖️ #Salud'
            },
            {
                'asin': 'B08GSQXLB5',
                'title': 'Purificador de Aire con Filtro HEPA',
                'url': f'https://www.amazon.com/dp/B08GSQXLB5/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Respira aire más limpio con este purificador con filtro HEPA. Elimina alérgenos, polvo y olores para un hogar más saludable 🌬️ #Salud'
            },
            {
                'asin': 'B08FSZ5GRB',
                'title': 'Tensiómetro de Brazo Digital',
                'url': f'https://www.amazon.com/dp/B08FSZ5GRB/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Controla tu presión arterial cómodamente desde casa con este tensiómetro digital de alta precisión y fácil uso 💓 #Salud'
            },
            {
                'asin': 'B085XDYY17',
                'title': 'Cepillo de Dientes Eléctrico Sónico',
                'url': f'https://www.amazon.com/dp/B085XDYY17/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Logra una limpieza profesional con este cepillo eléctrico sónico. Elimina hasta 10 veces más placa que un cepillo manual ✨ #Salud'
            },
        ],
        "viajes": [
            {
                'asin': 'B07RM5D4XV',
                'title': 'Maleta de Cabina Ultraligera',
                'url': f'https://www.amazon.com/dp/B07RM5D4XV/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Viaja sin preocupaciones con esta maleta de cabina ultraligera y resistente. Cumple con las medidas de todas las aerolíneas ✈️ #Viajes'
            },
            {
                'asin': 'B07F1RY2XW',
                'title': 'Set de Organizadores de Equipaje',
                'url': f'https://www.amazon.com/dp/B07F1RY2XW/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Mantén tu ropa y accesorios perfectamente organizados con este set de 7 cubos de embalaje. Maximiza el espacio en tu maleta 🧳 #Viajes'
            },
            {
                'asin': 'B07WNPPWW4',
                'title': 'Almohada de Viaje Cervical Ergonómica',
                'url': f'https://www.amazon.com/dp/B07WNPPWW4/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Descansa cómodamente durante tus viajes con esta almohada cervical de memory foam. Evita dolores de cuello y disfruta del trayecto 😴 #Viajes'
            },
            {
                'asin': 'B07S36P9DS',
                'title': 'Adaptador Universal de Viaje',
                'url': f'https://www.amazon.com/dp/B07S36P9DS/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Conecta tus dispositivos en cualquier país con este adaptador universal compatible con más de 150 países. Incluye puertos USB 🔌 #Viajes'
            },
            {
                'asin': 'B071X4RZ79',
                'title': 'Báscula Digital para Maletas',
                'url': f'https://www.amazon.com/dp/B071X4RZ79/?tag={AMAZON_ASSOCIATE_TAG}',
                'description': 'Evita sobrecostes por exceso de equipaje con esta báscula digital portátil. Precisa, ligera y fácil de usar antes de cada viaje ⚖️ #Viajes'
            },
        ],
    }
    # Si el nicho no existe en nuestro catálogo, usa uno aleatorio
    if niche not in catalogo:
        niche = random.choice(list(catalogo.keys()))
        
    # Devuelve el catálogo para ese nicho
    productos = catalogo[niche]
    
    # Si no hay suficientes productos, duplica los existentes
    while len(productos) < max_results:
        productos = productos + productos
        
    # Limita al máximo solicitado
    return productos[:max_results]

def generate_tweet(product):
    desc = product['description'][:180]
    tweet = f"{desc} {product['url']}"
    if len(tweet) > 270:  # Twitter permite hasta 280 caracteres
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
    tweet_id, error = post_tweet_v2_direct(tweet)
    
    if tweet_id:
        print(f"Tuit publicado: {tweet}")
        print(f"URL: https://twitter.com/i/web/status/{tweet_id}")
        
        # Guardar ID para evitar repeticiones
        if tipo == "promocional":
            posted_tweets['promocionales'].append(tweet_id)
        elif tipo == "valioso":
            posted_tweets['valiosos'].append(tweet)
        save_posted_tweets()
        
        # Registrar estadística básica
        registrar_tweet_stat(tweet, tipo, tweet_id)
        return tweet_id
    else:
        print(f"Error al publicar tuit: {error}")
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
        products = get_amazon_products(niche)
        random.shuffle(products)
        
        # Buscar un producto válido que no se haya publicado aún
        valid_product_found = False
        for product in products:
            if product['asin'] not in posted_products:
                # Verificar que la URL de Amazon es válida
                if verify_amazon_url(product['url']):
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

if __name__ == "__main__":
    print(f"Iniciando bot Amazon Afiliados + Twitter... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    run_estrategia()
