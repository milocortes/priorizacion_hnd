import streamlit as st
from utils import build_radar_data
import polars as pl 
import altair as alt 
import pandas as pd 
from typing import  List 
import pickle

from streamlit_echarts import st_echarts
import pyecharts.options as opts
from streamlit_echarts import st_echarts, JsCode
import plotly.express as px

st.title(":material/bar_chart: Perfil de Industrias")

## Carga datos
factores = pl.read_csv("datos/factores.csv")
cdata_honduras = pl.read_csv("datos/cdata_honduras.csv")
industrias = cdata_honduras.select("clase_titulo")

### Cargamos datos
cdata_hnd = pl.read_csv("datos/cdata_honduras.csv")

# Cargamos recodificación
recod = pd.read_csv("datos/recodificacion_hnd_usa.csv")

## Diccionario CIIU 4 a nombres
mapp_ciiu = pl.from_pandas(recod.query("clasificador=='ciiu_rev_4'")[["codigo", "nombre_actividad"]])

### Resultados finales Intensivo
resultados_finales_intensivo = pd.read_excel("datos/seleccion_final_complexity.xlsx", sheet_name="intensivo")

### Resultados finales Extensivo
resultados_finales_extensivo = pd.read_excel("datos/seleccion_final_complexity.xlsx", sheet_name="extensivo")

### Industrias Seleccionadas
industrias_seleccionadas = pd.concat(
    [
    resultados_finales_intensivo[["ciiu4_cod"]],
    resultados_finales_extensivo[["ciiu4_cod"]]
    ], ignore_index=True
)

industrias_seleccionadas_nombres = pd.concat(
    [
    resultados_finales_intensivo[["ciiu4_Actividad"]],
    resultados_finales_extensivo[["ciiu4_Actividad"]]
    ], ignore_index=True
)

industrias_seleccionadas_lista = industrias_seleccionadas_nombres["ciiu4_Actividad"].to_list()

def color_industria(industria, lista_industrias): 
    if industria in lista_industrias: 
        return "#f58518"
    else:
        return "#4c78a8"
        
cdata_hnd = cdata_hnd.with_columns(
    pl.when(
        pl.col("ACTIVITY").is_in(industrias_seleccionadas["ciiu4_cod"])
    ).then(
        pl.lit("Sí")
    ).otherwise(
        pl.lit("No")
    ).alias("Industria Seleccionada")
)

cdata_hnd = cdata_hnd.filter(
    (pl.col("REF_AREA")=="HND") & 
    (pl.col("rca")>0)

).join(
    mapp_ciiu,
    left_on="ACTIVITY", 
    right_on="codigo"
)



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
    st_echarts(option, height="600px")



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
    st_echarts(option, height="600px", theme="streamlit")

st.markdown(f"## {selected_industry}")

st.markdown(f"### Overview")

pci_promedio = cdata_hnd["pci"].mean()
distancia_promedio = cdata_hnd["distance"].mean()

perfil_industria = {i:j[0] for i,j in cdata_hnd.filter(clase_titulo=selected_industry).to_dict(as_series=False).items()}


def build_perfil_texto(perfil : dict) -> str:
    mcp = perfil["mcp"]
    distancia = perfil["distance"]
    pci = perfil["pci"]
    industria = perfil["clase_titulo"]

    distancia_desc = "**con Distancia por debajo de la distancia media**" if distancia < distancia_promedio else  "**con distancia por encima de la Distancia media**"
    pci_desc = "**con Complejidad por debajo de la distancia media**" if pci < pci_promedio else  "**con distancia por encima de la Complejidad media**"

    ventaja = "**No tiene**" if mcp == 0 else  "**Tiene**"

    ventaja_bool = "**No hay**" if mcp == 0 else  "**Hay**"
    
    overview = f"""
    **{industria}** es una industria {distancia_desc} y {pci_desc} en Honduras. Los datos internacionales de Empleo muestran que Honduras {ventaja} Ventaja Comparativa Revelada en esta industria, lo que significa que {ventaja_bool} entidades económicas intensamente involucradas en este producto en Honduras en comparación con el resto del mundo.
    """

    return overview

st.markdown(build_perfil_texto(perfil_industria))


principal_plot = alt.Chart(
    cdata_hnd
        ).mark_circle(
            opacity=0.99,
            stroke='black',
            strokeWidth=1.2,
            strokeOpacity=0.9, 
            size=180,     
        ).encode(
    x=alt.X('distance').scale(zero=False).title("Distancia"),
    y=alt.Y('pci').title("PCI"),#.scale(type ="log"),
    #shape = alt.Shape("mcp:N").title("M"),
    size = alt.Size("OBS_VALUE").title("Empleo").scale(type ="log"),
    #color = alt.Color("rca").scale(type ="log", scheme='redblue', domainMid=1.0).title("RCA"),
    color = alt.Color("rca").title("RCA").scale(type ="log", scheme='redblue', domainMid=1.0),
    #size = alt.Size("rca").scale(type ="log").title("RCA"),
    tooltip=[
        
            alt.Tooltip('clase_titulo', title='Actividad'), 
            alt.Tooltip('rca', title='RCA')
    ] 
)

industria_plot = alt.Chart(
    cdata_hnd.filter(clase_titulo=selected_industry)
        ).mark_circle(
            opacity=0.99,
            stroke='black',
            strokeWidth=3.2,
            strokeOpacity=0.9, 
            size=700,     
        ).encode(
    x=alt.X('distance').scale(zero=False).title("Distancia"),
    y=alt.Y('pci').title("PCI"),
    color=alt.value(color_industria(selected_industry, industrias_seleccionadas_lista)),
    tooltip=[
        
            alt.Tooltip('clase_titulo', title='Actividad'), 
            alt.Tooltip('rca', title='RCA')
    ] 
)

# Create a horizontal line at y = -1.14
rule_pci = alt.Chart(pd.DataFrame({'y': [cdata_hnd["pci"].mean()]})).mark_rule(color='gray', strokeWidth=3, strokeDash=[4,4]).encode(y='y:Q')

rule_distancia = alt.Chart(pd.DataFrame({'x': [cdata_hnd["distance"].mean()]})).mark_rule(color='gray', strokeWidth=3, strokeDash=[4,4]).encode(x='x:Q')

pci_distancia = (principal_plot + industria_plot + rule_pci + rule_distancia).properties(
    title=alt.TitleParams(
        "Diagrama Distancia-PCI",
        subtitle="Honduras. Datos de Empleo de OECD SBS 2019",
        subtitleColor="gray"
    )
).configure_legend(
    strokeColor='gray',
    fillColor='white',
    padding=10,
    cornerRadius=10,
    orient='top-left', 
    titleFontSize=18,
    labelFontSize=16,
)

st.altair_chart(pci_distancia, theme=None, use_container_width=True)


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
            #"Dependencia de una restricción o restricción potencial (Energía)", 
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

st.markdown(f"### Factores de Viabilidad")

col2_factores_viabilidad, col1_factores_viabilidad = st.columns(2, border=True)

with col1_factores_viabilidad:

    plot_radar_viablidad(
                cdata_honduras,
                factores, 
                selected_factores_viabilidad,
                selected_industry
    )

with col2_factores_viabilidad:
    st.markdown(
    """
    - **Fortaleza en países como Honduras (RCA en el grupo de pares)**
        - Promedio de las Ventajas Comparativas Reveladas de la Industria en los Países Pares (Ecuador y El Salvador).

    - **Disponibilidad de Insumos.**
        - Razón de productos disponibles o presentes por industria.
        >Fuente : Liao et al (2020) y AIPNET
    """
    )

    with st.popover("Más información"):

        st.markdown(
            """
            - **Disponibilidad de Insumos.**
                - Para la construcción de este indicador, se usó la metodología de Liao et al (2020) quienes descomponen la industria CIIU por los productos que la intengra, ponderado por el peso relativo de cada producto en la industria. Además, usamos los datos de [AI-generated Production Network - AIPNET](https://aipnet.io/) para identificar la cadena de producción de los productos.
                - Para cada producto, calculamos la razón de productos disponibles en el país al contabilizar la cantidad de productos en el país que tienen RCA mayor o igual a 1 con respecto al total de productos que se necesita para la producción. 
                - Con esta razón de productos disponibles **por producto**, usamos los ponderadores de Liao et al (2020) para calcular la razón de disponibilidad **por industria** al multiplicar y sumar la razón de productos disponibles por producto y los ponderadores del peso relativo del producto en la industria.
            """
        )
    st.markdown(
    """
    - **Dependencia de una restricción o restricción potencial (Energía)**
        - El indicador es la razón entre el valor de las compras de productos de energía y el valor total de las compras en bienes y servicios de la industria.
            >Fuente : OECD Structural Business Statistics
    - **Dependencia de una restricción o restricción potencial (Electricidad)**
        - El indicador es la razón entre el Gasto por consumo de energía eléctrica y los Gastos Totales por consumo de bienes y servicios de la industria.
            >Fuente : Censos Económicos 2023, INEGI.
    - **Intensidad Institucional**
        - La intensidad institucional es la proporción de insumos intermedios que no pueden adquirirse en mercados organizados y que no tienen un precio de referencia..
        >Fuente : Levchenko, A. A. (2013). International trade and institutional change. The Journal of Law, Economics, & Organization, 29(5), 1145-1181..
    """
    )
st.markdown(f"### Factores de Atractivo")

col2_factores_atractivo, col1_factores_atractivo = st.columns(2, border=True)

with col1_factores_atractivo:

    plot_radar_atractivo(
                cdata_honduras,
                factores, 
                selected_factores_viabilidad,
                selected_industry
                )
with col2_factores_atractivo:
    st.markdown(
    """
    - **Monto acumulado de inversión en capital (LAC)** 
        - Monto acumulado de inversión en capital y creacion de empleo entre 2019 y 2024 en América Latina.
        >Fuente : FDI Markets
    - **Tasa de crecimiento de la inversión (LAC)**
        - Tasa de crecimiento compuesta de la inversión entre 2019 y 2024 en América Latina.
        >Fuente : FDI Markets
    - **Elasticidad Empleo/Inversión (LAC)**
        - Elasticidad de crecimiento del empleo al crecimiento de la inversión entre 2019 y 2024 en América Latina.
        >Fuente : FDI Markets
    - **Crecimiento del Producto**
        - Crecimiento de la Producción de las industrias en el mundo. 
        >Fuente : OECD Structural Business Statistics
    - **Crecimiento de Exportaciones** 
    """
    )

    with st.popover("Más información"):

        st.markdown(
            """
            - **Crecimiento del Producto**
                - Crecimiento de la Producción de las industrias en el mundo. 
                >Fuente : OECD Structural Business Statistics
            """
        )

    st.markdown(
        """
    - **Posibilidad de sustituir las importaciones estadounidenses procedentes de China**
        """
    )
    with st.popover("Más información"):

        st.markdown(
            """
            - **Posibilidad de sustituir las importaciones estadounidenses procedentes de China**
                - Se estima la posibilidad de sustituir importaciones de China en USA al calcular la razón promedio ponderada de la industria CIIU a ser importada por USA desde China. Usando la metodología de Liao et al (2020) se calcula la razón de importación por producto proveniente de China con respecto al total de importación para USA. Con el peso relativo de cada producto en la industria se calcula la razón promedio poderada de la industria.
                >Fuente : Atlas de Complejidad 
            """
        )

    st.markdown(
        """
        - **Capacidad para crear empleo**
        """
    )
    with st.popover("Más información"):

        st.markdown(
            """
            - **Capacidad para crear empleo**
                - Elasticidad de crecimiento del empleo al crecimiento del producto de la industria. Este indicador mide cómo responde el empleo a los cambios en el producto de la industria. Indica cuánto crece el empleo de la industria por cada 1 % de aumento en el producto.
                >Fuente : OECD Structural Business Statistics
            """
        )
#st.dataframe(df)
st.write("## Disponibilidad de Insumos")

### Cargamos arbol de insumos
with open('datos/ciiu_arbol_insumos.pkl', 'rb') as file:
    arbol_insumos = pickle.load(file)

arbol_insumos_completo = pl.read_parquet("datos/arbol_insumos_completo.parquet")
map_ciiu_to_ciiu_code = {i:j for i,j in arbol_insumos_completo.select("Actividad", "CIIU").to_pandas().to_records(index = False)}

def test_boleano(valor):
    if valor==1:
        return "Sí"
    else:
        return "No"

def build_tree(arbol) : 
    return [
        {"name" : hs , 
         "itemStyle": { "color": "red" if  hs_down[0]["Disponibilidad Producto (HS12)"] >= 50.0 else "gray"}, 
         "value" : hs_down[0]["Disponibilidad Producto (HS12)"],
         "categoria" : "producto",
         "collapsed" : True,
         "children" : [
             { 
                 "name" : v["Producto Downstream (H12)"], 
                 "exporta" : test_boleano(v["Se Exporta"]),
                 "importa" : test_boleano(v["Se Importa"]), 
                 "disponible" : test_boleano(v["Disponible"]), 
                 "itemStyle": { "color": "orange" if  v["Se Exporta"] == 1 else  "blue" if v["Se Importa"] == 1 else "gray"}, 
                 "categoria" : "insumo",
             }
             for v in hs_down
         ]
        } for hs,hs_down in arbol.items() ]


if selected_industry in map_ciiu_to_ciiu_code:
    indutria_diponibilidad_insumos = {
        "name" : "Industria", 
        "categoria" : "raiz",
        "children" : build_tree(
            arbol_insumos[map_ciiu_to_ciiu_code[selected_industry]]
        )
        }

    option_arbol = {
        "tooltip": {
            "trigger": "item", 
            "triggerOn": "mousemove", 
                "formatter": JsCode(
                    """
                function (params) {
                    if (params.data.categoria == "raiz") {
                        return '<b>' + params.name ;
                    } else if (params.data.categoria == "producto"){
                        return '<b>' + params.name + '</b><br/> Disponibilidad del Producto (HS12) : ' + params.value  + '%';
                    } else if (params.data.categoria == "insumo"){
                        return '<b>' + params.name + '</b><br/> Se Exporta : ' + params.data.exporta  + '</b><br/> Se Importa : '  + params.data.importa+ '</b><br/> Disponible : '  + params.data.disponible;
                    }
                }
                    """
                ),
        },
        "series": [
            {
                "type": "tree",
                "data": [indutria_diponibilidad_insumos],
                "top": "1%",
                "left": "7%",
                "bottom": "1%",
                "right": "20%",
                "symbolSize": 10,
                "label": {
                    "position": "left",
                    "verticalAlign": "middle",
                    "align": "right",
                    "fontSize": 16,
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

    st.write(
        f"""
        La raiz del árbol corresponde a la industria **{selected_industry}**. El primer nivel del árbol son los productos que componen a la industria.
        Los nodos en este nivel son rojos si tienen una razón de disponibilidad arriba del 50%. El segundo nivel del árbol es la cadena de producción del producto. Los nodos color naranja indican que el insumo está disponible porque se exporta con ventaja comparativa, mientras que los nodos color azul indican que el insumo está diponible porque se importa con intensidad (El insumo representa el 20% de las importaciones totales con las que se produce el producto).
        """
    )
    st_echarts(option_arbol, height="500px")

    st.dataframe(
        arbol_insumos_completo.filter(Actividad=selected_industry),
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("No se encuentra Información disponible", icon="⚠️")

st.write("## Demanda Mundial")

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
    st.info("No se encuentra Información disponible", icon="⚠️")
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


    # Pass configuration into st.dataframe
    demanda_mundial_ciiu = demanda_mundial_ciiu.with_columns(
        pl.col("Valor de Importacion")/1_000_00
    )

    st.dataframe(
        demanda_mundial_ciiu.select(
            "Country", "Valor de Importacion", "Razon de Importacion [%]"
        ).sort("Valor de Importacion", descending = True),
        column_config={
            "Country": st.column_config.TextColumn(
                "Country", 
                max_chars=20
            ),
            "Valor de Importacion": st.column_config.NumberColumn(
                "Valor de Importacion [Millones US]", 
                format="%.2f"
            ),
            "Razon de Importacion [%]": st.column_config.TextColumn(
                "Razon de Importacion [%]", 
                #display_text="Click here to Buy"
                max_chars=20
            ), 
        },
        hide_index=True,
        use_container_width=True
    )