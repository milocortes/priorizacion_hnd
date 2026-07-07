import streamlit as st

st.set_page_config(
    page_title="Priorización de Industrias. Honduras",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

pg = st.navigation(
    [
        st.Page(
            "pages/showcase.py",
            title="Home",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page("pages/especializacion_industrias.py", title="Especialización de Industrias", icon=":material/code:"),
        st.Page("pages/portafolios.py", title = "Portafolios", icon = "🚀"), 
        st.Page("pages/viabilidad_atractivo.py", title = "Factores Viabilidad-Atractivo", icon = "🧮"),
        #st.Page("pages/perfil_industrias.py", title = "Perfil de Industrias", icon = "📊")
        #st.Page("pages/forecast_ml.py", title = "Pronóstico Modelos Aprendizaje de Máquina", icon = "📊"), 
        #st.Page("pages/actualiza_tokens.py", title = "Actualización de Tokens", icon = "🚨")
    ]
)
pg.run()

with st.sidebar:
    st.markdown(
        ":material/code: [streamlit-echarts](https://github.com/andfanilo/streamlit-echarts)"
    )
    st.caption("Made in :streamlit: by [@milocortes](https://github.com/milocortes)")
    #st.markdown(
    #    '<div style="margin-top: 0.75em;"><a href="https://www.buymeacoffee.com/andfanilo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174" style="border-radius: 12px;"></a></div>',
    #    unsafe_allow_html=True,
    #)