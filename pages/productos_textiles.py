import streamlit as st
from utils import condiciones_fases, textiles_topsis_viabilidad_atractivo
import polars as pl 
import altair as alt 
import pandas as pd 

st.title(":material/bar_chart: Productos Textiles : Factores de Viabilidad y Atractivo")

textiles_factores = pl.read_csv("datos/textiles_factores_topsis_complejidad.csv") 

top_n = st.selectbox(
    "Selecciona Top de Productos",
    (10, 15, 20),
)

textiles_topsis = textiles_topsis_viabilidad_atractivo(textiles_factores, top_n)


# Define your custom mapping arrays
group_domains = [
  "Other vegetable textile fibres",
  "Man-made staple fibres",
  "Impregnated, coated or laminated textile fabrics",
  "Man-made filaments",
  "Furniture",
  "Wadding, felt and nonwovens",
  "Knitted fabrics",
  "Wool",
  "Special woven fabrics"
]

color_range = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
"#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]


plot_textiles = alt.Chart(
        textiles_topsis
        ).mark_circle(
            opacity=0.99,
            stroke='black',
            strokeWidth=1.2,
            strokeOpacity=0.9, 
            size=180,     
        ).encode(
    y=alt.Y('topsis_atractivo').scale(zero=False).title("Atractivo"),
    x=alt.X('topsis_viabilidad').scale(zero=False).title("Viabilidad"),#.scale(type ="log"),
    color = alt.Color("cluster", scale=alt.Scale(domain=group_domains, range=color_range)).title("Cluster"),
    #size = alt.Size("topsis_atractivo"),
    tooltip=[

            alt.Tooltip('Actividad', title='Actividad'), 
    ] 
).properties(
    title=alt.TitleParams(
        "Diagrama Complejidad-Viabilidad-Atractivo",
        #subtitle="Honduras. Datos de Empleo de OECD SBS 2019",
        subtitleColor="gray"
    )
)

# Create a horizontal line at y = -1.14
textiles_rule_atractivo = alt.Chart(pd.DataFrame({'y': [textiles_topsis["topsis_atractivo"].mean()]})).mark_rule(color='gray', strokeWidth=3, strokeDash=[4,4]).encode(y='y:Q')
textiles_rule_viabilidad = alt.Chart(pd.DataFrame({'x': [textiles_topsis["topsis_viabilidad"].mean()]})).mark_rule(color='gray', strokeWidth=3, strokeDash=[4,4]).encode(x='x:Q')

# 2. Quadrant labels dataframe with custom coordinates
# Change these values to position text exactly where you want it
textiles_quadrant_labels = pd.DataFrame({
    'y_pos': [textiles_topsis["topsis_atractivo"].max(), 
            textiles_topsis["topsis_atractivo"].min()*1.05, 
            textiles_topsis["topsis_atractivo"].max(),
            textiles_topsis["topsis_atractivo"].min()*1.05],     # X coordinates for text
    'x_pos': [textiles_topsis["topsis_viabilidad"].max()*0.95,
            textiles_topsis["topsis_viabilidad"].max()*0.95,
            textiles_topsis["topsis_viabilidad"].min()*1.05,
            textiles_topsis["topsis_viabilidad"].min()*1.05],     # Y coordinates for text
    'label': ['Fase I', 'Fase II', 'Fase III', 'Fase IV'],
    'align': ['right', 'left', 'left', 'right'] # Optional: aligns text inside boundaries
})

# 5. Quadrant text layer
textiles_text_layer = alt.Chart(textiles_quadrant_labels).mark_text(
    size=16,
    fontStyle='bold',
    color='black'
).encode(
    x='x_pos:Q',
    y='y_pos:Q',
    text='label:N'
)

plot_textiles = (plot_textiles + textiles_rule_atractivo + textiles_rule_viabilidad + textiles_text_layer).properties(
#plot_intensivo.properties(
        title=alt.TitleParams(
            "Diagrama Viabilidad-Atractivo",
            subtitle="Productos Textiles",
            subtitleColor="gray"
        )
)

st.altair_chart(plot_textiles, theme=None, use_container_width=True)


textiles_topsis_fases = textiles_topsis.with_columns(
        Fase = pl.coalesce(
                pl.when(cond).then(pl.lit(val)) for val, cond in condiciones_fases.items()
            )
).rename(
    {
        "hs12" : "HS12", 
        "topsis_atractivo" : "TOPSIS Atractivo",
        "topsis_viabilidad" : "TOPSIS Viabilidad", 
        "topsis_complejidad" : "TOPSIS Complejidad", 
        "cluster" : "Cluster"
    }
).sort("Fase", "Cluster")

# Pass configuration into st.dataframe
st.dataframe(
    textiles_topsis_fases.sort("Fase", "Cluster"),
    column_config={
        "Fase": st.column_config.TextColumn(
            "Fase", 
            help="Fase de priorización",
            max_chars=20
        ),
        "Cluster": st.column_config.TextColumn(
            "Cluster", 
            max_chars=20
        ),
        "HS12": st.column_config.TextColumn(
            "Clave HS12", 
            #display_text="Click here to Buy"
            max_chars=20
        ), 
        "Actividad" : st.column_config.TextColumn(
            "Nombre HS12", 
            #display_text="Click here to Buy"
            max_chars=20
        ),
        "TOPSIS Complejidad" : st.column_config.TextColumn(
            "TOPSIS Complejidad", 
            #display_text="Click here to Buy"
            max_chars=20
        ), 
        "TOPSIS Viabilidad" : st.column_config.TextColumn(
            "TOPSIS Viabilidad", 
            #display_text="Click here to Buy"
            max_chars=20
        ), 
        "TOPSIS Atractivo" : st.column_config.TextColumn(
            "TOPSIS Atractivo", 
            #display_text="Click here to Buy"
            max_chars=20
        ),  
    },
    hide_index=True,
    use_container_width=True
)