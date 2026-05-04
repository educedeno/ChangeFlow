"""Bandeja del aprobador: aprobar / rechazar / solicitar cambios."""

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

st.caption(
    "Pega el ID de una Approval asignada a ti. La API valida que tu rol "
    "cubra el área (TECH/OPS/SECURITY) antes de aceptar la decisión."
)

approval_id_str = st.text_input("Approval ID", key="approval_id_input")

if approval_id_str:
    try:
        approval_id = UUID(approval_id_str)
    except ValueError:
        st.error("UUID inválido.")
        st.stop()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Aprobar", use_container_width=True):
            ok, msg, _ = client.approve(approval_id)
            (st.success if ok else st.error)(msg)

    with col2:
        with st.expander("❌ Rechazar"):
            reject_comment = st.text_area("Motivo del rechazo", key="reject_comment")
            if st.button("Confirmar rechazo", key="confirm_reject"):
                if not reject_comment.strip():
                    st.error("El comentario es obligatorio.")
                else:
                    ok, msg, _ = client.reject(approval_id, reject_comment)
                    (st.success if ok else st.error)(msg)

    with col3:
        with st.expander("🔁 Solicitar cambios"):
            change_comment = st.text_area("Qué cambios solicitas", key="change_comment")
            if st.button("Enviar solicitud", key="confirm_changes"):
                if not change_comment.strip():
                    st.error("El comentario es obligatorio.")
                else:
                    ok, msg, _ = client.request_changes(approval_id, change_comment)
                    (st.success if ok else st.error)(msg)

st.divider()
st.caption(f"Sesión: user_id = {st.session_state.user_id}")
