import streamlit as st

def main():
    st.title("DXF Generator")

    # --- Explanation Text ---
    st.write("explanation")   # <- You will replace this text later

    # Separator line
    st.markdown("---")

    # --- Unit Selector ---
    units = st.selectbox(
        "Select Units",
        options=["Inches", "Centimeters"],
        index=0
    )

    # --- File Name Input (full width) ---
    file_name = st.text_input("Nombre de archivo")

    st.markdown("---")

    # --- Numeric Inputs ---
    col1, col2 = st.columns(2)

    with col1:
        width = st.number_input("Width", min_value=0.0, step=0.1)
        roll_width = st.number_input("Roll Width", min_value=0, step=1)  # integer input

    with col2:
        height = st.number_input("Height", min_value=0.0, step=0.1)
        deflection = st.number_input("Deflection", min_value=0.0, step=0.01, value=10.0)  # default = 10

    st.markdown("---")

    # --- Generate Button ---
    if st.button("Generate DXF"):
        st.success("DXF generation process triggered! (Logic to be added)")

if __name__ == "__main__":
    main()
