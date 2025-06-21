import os
from bot import get_amazon_products

# Mostrar información de todos los nichos disponibles
niches = ["fitness", "cocina", "gaming", "mascotas", "tecnología", "salud", "viajes"]
tag = os.getenv('AMAZON_ASSOCIATE_TAG') or 'nosoymexa-20'

print("=== CATÁLOGO DE PRODUCTOS PARA BOT AMAZON AFILIADOS ===")
print(f"ID de Afiliado: {tag}")
print("-" * 60)

total_productos = 0

for niche in niches:
    print(f"\n>> NICHO: {niche.upper()}")
    productos = get_amazon_products(niche, max_results=2)
    
    for i, p in enumerate(productos, 1):
        print(f"  {i}. {p['title']}")
        print(f"     ASIN: {p['asin']}")
        print(f"     URL: {p['url']}")
        print(f"     Descripción: {p['description'][:50]}...")
    
    total_productos += len(productos)

print("\n" + "=" * 60)
print(f"Total: {total_productos} productos en {len(niches)} nichos")
print("=" * 60)
print("\nTodo está listo para usar el bot completo con productos reales.")
print("Puedes ejecutarlo con: python bot.py")