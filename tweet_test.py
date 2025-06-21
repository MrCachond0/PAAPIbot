import os
import random
import tweepy
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Credenciales de OAuth1
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# ID de afiliado Amazon
AMAZON_ASSOCIATE_TAG = os.getenv('AMAZON_ASSOCIATE_TAG')

def get_amazon_products(niche, max_results=10):
    # Simulación - devuelve productos simulados
    return [
        {
            'asin': f'ASIN{niche}{i}',
            'title': f'Producto {i} de {niche}',
            'url': f'https://www.amazon.com/dp/ASIN{niche}{i}/?tag={AMAZON_ASSOCIATE_TAG}',
            'description': f'¡Descubre el producto {i} ideal para {niche}!'
        }
        for i in range(1, max_results+1)
    ]

def generate_tweet(product):
    desc = product['description'][:180]
    tweet = f"{desc} {product['url']}"
    if len(tweet) > 200:
        tweet = tweet[:197] + '...'
    return tweet

# Publicar tweet usando OAuth 1.0a
def post_tweet_oauth1(text):
    try:
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)
        status = api.update_status(text)
        print(f"Tweet publicado exitosamente con OAuth 1.0a: {text}")
        return status.id
    except Exception as e:
        print(f"Error al publicar tweet: {e}")
        return None

# Selecciona un nicho aleatorio
niche = random.choice(["fitness", "cocina", "gaming", "mascotas", "tecnología", "salud", "viajes"])
print(f"Generando tweet para nicho: {niche}")

# Obtener producto y generar tweet
products = get_amazon_products(niche)
product = products[0]  # Primer producto
tweet_text = generate_tweet(product)
print(f"Contenido del tweet: {tweet_text}")

# Publicar tweet
tweet_id = post_tweet_oauth1(tweet_text)
if tweet_id:
    print(f"¡Éxito! Tweet publicado con ID: {tweet_id}")
else:
    print("No se pudo publicar el tweet.")
