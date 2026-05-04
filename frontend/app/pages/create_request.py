"""Crear una solicitud de cambio nueva (Engineer / Tech Lead / Admin)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from uuid import UUID

import streamlit as st

from app.api_client import ApiClient

st.set_page_config(page_title="Crear solicitud", page_icon="📝")
st.title("📝 Crear solicitud de cambio")

if not st.session_state.get("token"):
    st.warning("Debes iniciar sesión.")
    st.stop()

if "user_id" not in st.session_state:
    st.warning("Falta user_id en sesión. Vuelve a iniciar sesión.")
    st.stop()

client = ApiClient(user_id=st.session_state.user_id, token=st.session_state.get("token"))

with st.form("create_request_form"):
    title = st.text_input("Título")
    description = st.text_area("Descripción")
    affected_system = st.text_input("Sistema afectado")
    risk_level = st.selectbox("Nivel de riesgo", ["LOW", "MEDIUM", "HIGH"])
    rollback_plan = st.text_area(
        "Plan de rollback (obligatorio para MEDIUM y HIGH)",
        placeholder="Describe cómo revertir el cambio si algo sale mal.",
    )
    submitted = st.form_submit_button("Crear como DRAFT")

if submitted:
    if not (title and description and affected_system):
        st.error("Completa título, descripción y sistema afectado.")
    elif risk_level in ("MEDIUM", "HIGH") and not rollback_plan.strip():
        st.error(f"Riesgo {risk_level} requiere plan de rollback.")
    else:
        ok, msg, data = client.create_request({
            "title": title,
            "description": description,
            "affected_system": affected_system,
            "risk_level": risk_level,
            "requester_id": str(st.session_state.user_id),
            "rollback_plan": rollback_plan or None,
        })
        if ok and isinstance(data, dict):
            st.success(f"Solicitud creada. ID: {data.get('id')}")
            st.json(data)
        else:
            st.error(msg)
