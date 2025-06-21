import os
import requests
from bot import verify_amazon_url, get_amazon_products
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

AMAZON_ASSOCIATE_TAG = os.getenv('AMAZON_ASSOCIATE_TAG') or 'nosoymexa-20'

def test_url_validation():
    print("=== PRUEBA DE VALIDACIÓN DE URLS DE AMAZON ===")
    
    # 1. Probamos un ASIN conocido que debería existir (Kindle Paperwhite)
    asin_valido = "B08B495319"
    url_valida = f"https://www.amazon.com/dp/{asin_valido}/?tag={AMAZON_ASSOCIATE_TAG}"
    
    print(f"Probando URL válida: {url_valida}")
    resultado = verify_amazon_url(url_valida)
    print(f"Resultado: {'✅ Válida' if resultado else '❌ Inválida'}\n")
    
    # 2. Probamos un ASIN aleatorio que probablemente no exista
    asin_invalido = "B00NOTREAL1"
    url_invalida = f"https://www.amazon.com/dp/{asin_invalido}/?tag={AMAZON_ASSOCIATE_TAG}"
    
    print(f"Probando URL inválida: {url_invalida}")
    resultado = verify_amazon_url(url_invalida)
    print(f"Resultado: {'✅ Válida' if resultado else '❌ Inválida'}\n")
    
    # 3. Ahora probamos con los ASINs del catálogo actual del bot
    print("Probando URLs del catálogo actual del bot...")
    
    nichos = ["fitness", "cocina", "gaming", "mascotas", "tecnología", "salud", "viajes"]
    resultados = {"validos": 0, "invalidos": 0}
    
    for niche in nichos:
        print(f"\nNicho: {niche}")
        productos = get_amazon_products(niche, max_results=2)
        
        for producto in productos:
            print(f"  - Probando {producto['title']} (ASIN: {producto['asin']})")
            url = producto['url']
            es_valido = verify_amazon_url(url)
            if es_valido:
                print(f"    ✅ URL válida: {url}")
                resultados["validos"] += 1
            else:
                print(f"    ❌ URL inválida: {url}")
                resultados["invalidos"] += 1
    
    # Resumen final
    print("\n=== RESUMEN DE LA PRUEBA ===")
    print(f"URLs válidas: {resultados['validos']}")
    print(f"URLs inválidas: {resultados['invalidos']}")
    
    if resultados["invalidos"] > 0:
        print("\n⚠️ Se detectaron URLs inválidas en el catálogo.")
        print("Recomendación: Ejecuta el script actualizar_catalogo.py para actualizar el catálogo con ASINs válidos.")
    else:
        print("\n✅ Todas las URLs en el catálogo son válidas.")

if __name__ == "__main__":
    test_url_validation()
