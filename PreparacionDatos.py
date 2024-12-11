import pandas as pd
from dateutil import parser

# Cargar el archivo CSV
df = pd.read_csv('movies.csv')

# Función para intentar convertir la fecha usando diferentes formatos
def formatear_fecha(date_str):
    try:
        # Intentar convertir con dateutil.parser que es más flexible
        return parser.parse(date_str, fuzzy=True)
    except (ValueError, TypeError):
        # Si no se puede convertir, devolver NaT (Not a Time)
        return pd.NaT

# Eliminar filas con valores nulos en cualquier columna
df = df.dropna()

# Reformatear la columna de fechas 'released'
df['released'] = df['released'].apply(formatear_fecha)

# Eliminar espacios innecesarios en las columnas de texto
for columna in df.select_dtypes(include=['object']).columns:
    df[columna] = df[columna].str.strip()  # Eliminar espacios al principio y al final

# Eliminar nuevamente filas con valores nulos en cualquier columna después de las transformaciones
df = df.dropna()

# Calcular el ROI para cada película y lo redondea a 4 decimales
df['ROI'] = ((df['gross'] - df['budget']) / df['budget']).round(4)

# Guardar el DataFrame actualizado de nuevo a un archivo CSV
df.to_csv('Peliculas.csv', index=False)
