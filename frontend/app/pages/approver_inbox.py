"""Bandeja del aprobador: lista de approvals pendientes con acciones."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from uuid import UUID

import streamlit as st

from app.api_client import ApiClient

st.set_page_config(page_title="Approver Inbox", page_icon="📥")
st.title("📥 Bandeja del aprobador")

if not st.session_state.get("token"):
    st.warning("Debes iniciar sesión.")
    st.stop()
if "user_id" not in st.session_state:
    st.warning("Falta user_id en sesión.")
    st.stop()

client = ApiClient(user_id=st.session_state.user_id, token=st.session_state.get("token"))

ok, msg, items = client.my_pending_approvals()
if not ok:
    st.error(msg)
    st.stop()

if not items:
    st.info("No tienes approvals pendientes.")
    st.stop()

st.caption(f"{len(items)} approval(es) pendiente(s)")

for ap in items:
    aid = ap["approval_id"]
    with st.container(border=True):
        st.subheader(f"{ap.get('request_title') or '(sin título)'}")
        st.caption(
            f"Área: **{ap['area']}**  ·  Riesgo: {ap.get('risk_level')}  ·  "
            f"Estado solicitud: `{ap.get('request_status')}`"
        )
        st.caption(f"Approval ID: `{aid}`  ·  Request ID: `{ap['request_id']}`")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✅ Aprobar", key=f"approve-{aid}", use_container_width=True):
                ok, msg, _ = client.approve(UUID(aid))
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()

        with col2:
            with st.popover("❌ Rechazar", use_container_width=True):
                rc = st.text_area("Motivo del rechazo", key=f"reject-comment-{aid}")
                if st.button("Confirmar rechazo", key=f"reject-confirm-{aid}"):
                    if not rc.strip():
                        st.error("El comentario es obligatorio.")
                    else:
                        ok, msg, _ = client.reject(UUID(aid), rc)
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()

        with col3:
            with st.popover("🔁 Solicitar cambios", use_container_width=True):
                cc = st.text_area("Qué cambios pides", key=f"changes-comment-{aid}")
                if st.button("Confirmar", key=f"changes-confirm-{aid}"):
                    if not cc.strip():
                        st.error("El comentario es obligatorio.")
                    else:
                        ok, msg, _ = client.request_changes(UUID(aid), cc)
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()
