import inspect
import textwrap
import polars as pl
import streamlit as st
import altair as alt 


st.title(":material/bar_chart: Portafolios de Diversificación")

### Cargamos datos
portafolios = pl.read_csv("datos/portafolios.csv")
cdata_hnd = pl.read_csv("datos/cdata_hnd.csv")



### Define ponderadores
product_selection_criteria = {
    "Low-hanging Fruit" : {"cog" : 0.15, "pci" : 0.05, "density" : 0.8},
    "Balanced Portfolio" : {"cog" : 0.25, "pci" : 0.25, "density" : 0.5},
    "Long Jumps" : {"cog" : 0.45, "pci" : 0.35, "density" : 0.2},
}

### Mapeo portafolios - prefijos
mapp_portafolios = {
    "lhf" : "Low-hanging Fruit", 
    "bp" : "Balanced Portfolio", 
    "lj" : "Long Jumps"
}

mapp_portafolios_inv = {v:k for k,v in mapp_portafolios.items()}


def plot_portafolios( selected_criteria : str):
    ### Clases a priorizar
    clases_ciiu_priorizar = portafolios.filter(portafolio=mapp_portafolios_inv[selected_criteria])["clase_codigo"].to_numpy()

    #### Priorizados
    points_prioriza = cdata_hnd.filter(
                (pl.col("ACTIVITY").is_in(clases_ciiu_priorizar)) 
    )

    #### No Priorizados
    points_resto = cdata_hnd.filter(
                ~pl.col("ACTIVITY").is_in(clases_ciiu_priorizar)   
    )

    # Create an Altair chart
    selection_weigths = ", ".join([f"{i} = {j}" for i,j in product_selection_criteria[selected_criteria].items()])
    selection_weigths = "Weights : " + selection_weigths



    ### Priorized product plots
    relateness_plot_prioriza = alt.Chart(points_prioriza).mark_point(filled=True, size=230, stroke = "black").encode(
        alt.X('distance', title="Distancia").scale(domain=(cdata_hnd["distance"].min()-0.02,cdata_hnd["distance"].max() + 0.02)), # Encoding along the x-axis
        alt.Y("pci", title="Complejidad").scale(domain=(-4,8)), # Encoding along the y-axis
        color='seccion_titulo', # Category encoding by color
        tooltip=[
                
                    alt.Tooltip('clase_titulo', title='Actividad'), 
                    alt.Tooltip('seccion_titulo', title='Sección CIIU Rev 4'),
                    alt.Tooltip('distance', title='Distancia'),
                    alt.Tooltip('pci', title='PCI'),
            ] 
    ).properties(
        title = [f"Relatedness-complexity diagram - HND - Year : 2019", 
                 "Complejidad", 
                selection_weigths],

    )

    ### Unpriorized product plots
    relateness_plot = alt.Chart(points_resto).mark_point(filled=True, size=230, opacity=0.3).encode(
        alt.X('distance', title="Distancia").scale(domain=(cdata_hnd["distance"].min(),cdata_hnd["distance"].max())), # Encoding along the x-axis
        alt.Y("pci", title="Complejidad"), # Encoding along the y-axis
        color=alt.Color('seccion_titulo', title = "Seccion"), # Category encoding by color
        tooltip=[
                
                    alt.Tooltip('clase_titulo', title='Actividad'), 
                    alt.Tooltip('seccion_titulo', title='Sección CIIU Rev 4'),
                    alt.Tooltip('distance', title='Distancia'),
                    alt.Tooltip('pci', title='PCI'),
            ]     
        )

    st.altair_chart( relateness_plot_prioriza + relateness_plot , theme=None, use_container_width=True)


with st.sidebar:
    st.header("Covariables")

    selected_criteria = st.selectbox(
        label="Escoge Criterio Selección de Industrias",
        options=["Low-hanging Fruit", "Balanced Portfolio" , "Long Jumps"] ,
        key="ex_category",
        bind="query-params",
    )



st.markdown(f"## {selected_criteria}")

plot_portafolios(selected_criteria)