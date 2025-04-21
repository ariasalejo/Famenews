from flask import Flask, request, jsonify, send_file
from flask_caching import Cache
import requests
import xmltodict

# --- Configuración de la aplicación Flask ---
app = Flask(__name__)

# Configuración de la caché (usa memoria; en producción, puedes usar Redis o FileSystemCache)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Tiempo de vida de la caché en segundos (5 minutos)
cache = Cache(app)

# --- Funciones auxiliares ---

def get_rss_feed(url: str) -> list:
    """
    Obtiene y analiza un feed RSS desde una URL.
    Retorna una lista de noticias en formato dict.
    """
    try:
        response = requests.get(url, timeout=10)  # Timeout para prevenir bloqueos
        response.raise_for_status()  # Lanza error si la respuesta tiene status 4xx/5xx
        data = xmltodict.parse(response.content)

        # Extraer artículos del feed RSS (RSS 2.0 estándar)
        items = data.get('rss', {}).get('channel', {}).get('item', [])
        if not isinstance(items, list):
            items = [items]  # Convertir a lista si hay un solo artículo

        # Procesar los datos y limpiar resultados
        news_list = []
        for item in items:
            news_item = {
                'title': item.get('title', 'No title available'),
                'description': item.get('description', 'No description available'),
                'link': item.get('link', '#'),
                'pubDate': item.get('pubDate', 'Unknown'),
                'image_url': (
                    item.get('enclosure', {}).get('@url') or  # Imagen estándar
                    item.get('media:content', {}).get('@url') or  # Alternativa en media
                    None
                ),
                'author': item.get('author') or item.get('dc:creator', 'Unknown Author')
            }
            news_list.append(news_item)

        return news_list

    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return []  # Retorna lista vacía si ocurre un error
    except Exception as e:
        print(f"Error parsing RSS feed: {e}")
        return []

# --- Rutas del servidor ---

@app.route('/')
def index():
    """
    Sirve el archivo HTML principal.
    """
    try:
        return send_file('index.html')
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "index.html not found"}), 404

@app.route('/api/rss_news')
@cache.cached(timeout=300, query_string=True)  # Activa caché según parámetros GET
def rss_news_api():
    """
    Endpoint para obtener noticias desde un feed RSS.
    """
    rss_url = request.args.get('url')
    if not rss_url:
        return jsonify({"status": "error", "message": "Missing 'url' parameter"}), 400

    news_items = get_rss_feed(rss_url)
    if not news_items:
        return jsonify({"status": "error", "message": "Could not fetch or parse RSS feed"}), 500

    return jsonify({
        "status": "ok",
        "total_hits": len(news_items),
        "articles": news_items
    })

@app.route('/clear_cache')
def clear_cache():
    """
    Endpoint para limpiar la caché manualmente.
    """
    cache.clear()
    return jsonify({"status": "ok", "message": "Cache cleared!"})

# --- Inicio del servidor ---
if __name__ == '__main__':
    app.run(debug=True)
