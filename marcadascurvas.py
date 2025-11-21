import streamlit as st
import ezdxf # O la librería que uses

st.title("Generador de DXF Online")

# 1. Entradas de usuario
largo = st.number_input("Introduce el largo (mm)", min_value=0.0)
ancho = st.number_input("Introduce el ancho (mm)", min_value=0.0)

# 2. Botón para generar
if st.button("Generar DXF"):
    # Aquí va tu lógica de generación
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_line((0, 0), (largo, 0))
    # ... resto de tu código ...
    
    # 3. Guardar en memoria temporal para descargar
    nombre_archivo = "pieza.dxf"
    doc.saveas(nombre_archivo)
    
    with open(nombre_archivo, "rb") as file:
        btn = st.download_button(
            label="Descargar archivo DXF",
            data=file,
            file_name=nombre_archivo,
            mime="image/vnd.dxf"
        )