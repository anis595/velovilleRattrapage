"""Écran Stations.

À compléter : tableau des stations filtrable par commune, pagination.
"""
"""Liste filtrable et paginée des stations."""

import math

import streamlit as st

from front.api_client import ErreurApi, appeler_api

st.title("Stations")

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


@st.cache_data(ttl=3600)
def charger_communes(jeton):
    """Lit les communes des stations et les garde en cache une heure."""
    communes = set()
    page = 1

    while True:
        reponse = appeler_api(
            "GET",
            "/stations",
            jeton=jeton,
            params={"page": page, "taille_page": 100},
        )
        communes.update(
            station["commune"] for station in reponse["resultats"]
        )
        if page * 100 >= reponse["total"]:
            break
        page += 1

    return sorted(communes)


try:
    with st.spinner("Chargement..."):
        communes = charger_communes(jeton)
except ErreurApi as erreur:
    st.error(str(erreur))
    st.stop()

colonne_commune, colonne_taille, colonne_page = st.columns(3)
with colonne_commune:
    commune = st.selectbox("Commune", ["Toutes", *communes])
with colonne_taille:
    taille_page = st.selectbox("Taille de page", [10, 20, 50], index=1)
with colonne_page:
    page = st.number_input("Page", min_value=1, value=1, step=1)

params = {"page": page, "taille_page": taille_page}
if commune != "Toutes":
    params["commune"] = commune

try:
    with st.spinner("Chargement..."):
        reponse = appeler_api(
            "GET", "/stations", jeton=jeton, params=params
        )
except ErreurApi as erreur:
    st.error(str(erreur))
    st.stop()

total = reponse["total"]
nombre_pages = max(1, math.ceil(total / taille_page))
st.write(f"{total} stations au total")

if not reponse["resultats"]:
    st.info("Aucun résultat pour ces critères.")
else:
    tableau = [
        {
            "Identifiant": station["station_id"],
            "Nom": station["nom"],
            "Commune": station["commune"],
            "Capacité": station["capacite"],
            "Mise en service": station["date_mise_en_service"] or "",
        }
        for station in reponse["resultats"]
    ]
    st.dataframe(tableau, use_container_width=True, hide_index=True)

st.caption(f"Page {page} sur {nombre_pages}")
