import os
import json
import random
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Credenciales para OAuth 1.0a
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

def post_tweet_v2_direct(text):
    """Publica tweet directamente con la API v2 usando OAuth 1.0a."""
    import base64
    import hmac
    import hashlib
    import time
    import uuid
    import urllib.parse
    
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
    
    print("Enviando solicitud a la API v2...")
    print(f"Headers: {headers}")
    print(f"Body: {request_body}")
    
    # Enviar solicitud
    response = requests.post(endpoint, headers=headers, data=request_body)
    
    # Analizar respuesta
    if response.status_code == 201:
        return response.json().get('data', {}).get('id'), None
    else:
        return None, f"{response.status_code} - {response.text}"

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
        # Publicar usando la implementación directa de OAuth
        tweet_id, error = post_tweet_v2_direct(tweet_text)
        
        if tweet_id:
            print(f"\n¡Éxito! Tweet publicado con ID: {tweet_id}")
            print(f"Puedes verlo en: https://twitter.com/i/web/status/{tweet_id}")
        else:
            print(f"\nError al publicar tweet: {error}")
            print("Comprueba que tus credenciales en .env son correctas y que tienes permisos de escritura.")
    else:
        print("Publicación cancelada.")

if __name__ == "__main__":
    print("=== Bot de Amazon Afiliados - Test de Publicación (API v2 Directa) ===")
    main()
