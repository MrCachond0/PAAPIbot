import random
from bot import post_tweet_v2_direct, get_amazon_products, generate_tweet

# Seleccionemos un nicho
niche = random.choice(["fitness", "cocina", "gaming", "mascotas", "tecnología", "salud", "viajes"])
print(f"Nicho seleccionado: {niche}")

# Obtener productos reales para ese nicho
productos = get_amazon_products(niche)
producto = random.choice(productos)

# Generar tweet con el producto
tweet_text = generate_tweet(producto)

print(f"Producto: {producto['title']}")
print(f"\nTweet a publicar:")
print(f"{tweet_text}")

# Confirmar
confirm = input("\n¿Quieres publicar este tweet? (s/n): ").lower()
if confirm == "s":
    tweet_id, error = post_tweet_v2_direct(tweet_text)
    
    if tweet_id:
        print(f"\n¡Éxito! Tweet publicado con ID: {tweet_id}")
        print(f"URL: https://twitter.com/i/web/status/{tweet_id}")
        print(f"Enlace de afiliado: {producto['url']}")
    else:
        print(f"Error al publicar: {error}")
else:
    print("Publicación cancelada")
