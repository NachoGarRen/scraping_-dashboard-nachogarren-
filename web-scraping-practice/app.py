import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Books Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    #Carga los datos desde el archivo CSV
    try:
        df = pd.read_csv('books_data.csv')
        return df
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo 'books_data.csv'. Por favor, ejecuta primero el script de scraping.")
        st.info("Ejecuta: `python scripts/scraper.py`")
        st.stop()

def main():
    # Título principal
    st.markdown('<h1 class="main-header">📚 Dashboard de Análisis de Libros</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Cargar datos
    df = load_data()
    
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por rating
    st.sidebar.subheader("Rating")
    rating_filter = st.sidebar.multiselect(
        "Selecciona el rating:",
        options=sorted(df['rating'].unique()),
        default=sorted(df['rating'].unique())
    )
    
    # Filtro por rango de precio
    st.sidebar.subheader("Rango de Precio")
    min_price = float(df['precio'].min())
    max_price = float(df['precio'].max())
    
    price_range = st.sidebar.slider(
        "Selecciona el rango de precio (£):",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=0.5
    )
    
    # Filtro por disponibilidad
    st.sidebar.subheader("Disponibilidad")
    availability_filter = st.sidebar.multiselect(
        "Selecciona disponibilidad:",
        options=df['disponibilidad'].unique(),
        default=df['disponibilidad'].unique()
    )
    
    # Aplicar filtros
    filtered_df = df[
        (df['rating'].isin(rating_filter)) &
        (df['precio'] >= price_range[0]) &
        (df['precio'] <= price_range[1]) &
        (df['disponibilidad'].isin(availability_filter))
    ]
    
    # Mostrar número de resultados
    st.sidebar.markdown("---")
    st.sidebar.metric("📊 Libros filtrados", len(filtered_df))
    st.sidebar.metric("📊 Total de libros", len(df))
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Precio Promedio",
            value=f"£{filtered_df['precio'].mean():.2f}",
            delta=f"{filtered_df['precio'].mean() - df['precio'].mean():.2f}"
        )
    
    with col2:
        st.metric(
            label="⭐ Rating Promedio",
            value=f"{filtered_df['rating'].mean():.2f}/5",
            delta=f"{filtered_df['rating'].mean() - df['rating'].mean():.2f}"
        )
    
    with col3:
        st.metric(
            label="💵 Precio Mínimo",
            value=f"£{filtered_df['precio'].min():.2f}"
        )
    
    with col4:
        st.metric(
            label="💵 Precio Máximo",
            value=f"£{filtered_df['precio'].max():.2f}"
        )
    
    st.markdown("---")
    
    # Gráficos
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Distribución de Precios", "⭐ Ratings", "📈 Análisis", "📋 Datos"])
    
    with tab1:
        st.subheader("Distribución de Precios de Libros")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histograma de precios
            fig_hist = px.histogram(
                filtered_df,
                x='precio',
                nbins=30,
                title="Histograma de Precios",
                labels={'precio': 'Precio (£)', 'count': 'Cantidad de Libros'},
                color_discrete_sequence=['#1f77b4']
            )
            fig_hist.update_layout(showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot de precios
            fig_box = px.box(
                filtered_df,
                y='precio',
                title="Box Plot de Precios",
                labels={'precio': 'Precio (£)'},
                color_discrete_sequence=['#ff7f0e']
            )
            st.plotly_chart(fig_box, use_container_width=True)
    
    with tab2:
        st.subheader("Análisis de Ratings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución de ratings
            rating_counts = filtered_df['rating'].value_counts().sort_index()
            fig_rating = px.bar(
                x=rating_counts.index,
                y=rating_counts.values,
                title="Distribución de Ratings",
                labels={'x': 'Rating (estrellas)', 'y': 'Cantidad de Libros'},
                color=rating_counts.values,
                color_continuous_scale='Blues'
            )
            fig_rating.update_layout(showlegend=False)
            st.plotly_chart(fig_rating, use_container_width=True)
        
        with col2:
            # Gráfico de pastel
            fig_pie = px.pie(
                values=rating_counts.values,
                names=rating_counts.index,
                title="Proporción de Ratings",
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab3:
        st.subheader("Análisis de Relación Precio-Rating")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Scatter plot precio vs rating
            fig_scatter = px.scatter(
                filtered_df,
                x='rating',
                y='precio',
                title="Relación entre Rating y Precio",
                labels={'rating': 'Rating (estrellas)', 'precio': 'Precio (£)'},
                color='rating',
                size='precio',
                hover_data=['titulo'],
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            # Precio promedio por rating
            avg_price_by_rating = filtered_df.groupby('rating')['precio'].mean().reset_index()
            fig_avg = px.line(
                avg_price_by_rating,
                x='rating',
                y='precio',
                title="Precio Promedio por Rating",
                labels={'rating': 'Rating (estrellas)', 'precio': 'Precio Promedio (£)'},
                markers=True,
                color_discrete_sequence=['#2ca02c']
            )
            st.plotly_chart(fig_avg, use_container_width=True)
        
        # Top 10 libros más caros
        st.subheader("🏆 Top 10 Libros Más Caros")
        top_expensive = filtered_df.nlargest(10, 'precio')[['titulo', 'precio', 'rating']]
        fig_top = px.bar(
            top_expensive,
            x='precio',
            y='titulo',
            orientation='h',
            title="Top 10 Libros Más Caros",
            labels={'precio': 'Precio (£)', 'titulo': 'Título'},
            color='rating',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_top, use_container_width=True)
    
    with tab4:
        st.subheader("📋 Tabla de Datos Filtrados")
        
        # Opciones de visualización
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Buscar por título:", "")
        with col2:
            sort_by = st.selectbox("Ordenar por:", ["titulo", "precio", "rating"])
        
        # Filtrar por búsqueda
        if search_term:
            display_df = filtered_df[filtered_df['titulo'].str.contains(search_term, case=False, na=False)]
        else:
            display_df = filtered_df
        
        # Ordenar
        display_df = display_df.sort_values(by=sort_by, ascending=False)
        
        # Mostrar tabla
        st.dataframe(
            display_df[['titulo', 'precio', 'rating', 'disponibilidad']],
            use_container_width=True,
            height=400
        )
        
        # Botón de descarga
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar datos filtrados (CSV)",
            data=csv,
            file_name="libros_filtrados.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>📚 Dashboard creado con Streamlit | Datos extraídos mediante Web Scraping con BeautifulSoup</p>
            <p>Fuente: <a href='http://books.toscrape.com' target='_blank'>Books to Scrape</a></p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
