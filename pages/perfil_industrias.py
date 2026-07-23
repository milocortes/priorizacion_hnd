import streamlit as st
from utils import build_radar_data
import polars as pl 
import altair as alt 
import pandas as pd 
from typing import  List 
import pickle

from streamlit_echarts import st_echarts
import pyecharts.options as opts

import plotly.express as px

st.title(":material/bar_chart: Perfil de Industrias")

## Carga datos
factores = pl.read_csv("datos/factores.csv")
cdata_honduras = pl.read_csv("datos/cdata_honduras.csv")
industrias = cdata_honduras.select("clase_titulo")

# Carga jerarquía de actividades CIIU
with open("datos/nested_ciiu.pkl", "rb") as file:
    jerarquia = pickle.load(file)

with st.sidebar:
    st.header("")

    #selected_industry = st.selectbox(
    #    label="Selecciona una Industria",
    #    options= industrias,
    #    key="ex_category",
    #    bind="query-params",
    #)

    st.title("Selecciona una Clase CIIU")

    # 1. Primary Dropdown
    seccion = st.selectbox("Sección CIIU:", options=list(jerarquia.keys()))

    # 2. Dependent Dropdown (Updates dynamically based on 'category')
    division = st.selectbox("División CIIU:", options=jerarquia[seccion].keys())

    selected_industry = st.selectbox("Clase CIIU:", options=jerarquia[seccion][division])

    #st.write(f"Clase **{selected_industry}** de division **{division}**  de seccion {seccion}.")
    
def plot_radar_viablidad(
    cdata_honduras : pl.DataFrame,
    factores : pl.DataFrame, 
    factores_lista_long_name : List[str],
    #tipo_factor : str,
    industria : str):


    indicator_data, data = build_radar_data(
            cdata_honduras,
            factores, 
            selected_factores_viabilidad,
            "viabilidad", 
            selected_industry
            )

    option = {
        "title": {"text": ""},
        "legend": {
            "data": [selected_industry], 
            "bottom": "0",
            "type": "scroll",
            "data": [d["name"] for d in data],
        },
        "tooltip": {"trigger": "item"},
        "radar": {
            "indicator": indicator_data
        },
        "series": [
            {
                "name": selected_industry,
                "type": "radar",
                "data": data,
            }
        ],
    }
    st_echarts(option, height="500px")



def plot_radar_atractivo(
    cdata_honduras : pl.DataFrame,
    factores : pl.DataFrame, 
    factores_lista_long_name : List[str],
    #tipo_factor : str,
    industria : str):


    indicator_data, data = build_radar_data(
            cdata_honduras,
            factores, 
            selected_factores_atractivo,
            "atractivo", 
            selected_industry
            )

    option = {
        "title": {"text": ""},
        "legend": {
            "data": [selected_industry], 
            "bottom": "0",
            "type": "scroll",
            "data": [d["name"] for d in data],
        },
        "tooltip": {"trigger": "item"},
        "radar": {
            "indicator": indicator_data
        },
        "series": [
            {
                "name": selected_industry,
                "type": "radar",
                "data": data,
            }
        ],
    }
    st_echarts(option, height="500px", theme="streamlit")


st.markdown(f"## {selected_industry}")


with st.popover("Selecciona Criterios"):

    col1_factores, col2_factores = st.columns(2, border=True)

    with col1_factores:
        st.header("**Atractivo**")

        ### Factores Atractivo
        factores_atractivo = [
            #"Monto acumulado de inversión en capital (Mundo)", 
            "Monto acumulado de inversión en capital (LAC)", 
            #"Tasa de crecimiento de la inversión (Mundo)", 
            "Tasa de crecimiento de la inversión (LAC)", 
            #"Elasticidad Empleo/Inversión (Mundo)",
            "Elasticidad Empleo/Inversión (LAC)", 
            "Crecimiento del Producto",
            "Crecimiento de Exportaciones", 
            "Posibilidad de sustituir las importaciones estadounidenses procedentes de China", 
            "Capacidad para crear empleo"
        ]
        selected_factores_atractivo = []

        st.write("Selecciona Factores de Atractivo:")

        # Generate checkboxes dynamically
        for factor in factores_atractivo:
            # Use the item name as a unique key
            checked = st.checkbox(factor, value=True)
            if checked:
                selected_factores_atractivo.append(factor)
    with col2_factores:
        st.header("**Viabilidad**")
        ### Factores Viabilidad
        factores_viabilidad = [
            "Fortaleza en países como Honduras (RCA en el grupo de pares)", 
            "Disponibilidad de Insumos", 
            "Dependencia de una restricción o restricción potencial (Energía)", 
            "Dependencia de una restricción o restricción potencial (Electricidad)", 
            "Intensidad Institucional"
        ]
        selected_factores_viabilidad = []

        st.write("Selecciona Factores de Viabilidad:")

        # Generate checkboxes dynamically
        for factor in factores_viabilidad:
            # Use the item name as a unique key
            checked = st.checkbox(factor, value=True)
            if checked:
                selected_factores_viabilidad.append(factor)

st.markdown(f"### Viabilidad")
plot_radar_viablidad(
            cdata_honduras,
            factores, 
            selected_factores_viabilidad,
            selected_industry
            )

st.markdown(f"### Atractivo")
plot_radar_atractivo(
            cdata_honduras,
            factores, 
            selected_factores_viabilidad,
            selected_industry
            )


#st.dataframe(df)
import json
with open("datos/flare.json", "r") as f:
    data = json.loads(f.read())

for idx, _ in enumerate(data["children"]):
    data["children"][idx]["collapsed"] = idx % 2 == 0

option = {
    "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
    "series": [
        {
            "type": "tree",
            "data": [data],
            "top": "1%",
            "left": "7%",
            "bottom": "1%",
            "right": "20%",
            "symbolSize": 7,
            "label": {
                "position": "left",
                "verticalAlign": "middle",
                "align": "right",
                "fontSize": 14,
            },
            "leaves": {
                "label": {
                    "position": "right",
                    "verticalAlign": "middle",
                    "align": "left",
                }
            },
            "emphasis": {"focus": "descendant"},
            "expandAndCollapse": True,
            "animationDuration": 550,
            "animationDurationUpdate": 750,
        }
    ],
}
st_echarts(option, height="500px")


def get_demanda_mundial(producto : str) -> pl.DataFrame: 
    return pl.scan_parquet(
        "datos/demanda_global_ciiu.parquet"
    ).filter(
        Actividad=producto
    ).with_columns(
        (pl.col("Razon de Importacion")*100).round(2)
    ).rename(
        {
            "Razon de Importacion" : "Razon de Importacion [%]"
        }
    ).collect()

demanda_mundial_ciiu = get_demanda_mundial(selected_industry)

if demanda_mundial_ciiu.is_empty():

    st.write("No se encuentra Información disponible")
else: 
    fig_demanda = px.scatter_geo(
        demanda_mundial_ciiu.to_pandas(), 
        locations="country_iso3_code",       # Column containing ISO country codes
        color="Razon de Importacion [%]",                  # Column determining the color scale
        hover_name="Country",      # Column shown in bold at top of hover tooltip
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"Demanda de la Industria {selected_industry} ", 
        projection="natural earth", 
        size = "Razon de Importacion [%]"
    )

    fig_demanda.update_layout(
        geo = dict(
            #showframe=False,
            showcoastlines=True,
            showcountries=True,

        )
    )
    fig_demanda.update_layout(height=600,width=800)

    st.plotly_chart(fig_demanda, theme="streamlit", use_container_width=True)