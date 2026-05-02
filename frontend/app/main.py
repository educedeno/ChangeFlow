import streamlit as st

st.set_page_config(
    page_title="ChangeFlow",
    page_icon="🔄",
    layout="wide",
)

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

st.title("🔄 ChangeFlow")
st.markdown("Plataforma de solicitudes de cambios técnicos.")

if st.session_state.user:
    st.success(f"Bienvenido, **{st.session_state.user['name']}** — Rol: `{st.session_state.user['role']}`")
else:
    st.info("Por favor inicia sesión desde el menú lateral.")