from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.responses import HTMLResponse
import os
import pandas as pd
import plotly.express as px

app = FastAPI()

# Rutas estáticas
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Plantillas
templates = Jinja2Templates(directory="templates")

# Página principal
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/conclusion")
async def conclision(request: Request):
    return templates.TemplateResponse("conclusion.html", {"request": request})

@app.get("/genero")
async def genero(request: Request):

    df = pd.read_csv("https://raw.githubusercontent.com/RodoECP/PF_Visualizacion_Datos/refs/heads/master/Peliculas.csv")
    roi_por_genero = df.groupby('genre')['ROI'].mean()

    # Crear una columna de colores, asignando verde a los valores mayores a 2.25 y rojo a los menores
    colores = ['green' if roi > 2.25 else 'red' for roi in roi_por_genero]

    # Crear gráfico de barras interactivo con los colores personalizados
    fig = px.bar(roi_por_genero,
                x=roi_por_genero.index,
                y=roi_por_genero.values,
                labels={'x': 'Género', 'y': 'ROI Promedio'},
                title='Géneros con Mayor Éxito')

    # Actualizar la propiedad de color
    fig.update_traces(marker=dict(color=colores))

    # Ajustar el tamaño de la figura
    fig.update_layout(
        width=600,  # Ancho de 600 píxeles
        height=469  # Alto de 469 píxeles
    )
    # Convertir la figura a JSON para pasarlo al frontend
    graph_html = fig.to_html()

    # Retornar la plantilla con el gráfico
    return templates.TemplateResponse("genero.html", {"request": request, "graph_html": graph_html})

@app.get("/involucrados")
async def involucrados(request: Request):
    df = pd.read_csv("https://raw.githubusercontent.com/RodoECP/PF_Visualizacion_Datos/refs/heads/master/Peliculas.csv")
    # Agrupamos y calculamos el promedio de ingresos por director
    top_directors = (
        df.groupby('director')['gross']
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    # Creamos el boxplot para los directores con colores en blanco/negro
    fig_directors_box = px.box(
        df[df['director'].isin(top_directors['director'])],  # Filtramos solo los top 10 directores
        x='director',
        y='gross',
        title='Distribución de Ingresos Brutos de los Top 10 Directores',
        labels={'gross': 'Ingresos Brutos', 'director': 'Director'},
        color='director',  # Colorear las cajas por director
        color_discrete_sequence=['black'] * len(top_directors)  # Asignar color negro a todas las cajas
    )

    # Personalizamos el diseño y ajustamos el tamaño de la figura
    fig_directors_box.update_layout(
        width=600,  # Ancho de 600 píxeles
        height=469,  # Alto de 469 píxeles
        xaxis_title='Director',
        yaxis_title='Ingresos Brutos (USD)',
        title_x=0.5,  # Centrar el título
        xaxis_tickangle=-45  # Rotar los nombres de los directores para mejor visualización
    )
    
    # Convertir la figura a html para pasarlo al frontend
    graph_html1 = fig_directors_box.to_html()

    # Agrupamos y calculamos el promedio de ingresos por actor
    top_actors = (
        df.groupby('star')['gross']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    # Creamos el boxplot para los actores con colores en blanco/negro
    fig_actors_box = px.box(
        df[df['star'].isin(top_actors['star'])],  # Filtramos solo los top 10 actores
        x='star',
        y='gross',
        title='Distribución de Ingresos Brutos de los Top 10 Actores',
        labels={'gross': 'Ingresos Brutos', 'star': 'Actor/Actriz'},
        color='star',  # Colorear las cajas por actor
        color_discrete_sequence=['black'] * len(top_actors)  # Asignar color negro a todas las cajas
    )

    # Personalizamos el diseño y ajustamos el tamaño de la figura
    fig_actors_box.update_layout(
        width=600,  # Ancho de 600 píxeles
        height=469,  # Alto de 469 píxeles
        xaxis_title='Actor/Actriz',
        yaxis_title='Ingresos Brutos (USD)',
        title_x=0.5,  # Centrar el título
        xaxis_tickangle=-45  # Rotar los nombres de los actores para mejor visualización
    )

    graph_html2 = fig_actors_box.to_html()

    # Agrupamos y calculamos el promedio de ROI por director
    top_directors_roi = (
        df.groupby('director')['ROI']
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    # Obtener los géneros asociados a cada director (tomando el género de sus películas)
    top_directors_genres = df[df['director'].isin(top_directors_roi['director'])]
    top_directors_genres = top_directors_genres.groupby('director')['genre'].apply(lambda x: ', '.join(set(x))).reset_index()

    # Unir el DataFrame de directores con los géneros
    top_directors_roi = top_directors_roi.merge(top_directors_genres, on='director', how='left')

    # Crear un mapeo de colores para los géneros
    genre_color_map = {
        'Drama': 'blue',
        'Comedy': 'yellow',
        'Action': 'red',
        'Adventure': 'green',
        'Horror': 'purple',
        'Romance': 'pink',
        'Sci-Fi': 'cyan',
    }

    # Asignar un color basado en el género (en caso de que un director tenga múltiples géneros, se toma el primero)
    top_directors_roi['color'] = top_directors_roi['genre'].apply(lambda x: genre_color_map.get(x.split(', ')[0], 'gray'))

    # Crear un gráfico con un mapeo de colores basado en el género
    fig_directors_roi = px.bar(
        top_directors_roi,
        x='ROI',
        y='director',
        orientation='h',
        title='Top 10 Directores por ROI Promedio',
        labels={'ROI': 'ROI Promedio', 'director': 'Director', 'color': 'Género'},
        color='genre',  # Usamos 'genre' para el color, para que aparezca en la leyenda
        color_discrete_map=genre_color_map,  # Mapear colores a géneros
    )

    # Personalizar el diseño
    fig_directors_roi.update_layout(
        xaxis_title='ROI Promedio',
        yaxis_title='',
        yaxis=dict(autorange='reversed'),  # Para que los valores más altos estén arriba
        title_x=0.5,  # Centrar el título
    )

    # Ajustar el tamaño de la figura
    fig_directors_roi.update_layout(
        width=600,  # Ancho de 600 píxeles
        height=469  # Alto de 469 píxeles
    )

    graph_html3 = fig_directors_roi.to_html()

    # Agrupar y calcular el promedio de ROI por actor
    top_actors_roi = (
        df.groupby('star')['ROI']
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    # Obtener los géneros asociados a cada actor (tomando el género de sus películas)
    top_actors_genres = df[df['star'].isin(top_actors_roi['star'])]
    top_actors_genres = top_actors_genres.groupby('star')['genre'].apply(lambda x: ', '.join(set(x))).reset_index()

    # Unir el DataFrame de actores con los géneros
    top_actors_roi = top_actors_roi.merge(top_actors_genres, on='star', how='left')

    # Crear un mapeo de colores para los géneros
    genre_color_map = {
        'Drama': 'blue',
        'Comedy': 'yellow',
        'Action': 'red',
        'Adventure': 'green',
        'Horror': 'purple',
        'Romance': 'pink',
        'Sci-Fi': 'cyan',
    }

    # Asignar un color basado en el género (en caso de que un actor tenga múltiples géneros, se toma el primero)
    top_actors_roi['color'] = top_actors_roi['genre'].apply(lambda x: genre_color_map.get(x.split(', ')[0], 'gray'))

    # Crear un gráfico con un mapeo de colores basado en el género
    fig_actors_roi = px.bar(
        top_actors_roi,
        x='ROI',
        y='star',
        orientation='h',
        title='Top 10 Actores por ROI Promedio',
        labels={'ROI': 'ROI Promedio', 'star': 'Actor/Actriz', 'color': 'Género'},
        color='genre',  # Usamos 'genre' para el color, para que aparezca en la leyenda
        color_discrete_map=genre_color_map,  # Mapear colores a géneros
    )

    # Personalizar el diseño
    fig_actors_roi.update_layout(
        xaxis_title='ROI Promedio',
        yaxis_title='',
        yaxis=dict(autorange='reversed'),  # Para que los valores más altos estén arriba
        title_x=0.5,  # Centrar el título
    )

    # Ajustar el tamaño de la figura
    fig_actors_roi.update_layout(
        width=600,  # Ancho de 600 píxeles
        height=469  # Alto de 469 píxeles
    )

    graph_html4 = fig_actors_roi.to_html()

    return templates.TemplateResponse("involucrados.html", {"request": request, "graph_html1": graph_html1, "graph_html2": graph_html2, "graph_html3": graph_html3, "graph_html4": graph_html4})

@app.get("/caracteristicas")
async def caracteristicas(request: Request):
    df = pd.read_csv("https://raw.githubusercontent.com/RodoECP/PF_Visualizacion_Datos/refs/heads/master/Peliculas.csv")
    # Agrupar clasificaciones
    df['rating'] = df['rating'].replace({
        'Unrated': 'NC-17',   # Agrupar 'Unrated' y 'X' con 'NC-17'
        'X': 'NC-17',
        'Not Rated': 'G',     # Agrupar 'Not Rated' y 'Approved' con 'G'
        'Approved': 'G',
        'TV-MA': 'R'          # Agrupar 'TV-MA' con 'R'
    })

    # Considerar película exitosa si el ROI es mayor que 2.25
    df['pelicula_exitosa'] = df['ROI'] > 2.25

    # Contar películas exitosas por tipo de clasificación
    df_grouped = df.groupby('rating').agg({'pelicula_exitosa': 'sum'}).reset_index()

    # Crear gráfico de dona
    color_map = {
        'G': 'green',
        'PG': 'blue',
        'PG-13': 'orange',
        'R': 'red',
        'NC-17': 'black'
    }

    fig = px.pie(df_grouped,
                names='rating',
                values='pelicula_exitosa',
                labels={'rating': 'Clasificación', 'pelicula_exitosa': 'Número de Películas Exitosas'},
                title='Películas Exitosas por Tipo de Clasificación',
                color='rating',  # Asignar color según la clasificación
                color_discrete_map=color_map,  # Mapear colores
                hole=0.4)  # Crear un gráfico de dona (hueco en el centro)

    # Ajustar el tamaño de la figura
    fig.update_layout(
        width=600,  # Ancho de 600 píxeles
        height=469  # Alto de 469 píxeles
    )
    graph_html1 = fig.to_html()
    # Filtrar los datos para obtener solo las películas con ROI mayor a 2.25
    data_filtered = df[df['ROI'] > 2.25]

    # Calcular el rango intercuartílico (IQR) para identificar y eliminar los valores extremos
    Q1 = data_filtered['ROI'].quantile(0.25)
    Q3 = data_filtered['ROI'].quantile(0.75)
    IQR = Q3 - Q1

    # Definir los límites superior e inferior para eliminar los valores extremos
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filtrar las películas con ROI dentro del rango no extremo
    data_filtered = data_filtered[(data_filtered['ROI'] >= lower_bound) & (data_filtered['ROI'] <= upper_bound)]

    # Verificar si hay valores nulos en las columnas 'runtime' y 'ROI'
    data_filtered = data_filtered.dropna(subset=['runtime', 'ROI'])

    # Crear la gráfica interactiva de dispersión
    fig = px.scatter(data_filtered, x='runtime', y='ROI',
                    title="Relación entre Duración y ROI en películas exitosas",
                    labels={'runtime': 'Duración (minutos)', 'ROI': 'Retorno de Inversión (ROI)'},
                    hover_data=['name', 'genre', 'rating', 'votes', 'budget', 'gross'])  # Agregar más columnas para mostrar en hover

    # Ajustar el tamaño de la figura
    fig.update_layout(
        width=600,  # Ancho de 600 píxeles
        height=469,  # Alto de 469 píxeles
    )
    graph_html2 = fig.to_html()
    return templates.TemplateResponse("caracteristicas.html", {"request": request, "graph_html1": graph_html1, "graph_html2": graph_html2})

@app.get("/tendencias")
async def tendencias(request: Request):
    return templates.TemplateResponse("tendencias.html", {"request": request})

@app.get("/problematica")
async def problematica(request: Request):

    df = pd.read_csv("https://raw.githubusercontent.com/RodoECP/PF_Visualizacion_Datos/refs/heads/master/Peliculas.csv")
    peliculas_exitosas = df[df['ROI'] > 2.25]

    # Contar el número de éxitos por año
    exitos_por_ano = peliculas_exitosas['year'].value_counts().sort_index()

    # Crear un DataFrame para usar en Plotly
    exitos_df = pd.DataFrame({
        'Año': exitos_por_ano.index,
        'Número de Éxitos': exitos_por_ano.values
    })

    # Crear el gráfico de líneas
    fig = px.line(exitos_df, x='Año', y='Número de Éxitos',
                title='Número de Éxitos por Año',
                labels={'Año': 'Año', 'Número de Éxitos': 'Número de Éxitos'})

    # Cambiar el color de la línea a rojo
    fig.update_traces(line=dict(color='red'))

    # Ajustar el tamaño de la figura
    fig.update_layout(
        width=600,  # Ancho de 600 píxeles
        height=469,  # Alto de 469 píxeles
    )

    # Convertir la figura a JSON para pasarlo al frontend
    graph_html = fig.to_html()

    # Retornar la plantilla con el gráfico
    return templates.TemplateResponse("problematica.html", {"request": request, "graph_html": graph_html})
