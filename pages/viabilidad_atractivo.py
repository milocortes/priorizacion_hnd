import streamlit as st
from utils import factores_descripcion
import polars as pl 
import altair as alt 
import pandas as pd 

st.title(":material/bar_chart: Factores de Viabilidad y Atractivo")

## Carga datos
cdata_intensivo = pl.read_csv("datos/honduras_intensivo_viabilidad_atractivo.csv")
cdata_extensivo = pl.read_csv("datos/honduras_extensivo_viabilidad_atractivo.csv")

def plot_industrias(criterio):


    # Define your custom mapping arrays
    group_domains = ['Actividades de servicios administrativos y de apoyo',
    'Actividades profesionales, científicas y técnicas',
    'Comercio al por mayor y al por menor; reparación de vehículos automotores y motocicletas',
    'Construcción',
    'Explotación de minas y canteras',
    'Industrias manufactureras',
    'Información y comunicaciones',
    'Suministro de agua; evacuación de aguas residuales, gestión de desechos y descontaminación',
    'Suministro de electricidad, gas, vapor y aire acondicionado',
    'Transporte y almacenamiento']

    color_range = [
        "#1f77b4", 
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#FFFF00",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]


    if criterio == "Margen Intensivo": 

        plot_intensivo = alt.Chart(
            cdata_intensivo    
        ).mark_circle(
                    opacity=0.99,
                    stroke='black',
                    strokeWidth=1.2,
                    strokeOpacity=0.9, 
                    size=200,     
                ).encode(
            x=alt.X('topsis_viabilidad').scale(zero=False).title("Viabilidad"),
            y=alt.Y('topsis_atractivo').scale(zero=False).title("Atractivo"),#.scale(type ="log"),
            color = alt.Color("seccion_titulo", scale=alt.Scale(domain=group_domains, range=color_range)).title("Sección"),
            #size = alt.Size("OBS_VALUE").scale(type ="log").title("Empleo"),
            tooltip=[

                    alt.Tooltip('nombre_actividad', title='Actividad'), 
                    alt.Tooltip('division_titulo', title='División CIIU Rev 4'),
                    alt.Tooltip('OBS_VALUE', title='Empleo'),
            ] 

        )

        # Create a horizontal line at y = -1.14
        rule_atractivo = alt.Chart(pd.DataFrame({'y': [cdata_intensivo["topsis_atractivo"].mean()]})).mark_rule(color='red').encode(y='y:Q')
        rule_viabilidad = alt.Chart(pd.DataFrame({'x': [cdata_intensivo["topsis_viabilidad"].mean()]})).mark_rule(color='red').encode(x='x:Q')


        plot_intensivo = (plot_intensivo + rule_atractivo + rule_viabilidad).properties(
        #plot_intensivo.properties(
                title=alt.TitleParams(
                    "Diagrama Viabilidad-Atractivo",
                    subtitle="Margen Intensivo",
                    subtitleColor="gray"
                )
        )

        st.altair_chart(plot_intensivo, theme=None, use_container_width=True)
    elif criterio == "Margen Extensivo":


        plot_extensivo = alt.Chart(
            cdata_extensivo    
        ).mark_circle(
                    opacity=0.99,
                    stroke='black',
                    strokeWidth=1.2,
                    strokeOpacity=0.9, 
                    size=200,     
                ).encode(
            x=alt.X('topsis_viabilidad').scale(zero=False).title("Viabilidad"),
            y=alt.Y('topsis_atractivo').scale(zero=False).title("Atractivo"),#.scale(type ="log"),
            color = alt.Color("seccion_titulo", scale=alt.Scale(domain=group_domains, range=color_range)).title("Sección"),
            #size = alt.Size("OBS_VALUE").scale(type ="log").title("Empleo"),
            tooltip=[

                    alt.Tooltip('nombre_actividad', title='Actividad'), 
                    alt.Tooltip('division_titulo', title='División CIIU Rev 4'),
                    alt.Tooltip('OBS_VALUE', title='Empleo'),
            ] 

        )

        # Create a horizontal line at y = -1.14
        rule_extensivo_atractivo = alt.Chart(pd.DataFrame({'y': [cdata_extensivo["topsis_atractivo"].mean()]})).mark_rule(color='red').encode(y='y:Q')
        rule_extensivo_viabilidad = alt.Chart(pd.DataFrame({'x': [cdata_extensivo["topsis_viabilidad"].mean()]})).mark_rule(color='red').encode(x='x:Q')


        plot_extensivo = (plot_extensivo + rule_extensivo_atractivo + rule_extensivo_viabilidad).properties(
        #plot_intensivo.properties(
                title=alt.TitleParams(
                    "Diagrama Viabilidad-Atractivo",
                    subtitle="Margen Extensivo",
                    subtitleColor="gray"
                )
        )

        st.altair_chart(plot_extensivo, theme=None, use_container_width=True)



tab1, tab2 = st.tabs(
    ["Descripción", "Resultados"], default="Descripción"
)

with tab1:
    col1, col2 = st.columns(2, border=True)

    with col1:
        st.header("**Atractivo**")
        st.markdown(
            """
            - Capacidad para movilizar FDI (Mundo y América Latina)
            - Crecimiento de la industria a nivel mundial (Empleo)
            - Crecimiento de la industria a nivel mundial (Exportaciones)
            - Posibilidad de sustituir las importaciones estadounidenses procedentes de China.
            - Capacidad para generar empleo.

            """
        )
    with col2:
        st.header("**Viabilidad**")
        st.markdown(
            """
            - Fortaleza en países como Honduras (RCA en el grupo de pares)
            - Disponibilidad de Insumos.
            - Dependencia de una restricción o restricción potencial (Energía) 
            - Dependencia de una restricción o restricción potencial (Electricidad) 

            """
        )


    action = st.menu_button("Descripción del Factor", options=factores_descripcion.keys())

    if action != None:
        st.markdown(f"## {action}")
        st.write(factores_descripcion[action])

        if action== "Capacidad para movilizar FDI (Mundo y América Latina)":
            st.latex(r'''
                \text { Elasticity }(\epsilon)=\frac{\% \text { Change in Employment }}{\% \text { Change in FDI }}
                ''')
            st.markdown(
                """
                * Si ε > 0 y < 1, el sector crea empleo, pero FDI también aumenta.
                * Si ε > 1, el sector es altamente intensivo en mano de obra y genera muchos empleos en relación con FDI.
                """
            )

        elif action == "Capacidad para generar empleo":
            st.latex(r'''
                \text { Elasticity }(\epsilon)=\frac{\% \text { Change in Employment }}{\% \text { Change in Output }}
                ''')
            st.markdown(
                """
                * Si ε > 0 y < 1, el sector crea empleo, pero el producto de la industria también aumenta.
                * Si ε > 1, el sector es altamente intensivo en mano de obra y genera muchos empleos en relación con el producto de la industria.
                """
            )    

with tab2:
    with st.sidebar:
        st.header("")

        selected_criteria = st.selectbox(
            label="Escoge Criterio de Especialización",
            options=["Margen Intensivo", "Margen Extensivo"] ,
            key="ex_category",
            bind="query-params",
        )
    
    st.markdown(
        """
    Posterior a la identificación de industrias clave dentro del espectro de alternativas económicas
    se aplicó la técnica **TOPSIS (Technique for Order of Preference by Similarity to Ideal
    Solution)**. Esta técnica pertenece al conjunto de métodos conocidos como **Decisión
    Multicriterio**, que se utiliza para **evaluar y ordenar múltiples opciones frente a un conjunto
    de criterios de valoración**. 
    
    TOPSIS destaca por su capacidad para determinar la cercanía de una alternativa a la solución ideal, que se define como la instancia donde cada criterio alcanza
    su valor óptimo o solución ideal.


    TOPSIS estima un ranking normalizado entre 0 y 1, donde 1 indica una coincidencia perfecta con la solución ideal. Este ranking proporciona una jerarquía clara de priorización industrial, develando aquellas industrias con el mayor potencial estratégico.

    Los criterios seleccionados para definir esta solución ideal corresponden a los factores de viabilidad y atractivo.
 

        """
    )

    st.markdown(f"## {selected_criteria}")
    plot_industrias(selected_criteria)