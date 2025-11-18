
# Dashboard de sucursales – Cartera e ICV (prototipo  de Dimex)

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from PIL import Image

# Configuración básica del dashboard que estoy haciendo
st.set_page_config(
    page_title="Dashboard de sucursales – Cartera e ICV",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta de colores de DIMEX
PALETA_DIMEX = [
    "#5DF200",  # Verde para casí todo esta va ser el principal 
    "#3ABD00",  # otro verde mas fuertecito 
    "#B6FF66",  # Verde lima claro tambien 
    "#66FF77",  # aqui le voy a poner un verde menta que vaya con la paleta de colores
    "#002040",  # Azul corporativo
]

COLOR_PRIMARIO = "#5DF200"
COLOR_SECUNDARIO = "#3ABD00"
COLOR_FONDO = "#F6FFF0"
COLOR_TEXTO = "#002040"


st.markdown(
    f"""
    <style>
    body {{
        background-color: {COLOR_FONDO};
        color: {COLOR_TEXTO};
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* Títulos */
    h1, h2, h3, h4, h5 {{
        color: {COLOR_SECUNDARIO} !important;
        font-weight: 700 !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: #E5FFCC !important;
        color: {COLOR_TEXTO} !important;
    }}

    /* Botones */
    div.stButton > button {{
        background-color: {COLOR_PRIMARIO} !important;
        color: {COLOR_TEXTO} !important;
        border-radius: 6px !important;
        padding: 0.4rem 0.8rem !important;
        border: none !important;
        font-weight: 600 !important;
    }}
    div.stButton > button:hover {{
        background-color: {COLOR_SECUNDARIO} !important;
        color: white !important;
        transform: scale(1.03);
    }}

    /* Métricas */
    [data-testid="stMetric"] {{
        background-color: white !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }}
    [data-testid="stMetricValue"] {{
        color: {COLOR_PRIMARIO} !important;
        font-weight: 700 !important;
    }}

    /* Contenedores generales */
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }}

    /* Tablas */
    .stDataFrame {{
        background-color: #F0FFE6 !important;
        border-radius: 12px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)



def encontrar_columna(df: pd.DataFrame, posibles_nombres):
    """
    Devuelve el nombre real de la primera columna que exista en el DataFrame
    de entre una lista de posibles nombres. Si no encuentra ninguna, devuelve None.
    """
    for nombre in posibles_nombres:
        if nombre in df.columns:
            return nombre
    return None


@st.cache_data(show_spinner="Cargando datos de Excel...")
def cargar_datos(ruta: str | Path, hoja: str) -> pd.DataFrame:
    df = pd.read_excel(ruta, sheet_name=hoja)
    return df

# aqui cargué los datos más en la parte de la base de datos en excel

RUTA_EXCEL = Path("250811_master_reto_sucursales1.xlsx")
HOJA = "Indicadores Comercial Clase (2)"

if not RUTA_EXCEL.exists():
    st.error(
        f"No se encontró el archivo {RUTA_EXCEL.name}. "
        f"Colócalo en la misma carpeta que este script."
    )
    st.stop()

try:
    df_raw = cargar_datos(RUTA_EXCEL, HOJA)
except Exception as e:
    st.error("Error al leer el archivo. Revisa nombre de hoja y contenido.")
    st.error(f"Detalle técnico: {e}")
    st.stop()

df = df_raw.copy()

# Aqui facilite el encontrar las columnas, que fuera más fácil para mi encontrar todo. 
col_region = encontrar_columna(df, ["Región", "Region", "REGION"])
col_vendedor = encontrar_columna(df, ["Vendedor", "VENDEDOR"])
col_cartera = encontrar_columna(
    df,
    [
        "Capital liquidado Actual",
        "Capital Liquidado Actual",
        "Cartera total",
        "Saldo actual",
        "Capital Liquidado T-00",
    ],
)
col_icv = encontrar_columna(df, ["ICV", "Índice de Cartera Vencida", "Indice de Cartera Vencida"])
col_krd = encontrar_columna(df, ["KRD", "KRD total"])


cols_fpd = [c for c in df.columns if "FPD" in str(c).upper()]

# logo y título

col_logo, col_title, col_empty = st.columns([1, 4, 1])

with col_logo:
    logo_path = Path("dimex_logo.png")
    if logo_path.exists():
        logo = Image.open(logo_path)
        st.image(logo, use_column_width=True)
    else:
        st.write("Logo Dimex")

with col_title:
    st.markdown(
        """
        <h1 style='margin-bottom: 0.1rem;'>Dashboard de sucursales – Cartera e ICV</h1>
        <p style='color:#555; font-size:0.95rem; margin-top:0.1rem;'>
        Prototipo para monitorear cartera, indicadores y desempeño comercial.
        </p>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

#filtros que usare 
st.sidebar.header("Filtros")

if col_region:
    regiones = sorted(df[col_region].dropna().unique().tolist())
    filtro_regiones = st.sidebar.multiselect(
        "Región", opciones := regiones, default=regiones
    )
else:
    filtro_regiones = None

if col_vendedor:
    vendedores = sorted(df[col_vendedor].dropna().unique().tolist())
    filtro_vendedores = st.sidebar.multiselect(
        "Vendedor", vendedores, default=vendedores
    )
else:
    filtro_vendedores = None

st.sidebar.markdown("---")
st.sidebar.write("Archivo de trabajo:")
st.sidebar.code(f"{RUTA_EXCEL.name} / hoja '{HOJA}'")

#Filtros
df_filtrado = df.copy()

if col_region and filtro_regiones:
    df_filtrado = df_filtrado[df_filtrado[col_region].isin(filtro_regiones)]

if col_vendedor and filtro_vendedores:
    df_filtrado = df_filtrado[df_filtrado[col_vendedor].isin(filtro_vendedores)]
#Metricas como el resumen ejecutivo , las sucursales activas, etc, etc. 
st.subheader("Resumen ejecutivo")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    n_sucursales = df_filtrado[col_region].nunique() if col_region else len(df_filtrado)
    st.metric("Sucursales activas", n_sucursales)

with col_m2:
    if col_cartera:
        total_cartera = df_filtrado[col_cartera].sum()
        st.metric("Cartera total filtrada", f"${total_cartera:,.0f}")
    else:
        st.metric("Cartera total filtrada", "Columna no encontrada")

with col_m3:
    if col_icv:
        icv_prom = df_filtrado[col_icv].mean()
        st.metric("ICV promedio", f"{icv_prom:,.2%}")
    else:
        st.metric("ICV promedio", "Columna no encontrada")

with col_m4:
    if col_krd:
        krd_total = df_filtrado[col_krd].sum()
        st.metric("KRD total", f"${krd_total:,.0f}")
    else:
        st.metric("KRD total", "Columna no encontrada")

st.markdown("")

#Tablas completas
tab_resumen, tab_region, tab_icv, tab_detalle = st.tabs(
    ["Visión general", "Análisis por región", "ICV y FPD", "Detalle de sucursales"]
)

#Tabla 1
with tab_resumen:
    st.markdown("### Distribución general de cartera y ventas")

    col_g1, col_g2 = st.columns(2)

    # Gráfica 1: Cartera por región
    with col_g1:
        if col_region and col_cartera:
            df_region = (
                df_filtrado.groupby(col_region, as_index=False)[col_cartera].sum()
            )
            fig_region = px.bar(
                df_region,
                x=col_region,
                y=col_cartera,
                title="Cartera por región",
                color=col_region,
                color_discrete_sequence=PALETA_DIMEX,
            )
            fig_region.update_layout(
                xaxis_title="Región",
                yaxis_title="Cartera total",
                showlegend=False,
                margin=dict(l=10, r=10, t=60, b=40),
            )
            st.plotly_chart(fig_region, use_container_width=True)
        else:
            st.info("No se encontraron columnas para Región y/o Cartera.")

    # Gráfica 2: Cartera por vendedor
    with col_g2:
        if col_vendedor and col_cartera:
            df_vend = (
                df_filtrado.groupby(col_vendedor, as_index=False)[col_cartera].sum()
            )
            df_vend = df_vend.sort_values(col_cartera, ascending=False).head(20)
            fig_vend = px.bar(
                df_vend,
                x=col_vendedor,
                y=col_cartera,
                title="Top vendedores por cartera",
                color=col_vendedor,
                color_discrete_sequence=PALETA_DIMEX,
            )
            fig_vend.update_layout(
                xaxis_title="Vendedor",
                yaxis_title="Cartera total",
                showlegend=False,
                margin=dict(l=10, r=10, t=60, b=40),
            )
            fig_vend.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_vend, use_container_width=True)
        else:
            st.info("No se encontraron columnas para Vendedor y/o Cartera.")

#Tabla 2
with tab_region:
    st.markdown("### Comparativo de indicadores por región")

    if col_region:
        # Tabla agregada por región
        cols_agregables = []
        for c in [col_cartera, col_icv, col_krd]:
            if c:
                cols_agregables.append(c)

        if cols_agregables:
            df_reg_agg = df_filtrado.groupby(col_region, as_index=False)[
                cols_agregables
            ].agg("mean")
            if col_cartera in df_reg_agg.columns:
                df_reg_agg[col_cartera] = df_filtrado.groupby(col_region)[
                    col_cartera
                ].sum().values
            st.dataframe(df_reg_agg, use_container_width=True, height=350)
        else:
            st.info("No se encontraron columnas numéricas clave para agrupar por región.")

        st.markdown("")

        col_r1, col_r2 = st.columns(2)

        with col_r1:
            if col_cartera:
                df_region_c = (
                    df_filtrado.groupby(col_region, as_index=False)[col_cartera].sum()
                )
                fig_reg_c = px.pie(
                    df_region_c,
                    names=col_region,
                    values=col_cartera,
                    title="Participación de cartera por región",
                    color=col_region,
                    color_discrete_sequence=PALETA_DIMEX,
                )
                fig_reg_c.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_reg_c, use_container_width=True)
            else:
                st.info("No se encontró la columna de cartera para el gráfico por región.")

        with col_r2:
            if col_icv:
                df_region_icv = (
                    df_filtrado.groupby(col_region, as_index=False)[col_icv].mean()
                )
                fig_icv_reg = px.bar(
                    df_region_icv,
                    x=col_region,
                    y=col_icv,
                    title="ICV promedio por región",
                    color=col_region,
                    color_discrete_sequence=PALETA_DIMEX,
                )
                fig_icv_reg.update_layout(
                    xaxis_title="Región",
                    yaxis_title="ICV promedio",
                    showlegend=False,
                )
                fig_icv_reg.update_yaxes(tickformat=".1%")
                st.plotly_chart(fig_icv_reg, use_container_width=True)
            else:
                st.info("No se encontró una columna de ICV para el gráfico por región.")
    else:
        st.info("No se encontró la columna de Región en el archivo.")

#Tabla 3
with tab_icv:
    st.markdown("### Indicadores de riesgo: ICV y FPD")

    col_i1, col_i2 = st.columns(2)

    with col_i1:
        if col_icv and col_cartera:
            fig_scatter_icv = px.scatter(
                df_filtrado,
                x=col_cartera,
                y=col_icv,
                color=col_region if col_region else None,
                color_discrete_sequence=PALETA_DIMEX,
                title="Relación entre cartera e ICV",
            )
            fig_scatter_icv.update_layout(
                xaxis_title="Cartera",
                yaxis_title="ICV",
            )
            fig_scatter_icv.update_yaxes(tickformat=".1%")
            st.plotly_chart(fig_scatter_icv, use_container_width=True)
        else:
            st.info("Se requieren columnas de cartera e ICV para este gráfico.")

    with col_i2:
        if cols_fpd:
            fpd_cols_sorted = sorted(cols_fpd)
            df_fpd = df_filtrado[fpd_cols_sorted].mean().reset_index()
            df_fpd.columns = ["Indicador", "Valor"]
            fig_fpd = px.bar(
                df_fpd,
                x="Indicador",
                y="Valor",
                title="Comparativo de indicadores FPD",
                color="Indicador",
                color_discrete_sequence=PALETA_DIMEX,
            )
            fig_fpd.update_layout(
                xaxis_title="Indicador",
                yaxis_title="Valor promedio",
                showlegend=False,
            )
            st.plotly_chart(fig_fpd, use_container_width=True)
        else:
            st.info("No se encontraron columnas que contengan 'FPD' en el archivo.")

#Tabla 4
with tab_detalle:
    st.markdown("### Detalle de sucursales (vista tabular)")

    st.write(
        "La tabla respeta los filtros actuales de región y vendedor. "
        "Puedes usar el buscador y los scrolls para explorar la información."
    )

    st.dataframe(df_filtrado, use_container_width=True, height=500)

    st.markdown("")
    st.caption(
        "Prototipo diseñado como apoyo para la visualización de cartera e indicadores comerciales de Dimex."
    )
