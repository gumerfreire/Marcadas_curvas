import streamlit as st
import ezdxf
from io import BytesIO

def create_rectangle_dxf(width, height):
    """
    Creates a DXF file in memory containing a rectangle
    drawn using 4 line entities.
    Returns the DXF data as bytes.
    """
    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()

    # Rectangle corners
    p1 = (0, 0)
    p2 = (width, 0)
    p3 = (width, height)
    p4 = (0, height)

    # Draw the 4 lines
    msp.add_line(p1, p2)
    msp.add_line(p2, p3)
    msp.add_line(p3, p4)
    msp.add_line(p4, p1)

    # Save into memory buffer
    buffer = BytesIO()
    doc.write_stream(buffer)  # <-- FIX
    buffer.seek(0)
    return buffer

def main():
    st.title("DXF Generator")

    # --- Explanation Text ---
    st.markdown("### Explanation")
    st.write("explanation")   # <- You will replace this text later
    st.markdown("---")

    # --- Unit Selector ---
    units = st.selectbox(
        "Select Units",
        options=["Inches", "Centimeters"],
        index=0
    )

    # --- File Name Input ---
    file_name = st.text_input("Nombre de archivo")

    st.markdown("---")

    # --- Numeric Inputs ---
    col1, col2 = st.columns(2)

    with col1:
        width = st.number_input("Width", min_value=0.0, step=0.1)
        roll_width = st.number_input("Roll Width", min_value=1, step=1)  # integer

    with col2:
        height = st.number_input("Height", min_value=0.0, step=0.1)
        deflection = st.number_input("Deflection", min_value=0.0, step=0.01, value=10.0)

    st.markdown("---")

    # --- Generate Button ---
    if st.button("Generate DXF"):

        if not file_name:
            st.error("Please enter a file name in 'Nombre de archivo'.")
            return

        st.success("Generating files...")

        # Generate each DXF
        for i in range(1, roll_width + 1):

            # Determine filename
            if roll_width == 1:
                final_name = f"{file_name}.dxf"
            else:
                final_name = f"{file_name}_{i:02d}.dxf"

            dxf_data = create_rectangle_dxf(width, height)

            # Provide a download button
            st.download_button(
                label=f"Download {final_name}",
                data=dxf_data,
                file_name=final_name,
                mime="application/dxf"
            )


if __name__ == "__main__":
    main()
