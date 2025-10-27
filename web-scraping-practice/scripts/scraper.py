import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_rating_number(rating_class):
    # Convierte la clase de rating a número
    ratings = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    return ratings.get(rating_class, 0)

def scrape_books(num_pages=5):
    # Extrae información de libros de múltiples páginas
    #Args:
    #    num_pages: Número de páginas a scrapear
    #Returns:
    #    DataFrame con la información de los libros

    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    all_books = []
    
    print(f"Iniciando scraping de {num_pages} páginas...")
    
    for page in range(1, num_pages + 1):
        url = base_url.format(page)
        print(f"Scrapeando página {page}...")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontrar todos los libros en la página
            books = soup.find_all('article', class_='product_pod')
            
            for book in books:
                # Extraer título
                title = book.h3.a['title']
                
                # Extraer precio
                price_text = book.find('p', class_='price_color').text
                price = float(price_text.replace('£', ''))
                
                # Extraer rating
                rating_class = book.find('p', class_='star-rating')['class'][1]
                rating = get_rating_number(rating_class)
                
                # Extraer disponibilidad
                availability = book.find('p', class_='instock availability').text.strip()
                
                # Extraer URL de la imagen
                img_url = book.find('img')['src']
                img_url = f"http://books.toscrape.com/{img_url.replace('../', '')}"
                
                # Extraer URL del libro
                book_url = book.h3.a['href']
                book_url = f"http://books.toscrape.com/catalogue/{book_url.replace('../', '')}"
                
                all_books.append({
                    'titulo': title,
                    'precio': price,
                    'rating': rating,
                    'disponibilidad': availability,
                    'imagen_url': img_url,
                    'libro_url': book_url
                })
            
            # Pausa para no sobrecargar el servidor
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error en página {page}: {e}")
            continue
    
    print(f"Scraping completado. Total de libros extraídos: {len(all_books)}")
    return pd.DataFrame(all_books)

def scrape_book_details(book_url):
    #Extrae detalles adicionales de un libro específico
    #Args:
    #    book_url: URL del libro
    #Returns:
    #    Diccionario con detalles del libro

    try:
        response = requests.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer categoría
        category = soup.find('ul', class_='breadcrumb').find_all('a')[2].text
        
        # Extraer descripción
        description_tag = soup.find('article', class_='product_page').find('p', recursive=False)
        description = description_tag.text if description_tag else "Sin descripción"
        
        # Extraer información de la tabla de producto
        table = soup.find('table', class_='table-striped')
        product_info = {}
        
        if table:
            rows = table.find_all('tr')
            for row in rows:
                header = row.find('th').text
                value = row.find('td').text
                product_info[header] = value
        
        return {
            'categoria': category,
            'descripcion': description,
            'upc': product_info.get('UPC', ''),
            'impuestos': product_info.get('Tax', ''),
            'stock': product_info.get('Availability', '')
        }
    
    except Exception as e:
        print(f"Error extrayendo detalles: {e}")
        return None

def main():
    # Función principal que ejecuta el scraping y guarda los datos
    # Scrapear libros básicosç
    
    print("=" * 50)
    print("INICIANDO WEB SCRAPING - BOOKS TO SCRAPE")
    print("=" * 50)
    
    df_books = scrape_books(num_pages=5)
    
    # Guardar datos básicos en CSV
    df_books.to_csv('books_data.csv', index=False, encoding='utf-8')
    print(f"\n✓ Datos guardados en 'books_data.csv'")
    
    # Crear estadísticas adicionales
    stats = {
        'total_libros': len(df_books),
        'precio_promedio': df_books['precio'].mean(),
        'precio_minimo': df_books['precio'].min(),
        'precio_maximo': df_books['precio'].max(),
        'rating_promedio': df_books['rating'].mean()
    }
    
    print("\n" + "=" * 50)
    print("ESTADÍSTICAS GENERALES")
    print("=" * 50)
    print(f"Total de libros: {stats['total_libros']}")
    print(f"Precio promedio: £{stats['precio_promedio']:.2f}")
    print(f"Precio mínimo: £{stats['precio_minimo']:.2f}")
    print(f"Precio máximo: £{stats['precio_maximo']:.2f}")
    print(f"Rating promedio: {stats['rating_promedio']:.2f}/5")
    
    # Opcional: Scrapear detalles de los primeros 10 libros
    print("\n" + "=" * 50)
    print("EXTRAYENDO DETALLES ADICIONALES (primeros 10 libros)")
    print("=" * 50)
    
    detailed_books = []
    for idx, row in df_books.head(10).iterrows():
        print(f"Procesando libro {idx + 1}/10...")
        details = scrape_book_details(row['libro_url'])
        if details:
            detailed_books.append({
                'titulo': row['titulo'],
                'precio': row['precio'],
                'rating': row['rating'],
                **details
            })
        time.sleep(0.5)
    
    if detailed_books:
        df_detailed = pd.DataFrame(detailed_books)
        df_detailed.to_csv('books_detailed.csv', index=False, encoding='utf-8')
        print(f"\n✓ Detalles guardados en 'books_detailed.csv'")
    
    print("\n" + "=" * 50)
    print("SCRAPING COMPLETADO EXITOSAMENTE")
    print("=" * 50)
    print("\nArchivos generados:")
    print("  - books_data.csv (datos básicos de todos los libros)")
    print("  - books_detailed.csv (detalles adicionales de 10 libros)")
    print("\nAhora puedes ejecutar la aplicación Streamlit con:")
    print("  streamlit run app.py")

if __name__ == "__main__":
    main()
