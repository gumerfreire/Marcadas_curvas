import streamlit as st

def main():
    st.title("Generador de marcadas curvas")

    # --- Explanation Text ---
    st.markdown("### Introduce los datos a continuación para generar los DXF para máquina de corte.")
    st.write("explanation")   # <- You will replace this text later

    # Separator line
    st.markdown("---")

    # --- Unit Selector ---
    units = st.selectbox(
        "Unidades",
        options=["Inch", "cm"],
        index=0
    )

    st.markdown("---")

    # --- Numeric Inputs ---
    col1, col2 = st.columns(2)

    with col1:
        width = st.number_input("Ancho tela (OF)", min_value=0.0, step=0.1)
        roll_width = st.number_input("Ancho de rollo", min_value=0, step=1)  # integer input

    with col2:
        height = st.number_input("Alto tela (OF)", min_value=0.0, step=0.1)
        deflection = st.number_input("Flecha tubo", min_value=0.0, step=0.01, value=10.0)  # default = 10

    st.markdown("---")

    # --- Generate Button ---
    if st.button("Generar DXF"):
        st.success("DXF generation process triggered! (Logic to be added)")

if __name__ == "__main__":
    main()