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

@app.get("/problematica")
async def genero_analysis(request: Request):
    return templates.TemplateResponse("problematica.html", {"request": request})

@app.get("/genero")
async def genero_analysis(request: Request):
    return templates.TemplateResponse("genero.html", {"request": request})

@app.get("/involucrados")
async def involved_analysis(request: Request):
    return templates.TemplateResponse("involucrados.html", {"request": request})

@app.get("/caracteristicas")
async def characteristics_analysis(request: Request):
    return templates.TemplateResponse("caracteristicas.html", {"request": request})

@app.get("/tendencias")
async def trends_analysis(request: Request):
    return templates.TemplateResponse("tendencias.html", {"request": request})

@app.get("/conclusion")
async def conclusion(request: Request):
    return templates.TemplateResponse("conclusion.html", {"request": request})



@app.get("/grafica3", response_class=HTMLResponse)
async def grafica3(request: Request):
    # Leer datos desde GitHub
    url = "https://raw.githubusercontent.com/DanteRobert1/Optativa_Liz_Uaa/main/vgsales.csv"
    df = pd.read_csv(url)

    # Crear columna de ventas regionales
    df['Regional_Sales'] = df['NA_Sales'] + df['EU_Sales'] + df['JP_Sales']

    # Crear gráfica
    fig = px.scatter(
        df,
        x='Regional_Sales',
        y='Global_Sales',
        color='Genre',
        size='Regional_Sales',
        hover_name='Name',
        title='Dispersión de Ventas por Regiones Combinadas'
    )

    # Convertir gráfica a HTML
    graph_html = fig.to_html(full_html=False)

    # Renderizar template
    return templates.TemplateResponse("grafica3.html", {"request": request, "graph_html": graph_html})
