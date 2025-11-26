import streamlit as st
import ezdxf
from io import BytesIO, StringIO
import math

# Parametros dee configuración
roll_edgetrim = 20 # Margen para saneamiento de borde de rollo de tela, en milímetros.
conf_remainingminimum = 50 # Alto mínimo del último tramo de tela atravesada. Si es menor, se hace de este alto.
conf_seamoverlap = 10 # Solape de telas para empalme en mm.

# Funciones 
def create_dxf_rectangletraves_bytes(width: float, height: float) -> bytes:
    '''
    Genera el archivo DXF de marcada con curva para corte a través.
    Esta función genera la parte superior con curva.
    con los datos introduciros width, height, deflection.
    devuelve el contenido del archivo DXF como bytes (para descarga Streamlit).
    '''
    # Crear documento (DXF2010)
    doc = ezdxf.new(dxfversion="R2010", setup=True)
    msp = doc.modelspace()

    # Puntos del rectángulo
    p1 = (0.0, 0.0)
    p2 = (float(width), 0.0)
    p3 = (float(width), float(height))
    p4 = (0.0, float(height))

    # Añadir líneas
    msp.add_line(p1, p2)
    msp.add_line(p2, p3)
    msp.add_line(p3, p4)
    msp.add_line(p4, p1)

    # Guardar a cadena de texto
    text_stream = StringIO()
    doc.write(text_stream)

    text_value = text_stream.getvalue()
    encoding = getattr(doc, "output_encoding", "utf-8") or "utf-8"
    dxf_bytes = text_value.encode(encoding)

    return dxf_bytes

def create_dxf_rectangletravescurva_bytes(width: float, height: float, deflection: float) -> bytes:
    '''
    Genera el archivo DXF de marcada con curva para corte a través.
    Esta función genera las partes rectangulares inferiores.
    con los datos introduciros width, height.
    devuelve el contenido del archivo DXF como bytes (para descarga Streamlit).
    '''

    # Crear documento (DXF2010)
    doc = ezdxf.new(dxfversion="R2010", setup=True)
    msp = doc.modelspace()

    # Puntos del rectángulo
    p1 = (0.0, 0.0)
    p2 = (float(width), 0.0)
    p3 = (float(width), float(height))
    p4 = (0.0, float(height))

    # Punto medio de arco
    p5 = (float(width) / 2.0, float(height) - float(deflection))

    # Añadir líneas
    msp.add_line(p1, p2)
    msp.add_line(p2, p3)
    msp.add_line(p4, p1)

    # Añadir arco p3 → p5 → p4
    cx, cy, r, start_ang, end_ang = circle_from_3_points(p3, p4, p5)

    # Dibujar arco CCW
    msp.add_arc(center=(cx, cy), radius=r, start_angle=start_ang, end_angle=end_ang)

    # Guardar a cadena de texto
    text_stream = StringIO()
    doc.write(text_stream)

    encoding = getattr(doc, "output_encoding", "utf-8") or "utf-8"
    dxf_bytes = text_stream.getvalue().encode(encoding)

    return dxf_bytes

def create_dxf_hilo_bytes(width: float, height: float, deflection: float) -> bytes:
    '''
    Genera el archivo DXF de marcada con curva para corte al hilo,
    con los datos introduciros width, height, deflection.
    devuelve el contenido del archivo DXF como bytes (para descarga Streamlit).
    '''
    doc = ezdxf.new(dxfversion="R2010", setup=True)
    msp = doc.modelspace()

    # Puntos base de rectangulo
    p1 = (0.0, float(width))
    p2 = (0.0, 0.0)
    p3 = (float(height), 0.0)
    p4 = (float(height), float(width))

    # Punto central de flecha
    p5 = (float(height)  - float(deflection), float(width) / 2.0)

    # Dibujo de lineas rectas
    msp.add_line(p1, p2)
    msp.add_line(p2, p3)
    msp.add_line(p4, p1)

    # Añadir arco p3 → p5 → p4
    cx, cy, r, start_ang, end_ang = circle_from_3_points(p3, p4, p5)
    msp.add_arc(center=(cx, cy), radius=r, start_angle=start_ang, end_angle=end_ang)

    # Guardar a cadena de texto
    text_stream = StringIO()
    doc.write(text_stream)

    encoding = getattr(doc, "output_encoding", "utf-8") or "utf-8"
    dxf_bytes = text_stream.getvalue().encode(encoding)

    return dxf_bytes


def circle_from_3_points(p1, p2, p3):
    """
    Función auxiliar.
    Calcula el centro y radio del círculo que pasa por los 3 puntos dados.
    Devuelve (cx,cy, r, start_angle_deg, end_angle_deg)
    Ángulos en grados para DXF ARC (ángulo inicial → ángulo final CCW)
    """

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    # determinante
    det = 2 * (x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))
    if abs(det) < 1e-9:
        raise ValueError("Puntos colineales")

    # circumcentro
    a = x1**2 + y1**2
    b = x2**2 + y2**2
    c = x3**2 + y3**2

    cx = (a*(y2 - y3) + b*(y3 - y1) + c*(y1 - y2)) / det
    cy = (a*(x3 - x2) + b*(x1 - x3) + c*(x2 - x1)) / det

    r = math.hypot(cx - x1, cy - y1)

    # ángulos para DXF ARC
    start_ang = math.degrees(math.atan2(y1 - cy, x1 - cx))
    mid_ang   = math.degrees(math.atan2(y3 - cy, x3 - cx))
    end_ang   = math.degrees(math.atan2(y2 - cy, x2 - cx))

    # ordenar para que el arco vaya de p1 -> p3 -> p2
    def is_between(a, b, c):
        a, b, c = a % 360, b % 360, c % 360
        if a < c:
            return a < b < c
        return b > a or b < c

    if not is_between(start_ang, mid_ang, end_ang):
        start_ang, end_ang = end_ang, start_ang

    return cx, cy, r, start_ang, end_ang

# Main

def main():
    st.markdown("### Generador de marcadas con curva")

    st.write(
        "Introduce los datos para generar automáticamente las marcadas con curva "
        "para corte de tela. Dependiendo de las medidas de tela y del ancho rollo "
        "se generará marcada al hilo o al través. Si son necesarios empalmes se generará "
        "una marcada para cada parte de tela."
    )

    # Nombre de archivo DXF a generar y flecha de tubo
    file_name = st.text_input("Introduce aquí el nombre del archivo que se generará:")
    col1, col2 = st.columns(2)
    
    with col1:
        deflection = st.number_input("Flecha de tubo (mm):", min_value=0.0, step=0.01, value=10.0, format="%.1f")
    
    with col2:
        confection = st.selectbox("Confección:", options=["Hilo o través según medida", "Forzar confección atravesada"], index=0)


    st.markdown("---")

    # Inputs
    col3, col4 = st.columns(2)

    with col3:
        units = st.selectbox("Unidad de medida", options=["Centímetros", "Inches"], index=0)
        roll_width = st.number_input("Ancho rollo de tela", min_value=1, step=1, value=1, format="%d")

    with col4:
        width = st.number_input("Ancho tela (como indica la OF)", min_value=0.0, step=0.1, format="%.2f")
        height = st.number_input("Alto tela (como indica la OF)", min_value=0.0, step=0.1, format="%.2f")

    # Inicializar sesión para mantener botones Descarga DXF
    if "dxf_files" not in st.session_state:
        st.session_state.dxf_files = []

    # Generar DXFs
    if st.button("Generar marcadas"):
        # Clear previous files
        st.session_state.dxf_files = []

        # Validaciones básicas
        if not file_name:
            st.error("Por favor, introduce un nombre para el archivo que se generará.")
            st.stop()

        if width <= 0 or height <= 0:
            st.error("El ancho y alto deben ser mayores a 0.")
            st.stop()

        if deflection <= 0:
            st.error("La flecha debe ser mayor a 0.")
            st.stop()

        # Conversión de unidades
        if units == "Centímetros":  # convertir centímetros a milímetros
            width_mm = width * 10
            height_mm = height * 10
            roll_width_mm = roll_width * 10
        elif units == "Inches":  # Convertir inches a milímetros
            width_mm = width * 10 * 2.54
            height_mm = height * 10 * 2.54
            roll_width_mm = roll_width * 10 * 2.54
        else:
            width_mm = width
            height_mm = height
            roll_width_mm = roll_width

        # Generación de marcadas
        if width_mm <= (roll_width_mm - roll_edgetrim) and confection == "Hilo o través según medida":
            # Confección al hilo
            st.success(f"Generando marcada para confección al hilo en DXF...")
            dxf_bytes = create_dxf_hilo_bytes(width_mm, height_mm, deflection)
            out_name = f"{file_name}.dxf"
            st.session_state.dxf_files.append((out_name, dxf_bytes))

        else:
            # Confección al través
            n_files = math.ceil(height_mm / (roll_width_mm - roll_edgetrim))
            st.success(f"Generando {n_files} marcadas para confección atravesada en DXF...")
            pad = 2 if n_files > 1 else 0
            height_rectangles = roll_width_mm - roll_edgetrim  # Alturas de marcadas inferiores
            height_remaining = height_mm - ((n_files - 1) * (roll_width_mm-roll_edgetrim)) + ((n_files - 1) * conf_seamoverlap)
            if (height_remaining - deflection) < conf_remainingminimum:
                height_remaining = conf_remainingminimum + deflection

            for i in range(1, n_files + 1):
                if i < n_files:
                    # paños rectangulares
                    out_name = f"{file_name}_{i:0{pad}d}.dxf"
                    dxf_bytes = create_dxf_rectangletraves_bytes(width_mm, height_rectangles)
                    st.session_state.dxf_files.append((out_name, dxf_bytes))
                elif i == n_files:
                    # paño con curva
                    out_name = f"{file_name}_{i:0{pad}d}.dxf"
                    dxf_bytes = create_dxf_rectangletravescurva_bytes(width_mm, height_remaining, deflection)
                    st.session_state.dxf_files.append((out_name, dxf_bytes))

    # Mostrar botones de descarga de DXFs
    if st.session_state.dxf_files:
        st.markdown("---")
        for name, buffer in st.session_state.dxf_files:
            st.download_button(
                label=f"Descargar marcada {name}",
                data=BytesIO(buffer),
                file_name=name,
                mime="application/dxf"
            )


if __name__ == "__main__":
    main()