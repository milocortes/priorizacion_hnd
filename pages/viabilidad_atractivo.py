import streamlit as st
from utils import factores_descripcion, calcula_topsis
import polars as pl 
import altair as alt 
import pandas as pd 

st.title(":material/bar_chart: Factores de Viabilidad y Atractivo")

## Carga datos
factores = pl.read_csv("datos/factores.csv")
cdata_honduras = pl.read_csv("datos/cdata_honduras.csv")

### Resultados finales Intensivo
resultados_finales_intensivo = pd.read_excel("datos/seleccion_final_complexity.xlsx", sheet_name="intensivo")

### Resultados finales Extensivo
resultados_finales_extensivo = pd.read_excel("datos/seleccion_final_complexity.xlsx", sheet_name="extensivo")


#cdata_intensivo = pl.read_csv("datos/honduras_intensivo_viabilidad_atractivo.csv")
#cdata_extensivo = pl.read_csv("datos/honduras_extensivo_viabilidad_atractivo.csv")
#ciiu_finales = pl.read_csv("datos/ciiu_finales.csv")

#cdata_extensivo = cdata_extensivo.filter(
#    pl.col("ACTIVITY").is_in(ciiu_finales["ciiu"])
#)

def plot_industrias(criterio):


    # Define your custom mapping arrays
    group_domains = [
            "C1 Manufactura avanzada y metalmecánica",
            "C2 Química, materiales y farmacéutica",
            "C3 Agroindustria y alimentos procesados",
            "C4 Servicios empresariales intensivos en conocimiento (KIBS)",
            "C5 Turismo, conectividad y logística",
            "C6 Textiles, confección y materiales flexibles"
    ]
    color_range = [
        "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948"
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
            color = alt.Color("Clusters", scale=alt.Scale(domain=group_domains, range=color_range)).title("Cluster"),
            #size = alt.Size("OBS_VALUE").scale(type ="log").title("Empleo"),
            tooltip=[

                    alt.Tooltip('nombre_actividad', title='Actividad'), 
                    alt.Tooltip("ACTIVITY", title = "Código CIIU Rev 4"),
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
            color = alt.Color("Clusters", scale=alt.Scale(domain=group_domains, range=color_range)).title("Cluster"),
            #size = alt.Size("OBS_VALUE").scale(type ="log").title("Empleo"),
            tooltip=[

                    alt.Tooltip('nombre_actividad', title='Actividad'), 
                    alt.Tooltip("ACTIVITY", title = "Código CIIU Rev 4"),
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
            - Crecimiento de la industria a nivel mundial (Producción)
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
            - Intensidad Institucional

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

        #st.write("Factores Viabilidad:", selected_factores_viabilidad)

    ### Calcula topsis

    topsis_data = calcula_topsis(
        cdata_honduras,
        factores, 
        selected_factores_viabilidad,
        selected_factores_atractivo, 
    )

    cdata_intensivo = topsis_data.filter(
        pl.col("ACTIVITY").is_in(resultados_finales_intensivo["ciiu4_cod"])
    ).join(
        pl.from_pandas(resultados_finales_intensivo[["Clusters", "ciiu4_cod"]]) , 
        left_on="ACTIVITY", 
        right_on="ciiu4_cod"
    )

    cdata_extensivo = topsis_data.filter(
        pl.col("ACTIVITY").is_in(resultados_finales_extensivo["ciiu4_cod"])
    ).join(
        pl.from_pandas(resultados_finales_extensivo[["Clusters", "ciiu4_cod"]]) , 
        left_on="ACTIVITY", 
        right_on="ciiu4_cod"
    )
    print(cdata_extensivo.columns)

    st.markdown(f"## {selected_criteria}")
    plot_industrias(selected_criteria)