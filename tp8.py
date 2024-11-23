import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Análisis de Ventas", layout="wide")

# Función para cargar datos
@st.cache_data
def cargar_datos(archivo):
    return pd.read_csv(archivo)

# Función para calcular línea de tendencia
def calcular_tendencia(datos, x_col, y_col):
    x = datos[x_col].values
    y = datos[y_col].values
    coef = np.polyfit(x, y, 1)  # Ajuste lineal
    tendencia = coef[0] * x + coef[1]
    return tendencia

# Sidebar
st.sidebar.header("Cargar archivo de datos")
archivo_cargado = st.sidebar.file_uploader("Sube un archivo CSV", type=["csv"])

if archivo_cargado:
    # Cargar datos
    datos = cargar_datos(archivo_cargado)
    
    # Verificar estructura
    columnas_esperadas = ['Sucursal', 'Producto', 'Año', 'Mes', 'Unidades_vendidas', 'Ingreso_total', 'Costo_total']
    if not all(col in datos.columns for col in columnas_esperadas):
        st.error("El archivo CSV debe contener las columnas: " + ", ".join(columnas_esperadas))
    else:
        # Seleccionar sucursal
        sucursales = ["Todas"] + list(datos['Sucursal'].unique())
        sucursal_seleccionada = st.sidebar.selectbox("Seleccionar Sucursal", sucursales)

        # Filtrar datos
        if sucursal_seleccionada != "Todas":
            datos = datos[datos['Sucursal'] == sucursal_seleccionada]

        # Crear columna de Año-Mes
        datos['Año-Mes'] = datos['Año'].astype(str) + "-" + datos['Mes'].astype(str).str.zfill(2)

        # Agrupar por producto
        productos = datos['Producto'].unique()

        # Mostrar datos por producto
        st.title(f"Datos de {'Todas las Sucursales' if sucursal_seleccionada == 'Todas' else sucursal_seleccionada}")
        for producto in productos:
            st.subheader(producto)
            datos_producto = datos[datos['Producto'] == producto]

            # Calcular métricas
            unidades_vendidas = datos_producto['Unidades_vendidas'].sum()
            ingreso_total = datos_producto['Ingreso_total'].sum()
            costo_total = datos_producto['Costo_total'].sum()
            precio_promedio = ingreso_total / unidades_vendidas if unidades_vendidas > 0 else 0
            margen_promedio = (ingreso_total - costo_total) / ingreso_total if ingreso_total > 0 else 0

            # Mostrar métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Precio Promedio", f"${precio_promedio:,.2f}")
            col2.metric("Margen Promedio", f"{margen_promedio * 100:.2f}%")
            col3.metric("Unidades Vendidas", f"{unidades_vendidas:,.0f}")

            # Preparar datos para el gráfico
            datos_producto_agrupados = datos_producto.groupby('Año-Mes').agg({
                'Unidades_vendidas': 'sum'
            }).reset_index()
            datos_producto_agrupados['Año-Mes_Num'] = range(len(datos_producto_agrupados))

            # Calcular tendencia
            datos_producto_agrupados['Tendencia'] = calcular_tendencia(
                datos_producto_agrupados, 'Año-Mes_Num', 'Unidades_vendidas'
            )

            # Gráfico de evolución de ventas
            # Gráfico de evolución de ventas
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(datos_producto_agrupados['Año-Mes'], datos_producto_agrupados['Unidades_vendidas'], label="Ventas", color='blue')
            ax.plot(datos_producto_agrupados['Año-Mes'], datos_producto_agrupados['Tendencia'], label="Tendencia", color='red', linestyle='--')
            ax.set_title(f"Evolución de Ventas Mensual - {producto}")
            ax.set_xlabel("Año-Mes")
            ax.set_ylabel("Unidades Vendidas")
            ax.legend()

# Mejorar las etiquetas del eje X
            ax.set_xticks(datos_producto_agrupados['Año-Mes'][::6])  # Mostrar una etiqueta cada 6 meses (ajusta según el tamaño de tus datos)
            ax.tick_params(axis='x', rotation=45)  # Rotar las etiquetas 45 grados

            st.pyplot(fig)

