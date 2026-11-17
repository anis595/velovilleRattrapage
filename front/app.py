"""Page d'accueil Streamlit : connexion.

À compléter : formulaire identifiant / mot de passe, appel de POST /auth/login via
api_client, stockage du jeton et du rôle dans st.session_state,
message d'erreur en français en cas d'échec.

Lancement : streamlit run front/app.py
"""
"""Page de connexion de VéloVille."""

import streamlit as st

from front.api_client import ErreurApi, appeler_api

st.set_page_config(page_title="VéloVille", layout="wide")
st.title("VéloVille — Plateforme de restitution")

if st.session_state.get("token"):
    st.sidebar.write(f"Connecté : {st.session_state['username']}")
    st.sidebar.write(f"Rôle : {st.session_state['role']}")

    if st.sidebar.button("Se déconnecter"):
        for cle in ("token", "role", "username"):
            st.session_state.pop(cle, None)
        st.rerun()

    st.success(
        f"Connecté en tant que {st.session_state['username']} "
        f"(rôle : {st.session_state['role']})."
    )
    st.write("Utilisez le menu latéral pour accéder aux écrans.")

else:
    st.subheader("Connexion")

    with st.form("formulaire_connexion"):
        username = st.text_input("Identifiant")
        password = st.text_input("Mot de passe", type="password")
        envoyer = st.form_submit_button("Se connecter")

    if envoyer:
        try:
            with st.spinner("Chargement..."):
                reponse = appeler_api(
                    "POST",
                    "/auth/login",
                    donnees={
                        "username": username,
                        "password": password,
                    },
                )
        except ErreurApi as erreur:
            st.error(str(erreur))
        else:
            st.session_state["token"] = reponse["access_token"]
            st.session_state["role"] = reponse["role"]
            st.session_state["username"] = username
            st.rerun()