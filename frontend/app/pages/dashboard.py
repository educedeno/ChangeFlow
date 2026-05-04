"""Listado completo de solicitudes con sus acciones disponibles."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from datetime import datetime, timedelta
from uuid import UUID

import streamlit as st

from app.api_client import ApiClient

st.set_page_config(page_title="Dashboard — ChangeFlow", page_icon="📊", layout="wide")
st.title("📊 Solicitudes de cambio")

if not st.session_state.get("token"):
    st.warning("Debes iniciar sesión.")
    st.stop()
if "user_id" not in st.session_state:
    st.warning("Falta user_id en sesión.")
    st.stop()

client = ApiClient(user_id=st.session_state.user_id, token=st.session_state.get("token"))

ok, msg, items = client.list_requests()
if not ok:
    st.error(msg)
    st.stop()

if not items:
    st.info("No hay solicitudes todavía.")
    st.stop()

for cr in items:
    with st.container(border=True):
        st.subheader(f"{cr['title']}  —  `{cr['status']}`  ·  riesgo {cr['risk_level']}")
        st.write(cr["description"])
        st.caption(f"ID: {cr['id']}  ·  Sistema: {cr['affected_system']}  ·  Solicitante: {cr['requester_id']}")
        if cr.get("rollback_plan"):
            with st.expander("Plan de rollback"):
                st.write(cr["rollback_plan"])
        if cr.get("scheduled_at"):
            st.caption(f"📅 Agendado: {cr['scheduled_at']}")
        if cr.get("executed_at"):
            st.caption(f"✅ Ejecutado: {cr['executed_at']}")
        if cr.get("failure_reason"):
            st.error(f"Falla: {cr['failure_reason']}")

        cols = st.columns(6)
        rid = cr["id"]
        status = cr["status"]
        is_owner = str(st.session_state.user_id) == str(cr["requester_id"])
        is_admin = (st.session_state.get("user") or {}).get("role") == "ADMIN"

        if status in ("DRAFT", "CHANGES_REQUESTED") and is_owner:
            if cols[0].button("Enviar", key=f"submit-{rid}"):
                ok, msg, _ = client.submit(UUID(rid))
                (st.success if ok else st.error)(msg)
                st.rerun()
        if status in ("DRAFT", "SUBMITTED", "TECH_REVIEW", "OPS_REVIEW", "SECURITY_REVIEW", "CHANGES_REQUESTED") and (is_owner or is_admin):
            if cols[1].button("Cancelar", key=f"cancel-{rid}"):
                ok, msg, _ = client.cancel(UUID(rid))
                (st.success if ok else st.error)(msg)
                st.rerun()
        if status == "APPROVED":
            if cols[2].button("Agendar +1h", key=f"sched-{rid}"):
                ok, msg, _ = client.schedule(UUID(rid), datetime.utcnow() + timedelta(hours=1))
                (st.success if ok else st.error)(msg)
                st.rerun()
        if status == "SCHEDULED":
            if cols[3].button("Marcar ejecutado", key=f"exec-{rid}"):
                ok, msg, _ = client.execute(UUID(rid))
                (st.success if ok else st.error)(msg)
                st.rerun()
            with cols[4]:
                with st.popover("Marcar fallido"):
                    reason = st.text_area("Motivo del fallo", key=f"reason-{rid}")
                    if st.button("Confirmar fallo", key=f"fail-confirm-{rid}"):
                        ok, msg, _ = client.fail(UUID(rid), reason)
                        (st.success if ok else st.error)(msg)
                        st.rerun()
