from amazon_dynamic import get_viral_product_for_niche, get_trending_hashtags
from bot import post_tweet_v2_direct
import random
import time
import logging

# Configuración de logging detallado
def setup_logger():
    logger = logging.getLogger("tweetbot")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("tweetbot.log", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger

logger = setup_logger()

# Nichos disponibles
NICHES = [
    "fitness",
    "cocina",
    "gaming",
    "mascotas",
    "tecnología",
    "salud",
    "viajes"
]

# Frases de llamada a la acción y urgencia
CALLS_TO_ACTION = [
    "¡No te lo pierdas!",
    "Oferta limitada 🚨",
    "¡Solo por hoy!",
    "Aprovecha antes de que se agote",
    "Miles ya lo están comprando",
    "¡Haz clic y súmate a la tendencia!",
    "Recomendado por expertos",
    "El favorito de Amazon ⭐",
    "¡Ideal para ti!",
    "Top ventas del mes"
]

EMOJIS = ["🔥", "💥", "🚀", "⭐", "✅", "🛒", "💡", "🎯", "💸", "📦"]

# 1. Seleccionar nicho aleatorio
niche = random.choice(NICHES)
logger.info(f"Nicho seleccionado: {niche}")
print(f"Nicho seleccionado: {niche}")

# 2. Analizar tendencia y buscar producto viral
logger.info("Buscando producto viral y tendencia...")
print("Buscando producto viral y tendencia...")
product = get_viral_product_for_niche(niche)

# 3. Generar tweet optimizado
if product:
    cta = random.choice(CALLS_TO_ACTION)
    emoji = random.choice(EMOJIS)
    hashtags = get_trending_hashtags(niche, max_tags=3)
    hashtags_str = ' '.join(hashtags)
    frases_venta = [
        "¡Aprovecha esta oportunidad única!",
        "Miles de personas ya lo compraron, ¿y tú?",
        "Transforma tu vida con este producto top.",
        "¡Haz clic y descubre por qué es tendencia!",
        "No dejes pasar la mejor oferta del mes.",
        "¡El favorito de los expertos y usuarios!"
    ]
    frase_venta = random.choice(frases_venta)
    tweet = (
        f"{emoji} {cta}\n"
        f"[{niche.upper()}] {product['title']}\n"
        f"{product['description']}\n"
        f"{frase_venta}\n"
        f"Compra aquí ➡️ {product['url']}\n"
        f"{hashtags_str}"
    )
    if len(tweet) > 270:
        tweet = tweet[:267] + '...'
    logger.info(f"Tweet generado: {tweet}")
    print("\n--- Tweet generado ---\n")
    print(tweet)

    # 4. Confirmar publicación
    confirm = input("¿Quieres publicar este tweet? (s/n): ").lower().strip()
    if confirm == 's':
        print("\nPublicando en Twitter...")
        tweet_id, error = post_tweet_v2_direct(tweet)
        if tweet_id:
            logger.info(f"Tweet publicado con éxito: https://twitter.com/i/web/status/{tweet_id}")
            print(f"¡Éxito! Tweet publicado con ID: {tweet_id}")
            print(f"URL: https://twitter.com/i/web/status/{tweet_id}")
        else:
            logger.error(f"Error al publicar: {error}")
            print(f"Error al publicar: {error}")
    else:
        print("Publicación cancelada.")
else:
    logger.warning("No se encontró producto viral para este nicho.")
    print("No se encontró producto viral para este nicho.")
