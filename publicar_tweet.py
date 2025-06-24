import os
import json
import random
import tweepy
from dotenv import load_dotenv
import tweet_guard

# Cargar variables de entorno
load_dotenv()

# Credenciales Twitter OAuth1.0a (permitidas para escritura en plan Free)
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# ID de afiliado Amazon
AMAZON_ASSOCIATE_TAG = os.getenv('AMAZON_ASSOCIATE_TAG')

def get_random_product(niche):
    """Genera un producto aleatorio simulado."""
    return {
        'asin': f'ASIN{niche}1',
        'title': f'Producto 1 de {niche}',
        'url': f'https://www.amazon.com/dp/ASIN{niche}1/?tag={AMAZON_ASSOCIATE_TAG}',
        'description': f'¡Descubre este increíble producto para {niche}! Ideal para quienes buscan calidad y funcionalidad 👍 #Amazon'
    }

def generate_tweet(product):
    """Genera el texto del tweet con el enlace afiliado."""
    desc = product['description'][:180]
    tweet = f"{desc} {product['url']}"
    if len(tweet) > 270:  # Twitter permite hasta 280 caracteres
        tweet = tweet[:267] + '...'
    return tweet

def post_tweet_v1(tweet_text):
    """Publica un tweet usando la API v1.1 a través de OAuth 1.0a."""
    try:
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
        )
        api = tweepy.API(auth)
        
        # La función legacy para publicar tweets
        result = api.update_status(tweet_text)
        return result.id, None
    except Exception as e:
        return None, str(e)

def main():
    """Función principal para publicar un tweet de prueba."""
    # Lista de nichos disponibles
    niches = ["fitness", "cocina", "gaming", "mascotas", "tecnología", "salud", "viajes"]
    
    # Seleccionar un nicho aleatorio
    niche = random.choice(niches)
    print(f"Seleccionado nicho: {niche}")
    
    # Obtener un producto para ese nicho
    product = get_random_product(niche)
    
    # Generar el tweet
    tweet_text = generate_tweet(product)
    print(f"\nContenido del tweet:\n{tweet_text}\n")
    
    # Confirmar antes de publicar
    confirm = input("¿Quieres publicar este tweet? (s/n): ").lower().strip()
    
    if confirm == 's':
        if tweet_guard.is_duplicate(tweet_text):
            print("ADVERTENCIA: Este tweet ya fue publicado antes. No se publicará de nuevo.")
            return
        # Publicar usando la API v1.1 (disponible en plan Free)
        tweet_id, error = post_tweet_v1(tweet_text)
        
        if tweet_id:
            print(f"\n¡Éxito! Tweet publicado con ID: {tweet_id}")
            print(f"Puedes verlo en: https://twitter.com/i/web/status/{tweet_id}")
            tweet_guard.register_tweet(tweet_text)
        else:
            print(f"\nError al publicar tweet: {error}")
            print("Comprueba que tus credenciales en .env son correctas y que tienes permisos de escritura.")
    else:
        print("Publicación cancelada.")

if __name__ == "__main__":
    print("=== Bot de Amazon Afiliados - Test de Publicación ===")
    main()
