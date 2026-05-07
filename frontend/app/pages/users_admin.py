import os

import streamlit as st
import requests

API_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="Administración de usuarios — ChangeFlow", page_icon="👥")
st.title("👥 Administración de usuarios")

# --- Guard: solo Admin ---
if not st.session_state.get("token"):
    st.warning("Debes iniciar sesión para acceder a esta página.")
    st.stop()

if st.session_state.user.get("role") != "ADMIN":
    st.error("No tienes permisos para acceder a esta sección.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}


# --- Listar usuarios ---
st.subheader("Usuarios registrados")

response = requests.get(f"{API_URL}/users/", headers=headers)

if response.status_code == 200:
    users = response.json()
    if users:
        st.table([
            {
                "Nombre": u["name"],
                "Email": u["email"],
                "Rol": u["role"],
                "Activo": "✅" if u["is_active"] else "❌",
            }
            for u in users
        ])
    else:
        st.info("No hay usuarios registrados.")
else:
    st.error("Error al cargar usuarios.")


# --- Crear usuario ---
st.divider()
st.subheader("Crear nuevo usuario")

with st.form("create_user_form"):
    name = st.text_input("Nombre")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    role = st.selectbox("Rol", ["ENGINEER", "TECH_LEAD", "OPS_REVIEWER", "SECURITY_REVIEWER", "ADMIN"])
    submitted = st.form_submit_button("Crear usuario")

if submitted:
    if not name or not email or not password:
        st.error("Completa todos los campos.")
    else:
        res = requests.post(
            f"{API_URL}/users/",
            json={"name": name, "email": email, "password": password, "role": role},
            headers=headers,
        )
        if res.status_code == 201:
            st.success(f"Usuario {name} creado correctamente.")
            st.rerun()
        elif res.status_code == 400:
            st.error(res.json().get("detail", "Error al crear usuario."))
        else:
            st.error("Error inesperado.")


# --- Asignar rol ---
st.divider()
st.subheader("Cambiar rol de usuario")

with st.form("assign_role_form"):
    user_id = st.text_input("ID del usuario")
    new_role = st.selectbox("Nuevo rol", ["ENGINEER", "TECH_LEAD", "OPS_REVIEWER", "SECURITY_REVIEWER", "ADMIN"])
    submitted_role = st.form_submit_button("Asignar rol")

if submitted_role:
    if not user_id:
        st.error("Ingresa el ID del usuario.")
    else:
        res = requests.put(
            f"{API_URL}/users/{user_id}/role",
            json={"role": new_role},
            headers=headers,
        )
        if res.status_code == 200:
            st.success("Rol actualizado correctamente.")
            st.rerun()
        elif res.status_code == 404:
            st.error("Usuario no encontrado.")
        else:
            st.error("Error inesperado.")