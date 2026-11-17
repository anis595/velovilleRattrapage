"""Écran Incidents.

À compléter : tableau filtrable par statut ; pour le rôle exploitant, changement de
statut d'un incident via l'API.
"""
"""Liste des incidents et modification de leur statut."""

import math

import streamlit as st

from front.api_client import ErreurApi, appeler_api

st.title("Incidents")

jeton = st.session_state.get("token")
if not jeton:
    st.info("Veuillez vous connecter.")
    st.page_link("app.py", label="Page de connexion")
    st.stop()

st.sidebar.write(f"Connecté : {st.session_state['username']}")
st.sidebar.write(f"Rôle : {st.session_state['role']}")
if st.sidebar.button("Se déconnecter"):
    for cle in ("token", "role", "username"):
        st.session_state.pop(cle, None)
    st.switch_page("app.py")

message = st.session_state.pop("incident_message", None)
if message:
    st.success(message)

colonne_statut, colonne_taille, colonne_page = st.columns(3)
with colonne_statut:
    statut = st.selectbox(
        "Statut", ["Tous", "ouvert", "en_cours", "resolu"]
    )
with colonne_taille:
    taille_page = st.selectbox("Taille de page", [10, 20, 50], index=1)
with colonne_page:
    page = st.number_input("Page", min_value=1, value=1, step=1)

params = {"page": page, "taille_page": taille_page}
if statut != "Tous":
    params["statut"] = statut

try:
    with st.spinner("Chargement..."):
        reponse = appeler_api(
            "GET", "/incidents", jeton=jeton, params=params
        )
except ErreurApi as erreur:
    st.error(str(erreur))
    st.stop()

total = reponse["total"]
nombre_pages = max(1, math.ceil(total / taille_page))
st.write(f"{total} incidents au total")

if not reponse["resultats"]:
    st.info("Aucun résultat pour ces critères.")
else:
    tableau = [
        {
            "Identifiant": incident["incident_id"],
            "Signalé le": incident["date_signalement"],
            "Cible": incident["cible"],
            "Vélo": incident["velo_id"] or "",
            "Station": incident["station_id"] or "",
            "Type": incident["type_incident"],
            "Statut": incident["statut"],
            "Résolu le": incident["date_resolution"] or "",
            "Technicien": incident["technicien"] or "",
        }
        for incident in reponse["resultats"]
    ]
    st.dataframe(tableau, use_container_width=True, hide_index=True)

st.caption(f"Page {page} sur {nombre_pages}")

st.subheader("Changer le statut d'un incident")

if st.session_state["role"] != "exploitant":
    st.info(
        "La modification des incidents est réservée aux exploitants."
    )
elif reponse["resultats"]:
    identifiants = [
        incident["incident_id"] for incident in reponse["resultats"]
    ]

    with st.form("modifier_incident"):
        incident_id = st.selectbox("Incident", identifiants)
        nouveau_statut = st.selectbox(
            "Nouveau statut", ["en_cours", "resolu"]
        )
        appliquer = st.form_submit_button("Appliquer")

    if appliquer:
        try:
            with st.spinner("Chargement..."):
                appeler_api(
                    "PUT",
                    f"/incidents/{incident_id}/statut",
                    jeton=jeton,
                    donnees={"statut": nouveau_statut},
                )
        except ErreurApi as erreur:
            st.error(str(erreur))
        else:
            st.session_state["incident_message"] = (
                f"Statut de l'incident {incident_id} mis à jour : "
                f"{nouveau_statut}."
            )
            st.rerun()
