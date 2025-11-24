import streamlit as st
import ezdxf
from io import BytesIO, StringIO
import math

# Parametros dee configuración

roll_sanearborde = 20 # Margen para saneamiento de borde de rollo de tela, en milímetros
conf_altominimo = 30 # Alto mínimo del último tramo de tela atravesada. Si es menor se elimina.

# Funciones 

def create_rectangle_dxf_bytes_rectangle(width: float, height: float) -> bytes:
    """
    Create a DXF drawing containing a rectangle drawn with 4 LINE entities,
    return the DXF file content as bytes.
    """
    # create document (R2010 is fine)
    doc = ezdxf.new(dxfversion="R2010", setup=True)
    msp = doc.modelspace()

    # rectangle corners (origin at 0,0)
    p1 = (0.0, 0.0)
    p2 = (float(width), 0.0)
    p3 = (float(width), float(height))
    p4 = (0.0, float(height))

    # add four lines (explicitly create separate LINE entities)
    msp.add_line(p1, p2)
    msp.add_line(p2, p3)
    msp.add_line(p3, p4)
    msp.add_line(p4, p1)

    # write to a text stream (ezdxf.write() writes text)
    text_stream = StringIO()
    doc.write(text_stream)  # writes str to the text stream

    # get string and encode to bytes using the document's output encoding
    text_value = text_stream.getvalue()
    encoding = getattr(doc, "output_encoding", "utf-8") or "utf-8"
    dxf_bytes = text_value.encode(encoding)

    return dxf_bytes

def create_rectangle_dxf_bytes(width: float, height: float, deflection: float) -> bytes:
    """
    Create DXF with:
    - bottom line p1→p2
    - right line p2→p3
    - top is an arc through p3 → p5 → p4
    - left line p4→p1

    Returns DXF as bytes (for Streamlit download).
    """

    doc = ezdxf.new(dxfversion="R2010", setup=True)
    msp = doc.modelspace()

    # Base rectangle points
    p1 = (0.0, 0.0)
    p2 = (float(width), 0.0)
    p3 = (float(width), float(height))
    p4 = (0.0, float(height))

    # Midpoint with deflection
    p5 = (float(width) / 2.0, float(height) - float(deflection))

    # Add the straight lines
    msp.add_line(p1, p2)
    msp.add_line(p2, p3)
    msp.add_line(p4, p1)

    # --- Add the arc p3 → p5 → p4 ---
    cx, cy, r, start_ang, end_ang = circle_from_3_points(p3, p4, p5)

    # Draw the arc FROM p3 TO p4 passing through p5
    # ezdxf draws arcs CCW, so we ensure correct direction:
    msp.add_arc(center=(cx, cy), radius=r, start_angle=start_ang, end_angle=end_ang)

    # --- Write DXF into a text buffer ---
    text_stream = StringIO()
    doc.write(text_stream)

    encoding = getattr(doc, "output_encoding", "utf-8") or "utf-8"
    dxf_bytes = text_stream.getvalue().encode(encoding)

    return dxf_bytes

def create_dxf_hilo_bytes(width: float, height: float, deflection: float) -> bytes:

    doc = ezdxf.new(dxfversion="R2010", setup=True)
    msp = doc.modelspace()

    # Puntos base de rectangulo
    p1 = (float(height), 0.0)
    p2 = (0.0, 0.0)
    p3 = (float(width), 0.0)
    p4 = (float(width), float(height))

    # Punto central de flecha
    p5 = (float(width)  - float(deflection), float(height) / 2.0)

    # Dibujod e lineas rectas
    msp.add_line(p1, p2)
    msp.add_line(p2, p3)
    msp.add_line(p4, p1)

    # --- Add the arc p3 → p5 → p4 ---
    cx, cy, r, start_ang, end_ang = circle_from_3_points(p3, p4, p5)

    # Draw the arc FROM p3 TO p4 passing through p5
    # ezdxf draws arcs CCW, so we ensure correct direction:
    msp.add_arc(center=(cx, cy), radius=r, start_angle=start_ang, end_angle=end_ang)

    # --- Write DXF into a text buffer ---
    text_stream = StringIO()
    doc.write(text_stream)

    encoding = getattr(doc, "output_encoding", "utf-8") or "utf-8"
    dxf_bytes = text_stream.getvalue().encode(encoding)

    return dxf_bytes


def circle_from_3_points(p1, p2, p3):
    """
    Compute the center and radius of the circle passing through 3 points.
    Returns (cx, cy, r, start_angle_deg, end_angle_deg)
    Angles in degrees for DXF ARC (start_angle → end_angle CCW).
    """

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    # determinant
    det = 2 * (x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))
    if abs(det) < 1e-9:
        raise ValueError("Points are collinear")

    # circumcenter
    a = x1**2 + y1**2
    b = x2**2 + y2**2
    c = x3**2 + y3**2

    cx = (a*(y2 - y3) + b*(y3 - y1) + c*(y1 - y2)) / det
    cy = (a*(x3 - x2) + b*(x1 - x3) + c*(x2 - x1)) / det

    r = math.hypot(cx - x1, cy - y1)

    # angles for DXF ARC
    start_ang = math.degrees(math.atan2(y1 - cy, x1 - cx))
    mid_ang   = math.degrees(math.atan2(y3 - cy, x3 - cx))
    end_ang   = math.degrees(math.atan2(y2 - cy, x2 - cx))

    # ensure arc goes from p1 -> p3 -> p2
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

    st.write("Introduce los datos para generar automáticamente las marcadas con curva para corte de tela. Dependiendo de las medidas de tela y del ancho rollo se generará marcada al hilo o al través. Si son necesarios empalmes se generará una marcada para cada parte de tela.")

    # Nombre de archivo DXF a generar y flecha de tubo
    file_name = st.text_input("Introduce aquí el nombre del archivo que se generará:")
    deflection = st.number_input("Flecha de tubo (mm):", min_value=0.0, step=0.01, value=10.0, format="%.1f")

    st.markdown("---")

    # Input
    col1, col2 = st.columns(2)

    with col1:
        units = st.selectbox("Unidad de medida", options=["Centímetros", "Inches"], index=0)
        roll_width = st.number_input("Ancho rollo de tela", min_value=1, step=1, value=1, format="%d")

    with col2:
        width = st.number_input("Ancho tela (como indica la OF)", min_value=0.0, step=0.1, format="%.2f")
        height = st.number_input("Alto tela (como indica la OF)", min_value=0.0, step=0.1, format="%.2f")
        

    st.markdown("---")

    if st.button("Generar marcadas"):
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

        if deflection == "Centímetros": #convertir centímetros a milímetros
            width = width * 10
            height = height * 10
            roll_width = roll_width * 10
        elif deflection == "Inches": # Convertir inches a milímetros
            width = width * 10 * 2.54
            height = height * 10 * 2.54
            roll_width = roll_width * 10 * 2.54

        # Generación de marcadas

        if width <= (roll_width - roll_sanearborde):
            # Confeccion al hilo
            st.success(f"Generando marcada para corte al hilo en DXF...")
            dxf_bytes = create_dxf_hilo_bytes(width, height, deflection)

            # provide download button for each file
            st.download_button(
                label=f"Descargar marcada {out_name}",
                data=dxf_bytes,
                file_name=out_name,
                mime="application/dxf"
            )
            
        else:
            #codetraves

            # roll_width comes from number_input; make sure it's int
            try:
                n_files = int(roll_width)
            except Exception:
                n_files = 1

            st.success(f"Generando {n_files} marcadas en DXF...")

            # if multiple files, use padded suffixes name_01.dxf ... name_NN.dxf
            pad = 2 if n_files > 1 else 0

            # collect download buttons (multiple possible)
            for i in range(1, n_files + 1):
                if n_files == 1:
                    out_name = f"{file_name}.dxf"
                else:
                    out_name = f"{file_name}_{i:0{pad}d}.dxf"

                # create DXF bytes
                dxf_bytes = create_rectangle_dxf_bytes(width, height, deflection)

                # provide download button for each file
                st.download_button(
                    label=f"Descargar marcada {out_name}",
                    data=dxf_bytes,
                    file_name=out_name,
                    mime="application/dxf"
                )

if __name__ == "__main__":
    main()
