"""
Vista de detalle de una solicitud de cambio.

Esta vista la comparten varias personas del equipo. La sección
"Acciones del aprobador" es responsabilidad de Persona 3 (feature de aprobación).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from uuid import UUID

import streamlit as st

from app.api_client import ApiClient

st.set_page_config(page_title="Detalle de solicitud", page_icon="📄")
st.title("📄 Detalle de solicitud")

if "user_id" not in st.session_state:
    st.warning("Debes iniciar sesión.")
    st.stop()

user_id: UUID = st.session_state["user_id"]
client = ApiClient(user_id=user_id)

# ----- Datos de la solicitud (los renderiza el compañero responsable) -----
st.info(
    "Aquí va la información completa de la solicitud "
    "(título, descripción, risk, estado, plan de rollback, historial, etc). "
    "Implementación a cargo de otra persona del equipo."
)

st.divider()

# =============================================================================
# Acciones del aprobador (Persona 3)
# =============================================================================

st.subheader("Acciones del aprobador")

approval_id_str = st.text_input(
    "Approval ID asignada a ti para esta solicitud",
    help="Cuando se conecte el listado real, esto se rellenará automáticamente.",
)

if approval_id_str:
    try:
        approval_id = UUID(approval_id_str)
    except ValueError:
        st.error("Approval ID inválido.")
        st.stop()

    action = st.radio(
        "¿Qué deseas hacer?",
        options=["Aprobar", "Rechazar", "Solicitar cambios"],
        horizontal=True,
    )

    comment = ""
    if action in ("Rechazar", "Solicitar cambios"):
        comment = st.text_area(
            f"Comentario (obligatorio para {action.lower()})",
            key="detail_comment",
        )

    if st.button("Confirmar acción", type="primary"):
        if action == "Aprobar":
            ok, msg, _ = client.approve(approval_id)
        elif action == "Rechazar":
            if not comment.strip():
                st.error("El comentario es obligatorio.")
                st.stop()
            ok, msg, _ = client.reject(approval_id, comment)
        else:
            if not comment.strip():
                st.error("El comentario es obligatorio.")
                st.stop()
            st.info("TODO: endpoint dedicado para solicitar cambios.")
            st.stop()

        if ok:
            st.success(msg)
        else:
            st.error(msg)