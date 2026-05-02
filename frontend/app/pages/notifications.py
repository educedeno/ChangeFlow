"""Página de notificaciones del usuario autenticado."""

import os

import requests
import streamlit as st

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="Notificaciones — ChangeFlow", page_icon="🔔")
st.title("🔔 Notificaciones")

if not st.session_state.get("token"):
    st.warning("Debes iniciar sesión para ver tus notificaciones.")
    st.stop()

token = st.session_state.token
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(f"{API_URL}/notifications/me", headers=headers, timeout=10)

if response.status_code != 200:
    st.error(f"Error al cargar notificaciones: {response.json().get('detail', response.status_code)}")
    st.stop()

notifications = response.json()

if not notifications:
    st.info("No tienes notificaciones.")
    st.stop()

st.caption(f"{len(notifications)} notificación(es)")

for n in notifications:
    col1, col2 = st.columns([5, 1])
    with col1:
        prefix = "📭" if n["read"] else "📬"
        st.write(f"{prefix} **{n['event_type']}** — {n['message']}")
        st.caption(n["created_at"])
    with col2:
        if not n["read"]:
            if st.button("Marcar leída", key=n["id"]):
                resp = requests.post(
                    f"{API_URL}/notifications/{n['id']}/read",
                    headers=headers,
                    timeout=10,
                )
                if resp.status_code == 204:
                    st.rerun()
                else:
                    st.error("No se pudo marcar como leída.")
    st.divider()
