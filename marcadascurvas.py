import streamlit as st
import ezdxf
from io import BytesIO, StringIO

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


def main():
    st.title("DXF Generator")

    # Explanation
    st.markdown("### Explanation")
    st.write("explanation")  # you will replace this text later
    st.markdown("---")

    # Unit selector
    units = st.selectbox("Select Units", options=["Inches", "Centimeters"], index=0)

    # File name (full width)
    file_name = st.text_input("Nombre de archivo")

    st.markdown("---")

    # Numeric inputs
    col1, col2 = st.columns(2)

    with col1:
        width = st.number_input("Width", min_value=0.0, step=0.1, format="%.3f")
        # roll_width is an integer (no decimals)
        roll_width = st.number_input("Roll Width", min_value=1, step=1, value=1, format="%d")

    with col2:
        height = st.number_input("Height", min_value=0.0, step=0.1, format="%.3f")
        deflection = st.number_input("Deflection", min_value=0.0, step=0.01, value=10.0, format="%.3f")

    st.markdown("---")

    if st.button("Generate DXF"):
        # basic validation
        if not file_name:
            st.error("Please enter a file name in 'Nombre de archivo'.")
            st.stop()

        if width <= 0 or height <= 0:
            st.error("Width and Height must be greater than zero.")
            st.stop()

        # roll_width comes from number_input; make sure it's int
        try:
            n_files = int(roll_width)
        except Exception:
            n_files = 1

        st.success(f"Generating {n_files} DXF file(s)...")

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
                label=f"Download {out_name}",
                data=dxf_bytes,
                file_name=out_name,
                mime="application/dxf"
            )

if __name__ == "__main__":
    main()
