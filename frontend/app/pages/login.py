import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Login — ChangeFlow", page_icon="🔐")
st.title("🔐 Iniciar sesión")

if st.session_state.get("token"):
    st.success(f"Ya estás autenticado como **{st.session_state.user['name']}**")
    if st.button("Cerrar sesión"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()
else:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")

    if submitted:
        if not email or not password:
            st.error("Completa todos los campos.")
        else:
            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": email, "password": password},
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.user = {
                        "name": data["name"],
                        "role": data["role"],
                    }
                    st.success(f"Bienvenido, {data['name']}!")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Intenta de nuevo.")
            except requests.exceptions.ConnectionError:
                st.error("No se pudo conectar con el servidor. Verifica que la API esté corriendo.")