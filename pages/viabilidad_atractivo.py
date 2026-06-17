import streamlit as st
from utils import factores_descripcion

st.title(":material/bar_chart: Factores de Viabilidad y Atractivo")



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

        st.markdown(f"## {selected_criteria}")