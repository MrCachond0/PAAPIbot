import random
from bot import post_tweet_v2_direct

# Textos de ejemplo para probar
sample_tweets = [
    "¡Bienvenidos a mi canal de afiliados! Compartiré productos increíbles con ustedes 🔥 #Amazon #Afiliados",
    "Estoy emocionado de iniciar este viaje compartiendo recomendaciones de productos que realmente valen la pena. ¡Sígueme para descubrir más! #Amazon",
    "¿Buscas reviews honestas de productos? Te ayudaré a encontrar lo mejor para tus necesidades #ProductReviews #Amazon"
]

# Seleccionar un tweet aleatorio
tweet_text = random.choice(sample_tweets)
print(f"Enviando tweet de prueba: {tweet_text}")

# Publicar tweet
tweet_id, error = post_tweet_v2_direct(tweet_text)

if tweet_id:
    print(f"¡Éxito! Tweet publicado con ID: {tweet_id}")
    print(f"URL: https://twitter.com/i/web/status/{tweet_id}")
else:
    print(f"Error: {error}")
