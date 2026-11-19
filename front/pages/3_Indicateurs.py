from datetime import date

import streamlit as st

from front.api_client import ErreurApi, appeler_api

st.title("Indicateurs")

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

colonne_debut, colonne_fin, colonne_limite = st.columns(3)
with colonne_debut:
    date_debut = st.date_input(
        "Période : du", value=date(2026, 8, 24)
    )
with colonne_fin:
    date_fin = st.date_input(
        "Période : au", value=date(2026, 8, 30)
    )
with colonne_limite:
    limite = st.number_input(
        "Nombre de stations", min_value=1, max_value=50, value=10
    )

st.button("Actualiser")

try:
    with st.spinner("Chargement..."):
        activite = appeler_api(
            "GET",
            "/indicateurs/activite-par-jour",
            jeton=jeton,
            params={
                "date_debut": date_debut.isoformat(),
                "date_fin": date_fin.isoformat(),
            },
        )
        stations = appeler_api(
            "GET",
            "/indicateurs/stations-actives",
            jeton=jeton,
            params={"limite": limite},
        )
        incidents = appeler_api(
            "GET",
            "/indicateurs/incidents-par-statut",
            jeton=jeton,
        )
except ErreurApi as erreur:
    st.error(str(erreur))
    st.stop()

nb_trajets = sum(
    ligne["nb_trajets"] for ligne in activite["donnees"]
)
nb_stations = len(stations["donnees"])
delai = incidents["delai_moyen_resolution_heures"]
delai_affiche = "n. d." if delai is None else f"{delai:.1f}".replace(".", ",")

metrique_trajets, metrique_stations, metrique_delai = st.columns(3)
metrique_trajets.metric("Trajets sur la période", nb_trajets)
metrique_stations.metric("Stations actives", nb_stations)
metrique_delai.metric("Délai moyen de résolution (h)", delai_affiche)

st.subheader("Activité par jour")
if activite["donnees"]:
    st.dataframe(
        [
            {
                "Jour": ligne["jour"],
                "Nombre de trajets": ligne["nb_trajets"],
            }
            for ligne in activite["donnees"]
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Aucun résultat pour ces critères.")

st.subheader("Stations les plus actives")
if stations["donnees"]:
    st.dataframe(
        [
            {
                "Identifiant": ligne["station_id"],
                "Nom": ligne["nom"],
                "Départs": ligne["nb_departs"],
                "Arrivées": ligne["nb_arrivees"],
                "Total": ligne["nb_departs"] + ligne["nb_arrivees"],
            }
            for ligne in stations["donnees"]
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Aucun résultat pour ces critères.")

st.subheader("Incidents par statut")
if incidents["donnees"]:
    st.dataframe(
        [
            {
                "Statut": ligne["statut"],
                "Nombre d'incidents": ligne["nb_incidents"],
            }
            for ligne in incidents["donnees"]
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Aucun résultat pour ces critères.")
