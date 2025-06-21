import os
import requests
from dotenv import load_dotenv
from amazon_paapi_helper import search_amazon_items

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
    Si no hay suficientes resultados, rellena con el nicho original.
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
    # Asegura al menos una keyword
    if not keywords:
        keywords = [niche]
    return keywords[:top_n]


def get_best_seller_from_amazon(keyword):
    """
    Mejorado: Relaja los filtros. Devuelve el primer producto con título, imagen y url, priorizando Best Seller/Amazon's Choice, pero si no hay, acepta cualquier producto válido.
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
        for result in results:
            asin = result.get('data-asin')
            if not asin:
                continue
            # Filtrar patrocinados (opcional, pero menos estricto)
            sponsored = result.find('span', string=lambda s: s and 'Sponsored' in s)
            if sponsored:
                continue
            badge = result.find('span', {'class': 'a-badge-text'})
            badge_text = badge.text.strip() if badge else ''
            rating_elem = result.find('span', {'class': 'a-icon-alt'})
            try:
                rating = float(rating_elem.text.split()[0].replace(',', '.')) if rating_elem else 0
            except Exception:
                rating = 0
            reviews_elem = result.find('span', {'class': 'a-size-base'})
            try:
                reviews = int(reviews_elem.text.replace(',', '')) if reviews_elem and reviews_elem.text.replace(',', '').isdigit() else 0
            except Exception:
                reviews = 0
            title_elem = result.find('span', {'class': 'a-size-medium'})
            title = title_elem.text.strip() if title_elem else keyword
            product_url = f"https://www.amazon.com/dp/{asin}/?tag={AMAZON_ASSOCIATE_TAG}"
            desc = title
            img_elem = result.find('img', {'class': 's-image'})
            image = img_elem['src'] if img_elem else ''
            # Log de descarte
            if not (title and product_url and image):
                print(f"[Descartado] Faltan datos clave: title={bool(title)}, url={bool(product_url)}, image={bool(image)}")
                continue
            # Prioridad: Best Seller/Amazon's Choice
            if badge_text in ["Best Seller", "Amazon's Choice"]:
                print(f"[Seleccionado] Producto destacado: {title} | Badge: {badge_text}")
                return {
                    'asin': asin,
                    'title': title,
                    'url': product_url,
                    'description': desc,
                    'image': image,
                    'badge': badge_text,
                    'rating': rating,
                    'reviews': reviews
                }
        # Si no hay destacados, devolver el primer producto válido
        for result in results:
            asin = result.get('data-asin')
            if not asin:
                continue
            sponsored = result.find('span', string=lambda s: s and 'Sponsored' in s)
            if sponsored:
                continue
            title_elem = result.find('span', {'class': 'a-size-medium'})
            title = title_elem.text.strip() if title_elem else keyword
            product_url = f"https://www.amazon.com/dp/{asin}/?tag={AMAZON_ASSOCIATE_TAG}"
            img_elem = result.find('img', {'class': 's-image'})
            image = img_elem['src'] if img_elem else ''
            if title and product_url and image:
                print(f"[Seleccionado] Producto genérico: {title}")
                return {
                    'asin': asin,
                    'title': title,
                    'url': product_url,
                    'description': title,
                    'image': image
                }
        print("[Scraping] No se encontró producto válido en el HTML de Amazon.")
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
                    return {
                        'asin': asin,
                        'title': title,
                        'url': product_url,
                        'description': title,
                        'image': ''
                    }
        print("[Scraping] No se encontró producto válido en Google.")
    except Exception as e:
        print(f"[Scraping] Error en scraping Google: {e}")
    # Si scraping falla, intenta PAAPI
    print("[PAAPI] Intentando obtener producto con Product Advertising API...")
    data = search_amazon_items(keyword, item_count=1)
    if data and 'SearchResult' in data and 'Items' in data['SearchResult'] and len(data['SearchResult']['Items']) > 0:
        item = data['SearchResult']['Items'][0]
        return {
            'asin': item['ASIN'],
            'title': item['ItemInfo']['Title']['DisplayValue'],
            'url': item['DetailPageURL'],
            'description': item['ItemInfo']['Features']['DisplayValues'][0] if 'Features' in item['ItemInfo'] else '',
            'image': item['Images']['Primary']['Large']['URL'] if 'Images' in item and 'Primary' in item['Images'] else ''
        }
    return None

def get_viral_product_for_niche(niche):
    """
    Busca el producto más viral y vendible para un nicho, probando varias keywords virales.
    """
    keywords = get_trending_keywords(niche, top_n=3)
    for kw in keywords:
        product = get_best_seller_from_amazon(kw)
        if product:
            return product
    # Si no se encontró producto ideal, fallback a método original
    print("[Fallback] Usando método alternativo para encontrar producto...")
    for kw in keywords:
        # Scraping Google y PAAPI ya están en get_best_seller_from_amazon
        product = get_best_seller_from_amazon(kw)
        if product:
            return product
    return None

# Ejemplo de uso:
if __name__ == "__main__":
    niche = "fitness"
    product = get_viral_product_for_niche(niche)
    print(product)
