"""
Vista del aprobador: muestra las solicitudes pendientes asignadas a él
y permite aprobar, rechazar o solicitar cambios.

Esta vista asume que el usuario ya tiene `user_id` en st.session_state,
lo cual lo manejará la página de login (otra persona del equipo).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from uuid import UUID

import streamlit as st

from app.api_client import ApiClient

st.set_page_config(page_title="Approver Inbox", page_icon="📥")
st.title("📥 Bandeja del aprobador")

# ---------------------------------------------------------------------------
# Verificación de sesión
# ---------------------------------------------------------------------------

if "user_id" not in st.session_state:
    st.warning("Debes iniciar sesión para ver tu bandeja.")
    # Permitir poner un user_id manualmente para testear sin login
    test_user = st.text_input("UUID de prueba (mientras no haya login)")
    if test_user:
        try:
            st.session_state["user_id"] = UUID(test_user)
            st.rerun()
        except ValueError:
            st.error("UUID inválido.")
    st.stop()

user_id: UUID = st.session_state["user_id"]
client = ApiClient(user_id=user_id)

# ---------------------------------------------------------------------------
# Listado de solicitudes pendientes
# ---------------------------------------------------------------------------

st.subheader("Aprobar / Rechazar / Solicitar cambios")
st.caption(
    "Ingresa el ID de una Approval asignada a ti para tomar una decisión."
)

approval_id_str = st.text_input("Approval ID", key="approval_id_input")

if approval_id_str:
    try:
        approval_id = UUID(approval_id_str)
    except ValueError:
        st.error("El Approval ID no es un UUID válido.")
        st.stop()

    col1, col2, col3 = st.columns(3)

    # ----- Aprobar -----
    with col1:
        if st.button("✅ Aprobar", use_container_width=True):
            ok, msg, _ = client.approve(approval_id)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    # ----- Rechazar -----
    with col2:
        with st.expander("❌ Rechazar"):
            reject_comment = st.text_area(
                "Motivo del rechazo (obligatorio)", key="reject_comment"
            )
            if st.button("Confirmar rechazo", key="confirm_reject"):
                if not reject_comment.strip():
                    st.error("El comentario es obligatorio para rechazar.")
                else:
                    ok, msg, _ = client.reject(approval_id, reject_comment)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

    # ----- Solicitar cambios -----
    with col3:
        with st.expander("🔁 Solicitar cambios"):
            change_comment = st.text_area(
                "Qué cambios solicitas (obligatorio)", key="change_comment"
            )
            if st.button("Enviar solicitud", key="confirm_changes"):
                if not change_comment.strip():
                    st.error("Debes describir los cambios solicitados.")
                else:
                    # Reusamos reject endpoint con un comentario marcado, o
                    # idealmente un endpoint específico request_changes.
                    st.info(
                        "TODO: endpoint /request-changes pendiente. "
                        "Mientras tanto, usa Rechazar con comentario."
                    )

st.divider()
st.caption(f"Sesión: user_id = {user_id}")