import os

import requests
import streamlit as st

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(
    page_title="ChangeFlow",
    page_icon="🔄",
    layout="wide",
)

if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# Badge de notificaciones no leídas en el sidebar
if st.session_state.token:
    try:
        resp = requests.get(
            f"{API_URL}/notifications/me",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=5,
        )
        if resp.status_code == 200:
            unread = sum(1 for n in resp.json() if not n["read"])
            if unread > 0:
                st.sidebar.metric("🔔 Notificaciones", unread, help="Notificaciones no leídas")
    except requests.exceptions.ConnectionError:
        pass

st.title("🔄 ChangeFlow")
st.markdown("Plataforma de solicitudes de cambios técnicos.")

if st.session_state.user:
    st.success(f"Bienvenido, **{st.session_state.user['name']}** — Rol: `{st.session_state.user['role']}`")
else:
    st.info("Por favor inicia sesión desde el menú lateral.")