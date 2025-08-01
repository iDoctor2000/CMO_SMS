# ----------------------------------------
# Paso 1: Instalamos dependencias necesarias
# ----------------------------------------
!pip install pandas plotly openpyxl

# ----------------------------------------
# Paso 2: Cargamos el Excel (sube el archivo)
# ----------------------------------------
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.colab import files

print("🔄 Sube tu archivo Excel con los datos de consultas...")
uploaded = files.upload()

# Tomamos el primer archivo subido
filename = list(uploaded.keys())[0]

# ----------------------------------------
# Paso 3: Procesamos los datos
# ----------------------------------------
df = pd.read_excel(filename)
df = df.dropna(how='all')  # Quitamos filas vacías
df['Mes'] = df['Mes'].astype(str).str.strip()  # Quitamos espacios

# Nos quedamos con "Primeras Realizadas" y "Sucesivas Realizadas"
df_filtrado = df[df['Mes'].isin(['Primeras Realizadas', 'Sucesivas Realizadas'])]

# Reorganizamos para tener una fila por mes
datos = df_filtrado.melt(
    id_vars=['Área ', 'Servicio', 'Mes'],
    value_vars=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto',
                'Septiembre','Octubre','Noviembre','Diciembre'],
    var_name='MesDelAño',
    value_name='Número'
)

datos['Tipo'] = datos['Mes'].apply(lambda x: 'Primeras' if 'Primeras' in x else 'Sucesivas')

# ----------------------------------------
# Paso 4: Selección del servicio
# ----------------------------------------
servicios = datos['Servicio'].dropna().unique().tolist()
print("\nServicios disponibles:")
for i, s in enumerate(servicios):
    print(f"{i+1}. {s}")

servicio_sel = input("\n✏️ Escribe el nombre exacto del servicio a visualizar: ")
datos_servicio = datos[datos['Servicio'] == servicio_sel]

# Tabla de P/S por mes
pivot = datos_servicio.pivot_table(index='MesDelAño', columns='Tipo', values='Número', aggfunc='sum')
pivot['P/S'] = pivot['Primeras'] / pivot['Sucesivas']
orden_meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
               'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
pivot = pivot.reindex(orden_meses)

# ----------------------------------------
# Paso 5: Visualizaciones
# ----------------------------------------

# Gráfico de barras
fig1 = px.bar(datos_servicio,
              x='MesDelAño', y='Número', color='Tipo',
              barmode='group', title=f'Consultas Primeras y Sucesivas en {servicio_sel}')
fig1.show()

# Índice P/S
fig2 = px.line(pivot, y='P/S', title=f'Índice P/S (Primeras/Sucesivas) en {servicio_sel}',
               labels={'value': 'Índice P/S', 'MesDelAño': 'Mes'})
fig2.update_traces(mode='lines+markers')
fig2.show()

# ----------------------------------------
# Paso 6: Diagrama de flujo tipo Sankey
# ----------------------------------------

# Simulamos un mes consolidado para el Sankey (suma total anual)
primeras = int(pivot['Primeras'].sum())
sucesivas = int(pivot['Sucesivas'].sum())

# Simulamos salidas (puedes sustituir por datos reales si los tienes)
alta = int(sucesivas * 0.5)
hospitalizacion = int(sucesivas * 0.2)
intervencion = int(sucesivas * 0.2)
inasistencia = sucesivas - (alta + hospitalizacion + intervencion)

# Nodos del Sankey
nodos = [
    "AP - INP", "AP - ITC", "Interconsulta Hospitalaria",
    servicio_sel, "Alta", "Hospitalización", "Intervención", "Inasistencia"
]

# Enlaces
source = [0, 1, 2]            # Entradas al servicio
target = [3, 3, 3]            # Todas hacia el servicio

# Añadimos salidas desde el servicio hacia finalización
source += [3, 3, 3, 3]
target += [4, 5, 6, 7]

# Valores aproximados
value = [
    int(primeras * 0.4),  # AP - INP
    int(primeras * 0.3),  # AP - ITC
    int(primeras * 0.3),  # Interconsulta hospitalaria
    alta,
    hospitalizacion,
    intervencion,
    inasistencia
]

# Crear figura Sankey
fig3 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodos
    ),
    link=dict(
        source=source,
        target=target,
        value=value
    )
)])

fig3.update_layout(title_text="🧭 Flujo de pacientes (Sankey)", font_size=12)
fig3.show()
