import inspect
import textwrap
import polars as pl
import streamlit as st
import altair as alt 
import pandas as pd 

st.title(":material/bar_chart: Especialización de Industrias")

### Cargamos datos
cdata_hnd = pl.read_csv("datos/cdata.csv")

# Cargamos recodificación
recod = pd.read_csv("datos/recodificacion_hnd_usa.csv")

## Diccionario CIIU 4 a nombres
mapp_ciiu = pl.from_pandas(recod.query("clasificador=='ciiu_rev_4'")[["codigo", "nombre_actividad"]])

### Cargamos selección de industrias de Pedro
ciiu_pedro_2 = pl.from_pandas(
    pd.read_csv("datos/seleccion_pedro.csv").query("incluye==1")
)

def plot_industrias(criterio):

    if criterio == "Todas las Industrias": 
        plot_industrias = alt.Chart(cdata_hnd.filter(
            (pl.col("REF_AREA")=="HND") & 
            (pl.col("rca")>0)

        ).join(
            mapp_ciiu,
            left_on="ACTIVITY", 
            right_on="codigo"
        )
                ).mark_circle(
                    opacity=0.99,
                    stroke='black',
                    strokeWidth=1.2,
                    strokeOpacity=0.9, 
                    size=180,     
                ).encode(
            x=alt.X('distance').scale(zero=False).title("Distancia"),
            y=alt.Y('pci').title("PCI"),#.scale(type ="log"),
            shape = alt.Shape("mcp:N").title("M"),
            color = alt.Color("rca").scale(type ="log", scheme='redblue', domainMid=1.0).title("RCA"),
            size = alt.Size("rca").scale(type ="log"),
            tooltip=[
                
                    alt.Tooltip('nombre_actividad', title='Actividad'), 
                    alt.Tooltip('rca', title='RCA')
            ] 
        ).properties(
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
        st.altair_chart(plot_industrias, theme=None, use_container_width=True)
    elif criterio == "Margen Intensivo":
        cdata_intensivo = cdata_hnd.filter(
            (pl.col("REF_AREA")=="HND") & 
            (pl.col("rca")>0) & 
            (pl.col("mcp")==1)
        )

        plot_intensivo = alt.Chart(
            cdata_intensivo.join(
            mapp_ciiu,
            left_on="ACTIVITY", 
            right_on="codigo"
        ).join(
            ciiu_pedro_2.select("clase_codigo", "clase_titulo", "seccion_codigo", "seccion_titulo", "division_titulo"),
            left_on= "ACTIVITY", 
            right_on = "clase_codigo"
        )
        ).mark_circle(
                    opacity=0.99,
                    stroke='black',
                    strokeWidth=1.2,
                    strokeOpacity=0.9, 
                    size=180,     
                ).encode(
            x=alt.X('distance').scale(zero=False).title("Distancia"),
            y=alt.Y('pci').title("PCI"),#.scale(type ="log"),
            color = alt.Color("seccion_titulo").title("Sección"),
            size = alt.Size("OBS_VALUE").scale(type ="log").title("Empleo"),
            tooltip=[
                
                    alt.Tooltip('nombre_actividad', title='Actividad'), 
                    alt.Tooltip('division_titulo', title='División CIIU Rev 4'),
                    alt.Tooltip('OBS_VALUE', title='Empleo'),
            ] 

        )

        # Create a horizontal line at y = -1.14
        rule = alt.Chart(pd.DataFrame({'y': [-1.14]})).mark_rule(color='red').encode(y='y:Q')

        
        st.altair_chart( 
            (plot_intensivo + rule).properties(
                title=alt.TitleParams(
                    "Diagrama Distancia-PCI (Intensivo)",
                    subtitle="Honduras. Datos de Empleo de OECD SBS 2019",
                    subtitleColor="gray"
                )
            ), theme=None, use_container_width=True
        )

    elif criterio == "Margen Extensivo":
        cdata_intensivo = cdata_hnd.filter(
            (pl.col("REF_AREA")=="HND") & 
            (pl.col("rca")>0) & 
            (pl.col("mcp")==0)
        )

        plot_intensivo = alt.Chart(
            cdata_intensivo.join(
            mapp_ciiu,
            left_on="ACTIVITY", 
            right_on="codigo"
        ).join(
            ciiu_pedro_2.select("clase_codigo", "clase_titulo", "seccion_codigo", "seccion_titulo", "division_titulo"),
            left_on= "ACTIVITY", 
            right_on = "clase_codigo"
        )
        ).mark_circle(
                    opacity=0.99,
                    stroke='black',
                    strokeWidth=1.2,
                    strokeOpacity=0.9, 
                    size=180,     
                ).encode(
            x=alt.X('distance').scale(zero=False).title("Distancia"),
            y=alt.Y('pci').title("PCI"),#.scale(type ="log"),
            color = alt.Color("seccion_titulo", legend=alt.Legend(columns=2)).title("Sección"),
            size = alt.Size("OBS_VALUE").scale(type ="log").title("Empleo"),
            tooltip=[
                
                    alt.Tooltip('nombre_actividad', title='Actividad'), 
                    alt.Tooltip('division_titulo', title='División CIIU Rev 4'),
                    alt.Tooltip('OBS_VALUE', title='Empleo'),
            ]        
            ).properties(
            width=300,
            height=300
        )


        # Create a horizontal line at y = -1.14
        rule = alt.Chart(pd.DataFrame({'y': [-1.14]})).mark_rule(color='red').encode(y='y:Q')

        
        st.altair_chart( 
            (plot_intensivo + rule).properties(
                title=alt.TitleParams(
                    "Diagrama Distancia-PCI (Extensivo)",
                    subtitle="Honduras. Datos de Empleo de OECD SBS 2019",
                    subtitleColor="gray"
                )
            ).configure_legend(
            titleFontSize=12,
            labelFontSize=10,

        ) , theme=None, use_container_width=True
        )

with st.sidebar:
    st.header("")

    selected_criteria = st.selectbox(
        label="Escoge Criterio de Especialización",
        options=["Todas las Industrias", "Margen Intensivo", "Margen Extensivo"] ,
        key="ex_category",
        bind="query-params",
    )

st.markdown(f"## {selected_criteria}")

plot_industrias(selected_criteria)