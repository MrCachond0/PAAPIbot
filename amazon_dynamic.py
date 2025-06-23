import os
import requests
from dotenv import load_dotenv
from amazon_paapi_helper import search_amazon_items
from scraping_utils import USER_AGENTS, PROXIES
import random

load_dotenv()

AMAZON_ACCESS_KEY = os.getenv('AMAZON_ACCESS_KEY')
AMAZON_SECRET_KEY = os.getenv('AMAZON_SECRET_KEY')
AMAZON_ASSOCIATE_TAG = os.getenv('AMAZON_ASSOCIATE_TAG')
AMAZON_PARTNER_TYPE = "Associates"
AMAZON_MARKETPLACE = "www.amazon.com"

# Puedes instalar pytrends para Google Trends: pip install pytrends
from pytrends.request import TrendReq

def get_trending_keywords(niche, top_n=3):
    """
    Devuelve una lista de las top N keywords virales del nicho usando Google Trends.
    Si no hay suficientes resultados, rellena con el nicho original y términos alternativos.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    kw_list = [niche]
    pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='US', gprop='')
    keywords = []
    try:
        related_dict = pytrends.related_queries()
        if (
            related_dict and
            niche in related_dict and
            related_dict[niche] and
            related_dict[niche]['top'] is not None and
            not related_dict[niche]['top'].empty
        ):
            keywords = related_dict[niche]['top']['query'].tolist()[:top_n]
    except Exception as e:
        print(f"[pytrends] Sin tendencias relacionadas para '{niche}': {e}")
    # Asegura al menos una keyword y agrega términos alternativos si no hay suficientes
    if not keywords:
        # Términos alternativos por nicho
        alternativos = {
            "tecnología": ["gadgets", "smart home", "wearables"],
            "salud": ["bienestar", "nutrición", "vitaminas"],
            "fitness": ["ejercicio", "deporte", "gym"],
            "cocina": ["utensilios cocina", "recetas", "electrodomésticos"],
            "gaming": ["videojuegos", "consolas", "accesorios gaming"],
            "mascotas": ["perros", "gatos", "accesorios mascotas"],
            "viajes": ["maletas", "accesorios viaje", "equipaje"]
        }
        keywords = [niche] + alternativos.get(niche, [])
    return keywords[:top_n]


def get_best_seller_from_amazon(keyword, max_attempts=10):
    """
    Devuelve el primer producto realmente disponible y válido, intentando hasta max_attempts productos distintos.
    """
    print(f"[Scraping] Buscando producto viral en Amazon para '{keyword}'...")
    try:
        from bs4 import BeautifulSoup
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        }
        url = f"https://www.amazon.com/s?k={requests.utils.quote(keyword)}"
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        # Filtrar productos realmente disponibles
        def is_available(result):
            unavailable_signals = [
                'currently unavailable', 'no disponible', 'momentáneamente no disponible',
                'not available', 'unavailable', 'momentanemente no disponible',
                'out of stock', 'agotado', 'sin stock',
                'no longer available', 'ya no está disponible',
            ]
            # Buscar texto de no disponible en el resultado
            text = result.get_text(separator=' ').lower()
            return not any(signal in text for signal in unavailable_signals)
        attempts = 0
        for result in results:
            if attempts >= max_attempts:
                break
            asin = result.get('data-asin')
            if not asin:
                continue
            sponsored = result.find('span', string=lambda s: s and 'Sponsored' in s)
            if sponsored:
                continue
            badge = result.find('span', {'class': 'a-badge-text'})
            badge_text = badge.text.strip() if badge else ''
            title_elem = result.find('span', {'class': 'a-size-medium'})
            title = title_elem.text.strip() if title_elem else keyword
            product_url = f"https://www.amazon.com/dp/{asin}/?tag={AMAZON_ASSOCIATE_TAG}"
            img_elem = result.find('img', {'class': 's-image'})
            image = img_elem['src'] if img_elem else ''
            if not (title and product_url and image and is_available(result)):
                continue
            # Validar url real
            if is_valid_amazon_url(product_url):
                print(f"[Seleccionado] Producto válido: {title}")
                return {
                    'asin': asin,
                    'title': title,
                    'url': product_url,
                    'description': title,
                    'image': image,
                    'badge': badge_text
                }
            else:
                print(f"[Descartado] Producto con ASIN {asin} por URL inválida.")
            attempts += 1
        print("[Scraping] No se encontró producto disponible y válido en el HTML de Amazon.")
    except Exception as e:
        print(f"[Scraping] Error en scraping Amazon: {e}")
    # Scraping Google (site:amazon.com ...)
    print("[Scraping] Buscando producto viral en Google (site:amazon.com)...")
    try:
        from bs4 import BeautifulSoup
        google_url = f"https://www.google.com/search?q=site:amazon.com+{requests.utils.quote(keyword)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = requests.get(google_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = soup.find_all('a')
        for link in results:
            href = link.get('href')
            if href and 'amazon.com' in href and '/dp/' in href:
                # Extraer ASIN
                import re
                m = re.search(r'/dp/([A-Z0-9]{10})', href)
                if m:
                    asin = m.group(1)
                    product_url = f"https://www.amazon.com/dp/{asin}/?tag={AMAZON_ASSOCIATE_TAG}"
                    title = link.text.strip() or keyword
                    # Validar disponibilidad real
                    if is_valid_amazon_url(product_url):
                        return {
                            'asin': asin,
                            'title': title,
                            'url': product_url,
                            'description': title,
                            'image': ''
                        }
                    else:
                        print(f"[Descartado Google] ASIN {asin} por URL inválida/no disponible.")
        print("[Scraping] No se encontró producto válido en Google.")
    except Exception as e:
        print(f"[Scraping] Error en scraping Google: {e}")
    # PAAPI
    print("[PAAPI] Intentando obtener producto con Product Advertising API...")
    data = search_amazon_items(keyword, item_count=5)
    if data and 'SearchResult' in data and 'Items' in data['SearchResult']:
        for item in data['SearchResult']['Items']:
            url = item['DetailPageURL']
            title = item['ItemInfo']['Title']['DisplayValue']
            image = item['Images']['Primary']['Large']['URL'] if 'Images' in item and 'Primary' in item['Images'] else ''
            asin = item['ASIN']
            desc = item['ItemInfo']['Features']['DisplayValues'][0] if 'Features' in item['ItemInfo'] else ''
            # Validar disponibilidad real
            if is_valid_amazon_url(url):
                return {
                    'asin': asin,
                    'title': title,
                    'url': url,
                    'description': desc,
                    'image': image
                }
            else:
                print(f"[Descartado PAAPI] ASIN {asin} por URL inválida/no disponible.")
    return None

def get_viral_product_for_niche(niche, fallback_niches=None, max_attempts=10, fallback_depth=0, max_fallback_depth=2):
    """
    Busca el producto más viral y vendible para un nicho, probando varias keywords virales y validando la URL.
    Si no encuentra producto válido, prueba con otros nichos alternativos.
    Limita la profundidad de fallbacks para evitar loops infinitos.
    """
    keywords = get_trending_keywords(niche, top_n=3)
    for kw in keywords:
        product = get_best_seller_from_amazon(kw, max_attempts=max_attempts)
        if product and is_valid_amazon_url(product['url']):
            return product
        elif product:
            print(f"[Descartado] Producto con ASIN {product['asin']} por URL inválida.")
    # Si no se encontró producto ideal, fallback a método original
    print("[Fallback] Usando método alternativo para encontrar producto...")
    for kw in keywords:
        product = get_best_seller_from_amazon(kw, max_attempts=max_attempts)
        if product and is_valid_amazon_url(product['url']):
            return product
        elif product:
            print(f"[Descartado] Producto con ASIN {product['asin']} por URL inválida.")
    # Si sigue sin encontrar, probar con otros nichos
    if fallback_niches and fallback_depth < max_fallback_depth:
        for alt_niche in fallback_niches:
            if alt_niche == niche:
                continue
            print(f"[Fallback] Probando nicho alternativo: {alt_niche}")
            product = get_viral_product_for_niche(alt_niche, max_attempts=max_attempts, fallback_depth=fallback_depth+1, max_fallback_depth=max_fallback_depth)
            if product:
                return product
    return None

def is_valid_amazon_url(url):
    """
    Verifica si una URL de Amazon es válida (status 200, contiene '/dp/' y no muestra página de error).
    Ahora detecta mensajes de error en varios idiomas y variantes comunes de Amazon.
    Usa rotación de user-agent y soporte para proxies.
    """
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS)
        }
        proxy = random.choice(PROXIES)
        proxies = {"http": proxy, "https": proxy} if proxy else None
        resp = requests.get(url, headers=headers, timeout=8, proxies=proxies)
        if resp.status_code == 200 and '/dp/' in resp.url:
            html = resp.text.lower()
            error_signals = [
                # Inglés
                "sorry, we couldn't find that page",
                "no longer available",
                "looking for something?",
                "page not found",
                "did not match any products",
                # Español
                "lo sentimos, no pudimos encontrar",
                "ya no está disponible",
                "buscando algo?",
                "página no encontrada",
                "no coincide con ningún producto",
                # Portugués
                "desculpe, não foi possível encontrar essa página",
                "não está mais disponível",
                "procurando por algo?",
                "página não encontrada",
                # Genérico
                "dogs of amazon"
            ]
            if any(signal in html for signal in error_signals):
                print(f"[URL inválida] Página de error detectada en {url}")
                return False
            return True
        else:
            print(f"[URL inválida] {url} (status: {resp.status_code})")
            return False
    except Exception as e:
        print(f"[Error validando URL] {url}: {e}")
        return False

def get_trending_hashtags(niche=None, max_tags=3):
    """
    Devuelve los primeros hashtags del top de tendencias globales usando pytrends.
    """
    try:
        pytrends = TrendReq(hl='es-MX', tz=360)
        # Tendencias globales (Google Hot Trends)
        trending_searches = pytrends.trending_searches(pn='global')
        hashtags = []
        for trend in trending_searches[0].tolist():
            tag = f"#{trend.replace(' ', '').replace('#','')}"
            if len(tag) < 25:
                hashtags.append(tag)
            if len(hashtags) >= max_tags:
                break
        if not hashtags:
            hashtags = ["#Tendencia", "#Trending", "#Viral"][:max_tags]
        return hashtags
    except Exception as e:
        print(f"[pytrends] Error obteniendo hashtags globales: {e}")
        return ["#Tendencia", "#Trending", "#Viral"][:max_tags]

# Ejemplo de uso:
if __name__ == "__main__":
    niche = "fitness"
    product = get_viral_product_for_niche(niche)
    print(product)

