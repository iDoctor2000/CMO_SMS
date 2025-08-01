import pandas as pd

# Ruta al archivo Excel
file_path = 'SIAE_ Consultas Externas (TODAS LAS ÁREAS Y SMS 2024).xlsx'

# Cargar el primer (y único) sheet
df = pd.read_excel(file_path)

# Elimina filas completamente vacías
df = df.dropna(how='all')

# Algunos indicadores vienen con espacios en el nombre (p.ej. "Primeras Realizadas ")
df['Mes'] = df['Mes'].str.strip()

# Filtrar solo las filas de interés: Primeras y Sucesivas
df_filtrado = df[df['Mes'].isin(['Primeras Realizadas', 'Sucesivas Realizadas'])]

# Convertimos las columnas de meses en una sola columna
datos = df_filtrado.melt(
    id_vars=['Área ', 'Servicio', 'Mes'],
    value_vars=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
    var_name='MesDelAño',
    value_name='Número'
)

# Creamos una columna para distinguir Primeras y Sucesivas
datos['Tipo'] = datos['Mes'].apply(lambda x: 'Primeras' if 'Primeras' in x else 'Sucesivas')
import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos (o permitir al usuario subir su propio Excel)
@st.cache_data
def cargar_datos(path):
    df = pd.read_excel(path).dropna(how='all')
    df['Mes'] = df['Mes'].str.strip()
    df_filtrado = df[df['Mes'].isin(['Primeras Realizadas', 'Sucesivas Realizadas'])]
    datos = df_filtrado.melt(
        id_vars=['Área ', 'Servicio', 'Mes'],
        value_vars=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
        var_name='MesDelAño',
        value_name='Número'
    )
    datos['Tipo'] = datos['Mes'].apply(lambda x: 'Primeras' if 'Primeras' in x else 'Sucesivas')
    return datos

st.title("Dashboard de Consultas Externas")

# Widget para subir archivo
archivo = st.file_uploader("Sube el archivo Excel de consultas", type=["xlsx"])
if archivo:
    datos = cargar_datos(archivo)
else:
    st.stop()

# Selector de servicio
servicios = datos['Servicio'].dropna().unique()
servicio_sel = st.selectbox("Selecciona un servicio", sorted(servicios))

# Filtrar datos por servicio
datos_servicio = datos[datos['Servicio'] == servicio_sel]

# Calcular P/S por mes
datos_pivot = datos_servicio.pivot_table(index='MesDelAño', columns='Tipo', values='Número', aggfunc='sum')
datos_pivot['P/S'] = datos_pivot['Primeras'] / datos_pivot['Sucesivas']

# Selector de meses (multi-selección)
meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
meses_sel = st.multiselect("Selecciona meses", meses, default=meses)

# Gráfico de barras de primeras y sucesivas
fig = px.bar(datos_servicio[datos_servicio['MesDelAño'].isin(meses_sel)],
             x='MesDelAño', y='Número', color='Tipo',
             barmode='group',
             labels={'Número': 'Nº de consultas', 'MesDelAño': 'Mes'})

fig.update_layout(title=f"Consultas Primeras y Sucesivas en {servicio_sel}")

st.plotly_chart(fig, use_container_width=True)

# Mostrar ratio P/S
st.subheader("Índice Primeras/Sucesivas")
st.line_chart(datos_pivot['P/S'][datos_pivot.index.isin(meses_sel)])
st.caption("Un índice P/S bajo (<1) puede indicar muchas primeras sin continuidad. Muy alto (>3-4) puede sugerir seguimiento excesivo. Un rango 1,5–2,5 suele considerarse razonable según la especialidad.")
import io
from reportlab.pdfgen import canvas

# Crear un buffer y un PDF sencillo con el gráfico
pdf_buffer = io.BytesIO()
c = canvas.Canvas(pdf_buffer)
c.drawString(100, 750, f"Dashboard de {servicio_sel}")
# aquí se podrían insertar imágenes de los gráficos guardadas como PNG
c.save()
# Botón de descarga
st.download_button("Descargar resumen en PDF", data=pdf_buffer.getvalue(), file_name="resumen.pdf", mime="application/pdf")
