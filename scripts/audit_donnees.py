import pandas as pd

STATIONS = pd.read_csv("./data/stations.csv")
TRAJETS = pd.read_csv("./data/trajets.csv")
INCIDENTS = pd.read_csv("./data/incidents.csv")


#                  STATIONS
print(STATIONS["capacite"].value_counts(dropna=False))
print(STATIONS["station_id"].value_counts(dropna=False))
print(STATIONS["date_mise_en_service"].to_string())
date_converti = pd.to_datetime(
    STATIONS["date_mise_en_service"], format="%Y-%m-%d", errors="coerce"
)
print("Date absente ou non convertible :", date_converti.isna().sum())
print(STATIONS["commune"].value_counts(dropna=False))
latitude_check = pd.to_numeric(STATIONS["latitude"], errors="coerce")
print("Latitudes absentes ou non convertibles :", latitude_check.isna().sum())
longitude_check = pd.to_numeric(STATIONS["longitude"], errors="coerce")
print("Longitudes absentes ou non convertibles :", longitude_check.isna().sum())
print("Le nombre de noms manquant est :", STATIONS["nom"].isna().sum())
print(STATIONS["nom"].str.len().max())
print(STATIONS["commune"].str.len().max())
print(STATIONS["station_id"].str.fullmatch("S[0-9]{3}", na=False).all())

#                  TRAJETS

print("Le nombre de doublons est :", TRAJETS.duplicated().sum())
print(TRAJETS["trajet_id"].duplicated().sum())
duree_numeric = pd.to_numeric(TRAJETS["duree_secondes"], errors="coerce")
print(
    "Le nombre de durées absentes ou non convertibles est :",
    duree_numeric.isna().sum(),
)
print((duree_numeric <= 0).sum())
print(TRAJETS[(duree_numeric <= 0)])
print(TRAJETS[((duree_numeric % 1) != 0)])
print(TRAJETS["station_depart"].isin(STATIONS["station_id"]).value_counts())
print(TRAJETS["station_arrivee"].isna().sum())

print(
    (
        TRAJETS["station_arrivee"].notna()
        & ~TRAJETS["station_arrivee"].isin(STATIONS["station_id"])
    ).sum()
)

trajet_inconnu = TRAJETS["station_arrivee"].notna() & ~TRAJETS["station_arrivee"].isin(
    STATIONS["station_id"]
)

print(TRAJETS[trajet_inconnu])

horodatage = pd.to_datetime(
    TRAJETS["depart_horodatage"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
)
print(horodatage.isna().sum())

print(TRAJETS[horodatage.isna()])

print(TRAJETS["type_usager"].value_counts(dropna=False))

print(((TRAJETS["type_usager"] == "abonne") & (TRAJETS["usager_ref"].isna())).sum())
print(
    ((TRAJETS["type_usager"] == "occasionnel") & (TRAJETS["usager_ref"].notna())).sum()
)
velos_valides = TRAJETS["velo_id"].str.fullmatch("V[0-9]{4}", na=False)
print(TRAJETS[~velos_valides])

print(TRAJETS["usager_ref"].dropna().str.fullmatch("U[0-9a-fA-F]{8}").value_counts())

#                  INCIDENTS

print(INCIDENTS.duplicated().sum())
print(INCIDENTS["statut"].value_counts(dropna=False))
print(INCIDENTS["cible"].value_counts(dropna=False))

station_incident_invalide = (INCIDENTS["cible"] == "station") & ~(
    INCIDENTS["station_id"].isin(STATIONS["station_id"])
)

print(INCIDENTS[station_incident_invalide])

cibles_valides = (
    (INCIDENTS["cible"] == "velo")
    & INCIDENTS["velo_id"].notna()
    & INCIDENTS["station_id"].isna()
) | (
    (INCIDENTS["cible"] == "station")
    & INCIDENTS["station_id"].notna()
    & INCIDENTS["velo_id"].isna()
)

print("Incidents avec une cible incohérente :", (~cibles_valides).sum())
print(INCIDENTS[~cibles_valides])

signalement = pd.to_datetime(
    INCIDENTS["date_signalement"],
    format="%Y-%m-%d %H:%M",
    errors="coerce",
)

resolution = pd.to_datetime(
    INCIDENTS["date_resolution"],
    format="%Y-%m-%d %H:%M",
    errors="coerce",
)

statuts = INCIDENTS["statut"].str.strip().str.lower().str.replace(" ", "_", regex=False)

resolus = statuts.eq("resolu")
resolution_renseignee = INCIDENTS["date_resolution"].notna()
technicien_absent = INCIDENTS["technicien"].fillna("").str.strip().eq("")

controles = {
    "Signalement absent ou non convertible": signalement.isna(),
    "Résolution renseignée mais non convertible": resolution_renseignee
    & resolution.isna(),
    "Incident résolu sans date de résolution": resolus & ~resolution_renseignee,
    "Incident non résolu avec une date de résolution": ~resolus & resolution_renseignee,
    "Résolution antérieure au signalement": resolution < signalement,
    "Technicien absent après prise en charge — avertissement": statuts.isin(
        ["en_cours", "resolu"]
    )
    & technicien_absent,
}

colonnes = [
    "incident_id",
    "statut",
    "date_signalement",
    "date_resolution",
    "technicien",
]

for libelle, filtre in controles.items():
    print(f"\n{libelle} : {filtre.sum()}")
    if filtre.any():
        print(INCIDENTS.loc[filtre, colonnes].to_string(index=False))
