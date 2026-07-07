import numpy as np
from pymcdm.methods import TOPSIS
from pymcdm.helpers import rrankdata
from typing import List 
import polars as pl
import pandas as pd 

factores_descripcion = {
    "Capacidad para movilizar FDI (Mundo y América Latina)" : 
    """
    - Monto acumulado del monto acumulado de inversión en capital y creacion de empleo entre 2019 y 2024 en el mundo y América Latina.

    - Tasa de crecimiento compuesta de la inversión entre 2019 y 2024 en el mundo y América Latina.

    - Elasticidad de crecimiento del empleo al crecimiento de la inversión. 
    >Fuente : FDI Markets

    >La Elasticidad de crecimiento del empleo al crecimiento de la inversión mide cómo responde el empleo a los cambios en la inversión extranjera directa (IED) en un sector específico. Indica cuánto crece el empleo de la industria por cada 1 % de aumento en el crecimiento sectorial del FDI.
    """,
    "Crecimiento de la industria a nivel mundial (Producción)" : 
    """
    - Crecimiento de la Producción de las industrias en el mundo. 
    >Fuente : OECD Structural Business Statistics
    """,
    "Crecimiento de la industria a nivel mundial (Exportaciones)" : 
    """
    - Calculamos el crecimiento de la industria CIIU al calcular el crecimiento en exportaciones de los productos que componen a cada industria. De acuerdo a la metodología de Liao et al (2020) descomponen la industria CIIU por los productos que la intengran, ponderado por el peso relativo de cada producto en la industria. Con tales ponderadores se calcula con los datos del Atlas de Complejidad Económica el crecimiento exportador de la industria en el mundo.
    >Fuente : Atlas de Complejidad 
    """,
    "Posibilidad de sustituir las importaciones estadounidenses procedentes de China" : 
    """
    - Se estima la posibilidad de sustituir importaciones de China en USA al calcular la razón promedio ponderada de la industria CIIU a ser importada por USA desde China. Usando la metodología de Liao et al (2020) se calcula la razón de importación por producto proveniente de China con respecto al total de importación para USA. Con el peso relativo de cada producto en la industria se calcula la razón promedio poderada de la industria.
    >Fuente : Atlas de Complejidad 

    """,
    "Capacidad para generar empleo" : 
    """
    - Elasticidad de crecimiento del empleo al crecimiento del producto de la industria. Este indicador mide cómo responde el empleo a los cambios en el producto de la industria. Indica cuánto crece el empleo de la industria por cada 1 % de aumento en el producto.
    >Fuente : OECD Structural Business Statistics

    """,
    "Fortaleza en países como Honduras (RCA en el grupo de pares)" : 
    """
    
    - Elasticidad promedio de las industrias en Ecuador y El Salvador.
    """,
    "Disponibilidad de Insumos"  : 
    """

    - Se calculo una razón de productos disponibles o presentes por industria.
    - Para la construcción de este indicador, se usó la metodología de Liao et al (2020) quienes descomponen la industria CIIU por los productos que la intengra, ponderado por el peso relativo de cada producto en la industria. Además, usamos los datos de [AI-generated Production Network - AIPNET](https://aipnet.io/) para identificar la cadena de producción de los productos.
    - Para cada producto, calculamos la razón de productos disponibles en el país al contabilizar la cantidad de productos en el país que tienen RCA mayor o igual a 1 con respecto al total de productos que se necesita para la producción. 
    - Con esta razón de productos disponibles **por producto**, usamos los ponderadores de Liao et al (2020) para calcular la razón de disponibilidad **por industria** al multiplicar y sumar la razón de productos disponibles por producto y los ponderadores del peso relativo del producto en la industria.
    """,

    "Dependencia de una restricción o restricción potencial (Energía)"  : 
    """

    - El indicador es la razón entre el valor de las compras de productos de energía y el valor total de las compras en bienes y servicios de la industria.
    >Fuente : OECD Structural Business Statistics
    """,

    "Dependencia de una restricción o restricción potencial (Electricidad)"  : 
    """
    - El indicador es la razón entre el Gasto por consumo de energía eléctrica y los Gastos Totales por consumo de bienes y servicios de la industria.
    >Fuente : Censos Económicos 2023, INEGI.

    """,
    "Intensidad Institucional"  : 
    """
    - AGREGAR DESCRIPCION.
    >Fuente : AGREGAR FUENTE.

    """,
}
                     

cw_atractivo = {
    "Monto acumulado de inversión en capital (Mundo)" : "cumulative_investment_world", 
    "Monto acumulado de inversión en capital (LAC)" : "cumulative_investment_lac",
    "Tasa de crecimiento de la inversión (Mundo)" : "cagr_investment_world",
    "Tasa de crecimiento de la inversión (LAC)" : "cagr_investment_lac",
    "Elasticidad Empleo/Inversión (Mundo)" : "elasticidad_empleo_fdi_world",
    "Elasticidad Empleo/Inversión (LAC)" : "elasticidad_empleo_fdi_lac",
    "Crecimiento del Producto" : "cagr_production",
    "Crecimiento de Exportaciones" : "cagr_exports",
    "Posibilidad de sustituir las importaciones estadounidenses procedentes de China" : "share_imports_china", 
    "Capacidad para crear empleo" : "elasticidad_empleo_producto"
}

                
                 
                
                

cw_viabilidad = {
    "Fortaleza en países como Honduras (RCA en el grupo de pares)" : "rca_peers",
    "Disponibilidad de Insumos" : "razon_insumos_presentes", 
    "Dependencia de una restricción o restricción potencial (Energía)" : "share_energy",
    "Dependencia de una restricción o restricción potencial (Electricidad)" : "razon_electricidad_gasto_total",
    "Intensidad Institucional" : "institutional_intensity"
}

viabilidad_direccion = {
    "Fortaleza en países como Honduras (RCA en el grupo de pares)" : 1,
    "Disponibilidad de Insumos" : 1, 
    "Dependencia de una restricción o restricción potencial (Energía)" : -1,
    "Dependencia de una restricción o restricción potencial (Electricidad)" : -1,
    "Intensidad Institucional" : -1
}

atractivo_direccion = {
    "Monto acumulado de inversión en capital (Mundo)" : 1, 
    "Monto acumulado de inversión en capital (LAC)" : 1,
    "Tasa de crecimiento de la inversión (Mundo)" : 1,
    "Tasa de crecimiento de la inversión (LAC)" : 1,
    "Elasticidad Empleo/Inversión (Mundo)" : 1,
    "Elasticidad Empleo/Inversión (LAC)" : 1,
    "Crecimiento del Producto" : 1,
    "Crecimiento de Exportaciones" : 1,
    "Posibilidad de sustituir las importaciones estadounidenses procedentes de China" : 1, 
    "Capacidad para crear empleo" : 1
}

def calcula_topsis(
        cdata_honduras : pl.DataFrame,
        factores : pl.DataFrame, 
        factores_viabilidad : List[str],
        factores_atractivo : List[str], 
    ):

    ## Selecciona factores de viabilidad y atractivo
    viabilidad_factores = [cw_viabilidad[factor] for factor in factores_viabilidad]
    atractivo_factores = [cw_atractivo[factor] for factor in factores_atractivo]

    ### TOPSIS Atractivo
    alts_atractivo = factores.select(atractivo_factores).to_numpy()

    # Define criteria weights (should sum up to 1)
    weights_atractivo = np.array([1/len(atractivo_factores)]*len(atractivo_factores))

    # Define criteria types (1 for profit, -1 for cost)
    types_atractivo = np.array([1]*len(atractivo_factores))

    # Create object of the method
    # Note, that default normalization method for TOPSIS is minmax
    topsis_atractivo = TOPSIS()

    # Determine preferences and ranking for alternatives
    pref_atractivo = topsis_atractivo(alts_atractivo, weights_atractivo, types_atractivo)
    ranking_atractivo = rrankdata(pref_atractivo)

    ### TOPSIS Viabilidad
    alts_viabilidad = factores.select(viabilidad_factores).to_numpy()

    # Define criteria weights (should sum up to 1)
    weights_viabilidad = np.array([1/len(viabilidad_factores)]*len(viabilidad_factores))

    # Define criteria types (1 for profit, -1 for cost)
    types_viabilidad = np.array([viabilidad_direccion[factor] for factor in factores_viabilidad])

    # Create object of the method
    # Note, that default normalization method for TOPSIS is minmax
    topsis_viabilidad = TOPSIS()

    # Determine preferences and ranking for alternatives
    pref_viabilidad = topsis_viabilidad(alts_viabilidad, weights_viabilidad, types_viabilidad)
    ranking_viabilidad = rrankdata(pref_viabilidad)

    ### Creamos data frame con los scores de viabilidad y atractivo
    scores_viabilidad_atractivo = factores.select("ciiu").with_columns(
            topsis_atractivo = pref_atractivo, 
            topsis_viabilidad = pref_viabilidad, 
    ).with_columns(
        pl.col("ciiu").cast(pl.Int64)
    )

    ### Reunimos scores con datos de complejidad de honduras
    cdata_honduras = cdata_honduras.join(
            scores_viabilidad_atractivo, 
            left_on="ACTIVITY", 
            right_on="ciiu"
        )

    return cdata_honduras

def calcula_normalized_decision_matrix(
        cdata_honduras : pl.DataFrame,
        factores : pl.DataFrame, 
        factores_lista_long_name : List[str],
        tipo_factor : str
    ):

    ## Selecciona factores de viabilidad y atractivo
    if tipo_factor == "atractivo": 
        factores_lista = [cw_atractivo[factor] for factor in factores_lista_long_name]
    elif tipo_factor == "viabilidad": 
        factores_lista = [cw_viabilidad[factor] for factor in factores_lista_long_name]

    ### TOPSIS 
    alts = factores.select(factores_lista).to_numpy()

    # Define criteria weights (should sum up to 1)
    weights = np.array([1/len(factores_lista)]*len(factores_lista))

    # Define criteria types (1 for profit, -1 for cost)
    if tipo_factor == "atractivo": 
        types = np.array([atractivo_direccion[factor] for factor in factores_lista_long_name])
    elif tipo_factor == "viabilidad": 
        types = np.array([viabilidad_direccion[factor] for factor in factores_lista_long_name])

    # Create object of the method
    # Note, that default normalization method for TOPSIS is minmax
    topsis = TOPSIS()

    # Determine preferences and ranking for alternatives
    pref = topsis(alts, weights, types)
    ranking = rrankdata(pref)

    # If you want to inspect computation process in details
    results = topsis(alts, weights, types, verbose=True)

    # Construimos Normalized decision matrix
    normalized_decision_matrix =  results.results[0].data
    normalized_decision_matrix = pd.DataFrame(
        normalized_decision_matrix, 
        columns=factores_lista,
        index = factores["ciiu"]
        
    )
    normalized_decision_matrix.index.name = "ciiu"
    normalized_decision_matrix = normalized_decision_matrix.reset_index()
    normalized_decision_matrix["ciiu"] = normalized_decision_matrix["ciiu"].astype(int)

    print(normalized_decision_matrix.shape)

    ## Reunimos los nombres de las clases
    normalized_decision_matrix = cdata_honduras.select("ACTIVITY", "clase_titulo").join(
        pl.from_pandas(normalized_decision_matrix), 
        left_on="ACTIVITY", 
        right_on="ciiu"
    ).to_pandas()
    
    
    return normalized_decision_matrix

def build_radar_data(
        cdata_honduras : pl.DataFrame,
        factores : pl.DataFrame, 
        factores_lista_long_name : List[str],
        tipo_factor : str,
        industria : str):

    datos = calcula_normalized_decision_matrix(
        cdata_honduras,
        factores, 
        factores_lista_long_name,
        tipo_factor
    )

    ## Selecciona factores de viabilidad y atractivo
    if tipo_factor == "atractivo": 
        criterios = [cw_atractivo[factor] for factor in factores_lista_long_name]
    elif tipo_factor == "viabilidad": 
        criterios = [cw_viabilidad[factor] for factor in factores_lista_long_name]


    radar_data = datos.query(f"clase_titulo == '{industria}'")[criterios]
    
    indicator_data = [
        {
            "name" : criterio, 
            "max" : 1.0
        }
        for criterio in factores_lista_long_name
    ] 

    data = [
        {
            "value" : list(np.round(radar_data.to_numpy()[0], 2) ), 
            "name" : industria, 

            "symbol": 'rect',
            "symbolSize": 16,
            "lineStyle": {
                "type": 'dashed'
            },
            "label": {
                "show": True,
            }, 
          "areaStyle": {
            "color": 'rgba(255, 228, 52, 0.6)'
          }

        }
    ]

    return indicator_data, data
    