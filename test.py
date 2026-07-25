import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return


@app.cell
def _():
    import pandas as pd
    import altair as alt 
    import polars as pl

    return alt, pd, pl


@app.cell
def _(pd, pl):
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


    return cdata_hnd, color_industria, industrias_seleccionadas_lista


@app.cell
def _(alt, cdata_hnd, color_industria, industrias_seleccionadas_lista, pd):
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
        shape = alt.Shape("mcp:N").title("M"),
        #color = alt.Color("rca").scale(type ="log", scheme='redblue', domainMid=1.0).title("RCA"),
        color = alt.Color("Industria Seleccionada"),
        #size = alt.Size("rca").scale(type ="log").title("RCA"),
        tooltip=[
        
                alt.Tooltip('clase_titulo', title='Actividad'), 
                alt.Tooltip('rca', title='RCA')
        ] 
    )

    industria_plot = alt.Chart(
        cdata_hnd.filter(clase_titulo="Elaboración de productos lácteos")
            ).mark_circle(
                opacity=0.99,
                stroke='black',
                strokeWidth=3.2,
                strokeOpacity=0.9, 
                size=700,     
            ).encode(
        x=alt.X('distance').scale(zero=False).title("Distancia"),
        y=alt.Y('pci').title("PCI"),
        color=alt.value(color_industria("Elaboración de productos lácteos", industrias_seleccionadas_lista)),
        tooltip=[
        
                alt.Tooltip('clase_titulo', title='Actividad'), 
                alt.Tooltip('rca', title='RCA')
        ] 
    )

    # Create a horizontal line at y = -1.14
    rule_pci = alt.Chart(pd.DataFrame({'y': [cdata_hnd["pci"].mean()]})).mark_rule(color='gray', strokeWidth=3, strokeDash=[4,4]).encode(y='y:Q')

    rule_distancia = alt.Chart(pd.DataFrame({'x': [cdata_hnd["distance"].mean()]})).mark_rule(color='gray', strokeWidth=3, strokeDash=[4,4]).encode(x='x:Q')


    (principal_plot + industria_plot + rule_pci + rule_distancia).properties(
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
    return


@app.cell
def _():
    return


@app.cell
def _(pl):
    factores = pl.read_csv("datos/factores.csv")
    factores
    return


@app.cell
def _(cdata_hnd):
    pci_promedio = cdata_hnd["pci"].mean()
    distancia_promedio = cdata_hnd["distance"].mean()

    perfil_industria = {i:j[0] for i,j in cdata_hnd.filter(clase_titulo="Fabricación de sustancias químicas básicas").to_dict(as_series=False).items()}


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

    build_perfil_texto(perfil_industria)
    return (perfil_industria,)


@app.cell
def _(perfil_industria):
    perfil_industria
    return


if __name__ == "__main__":
    app.run()
