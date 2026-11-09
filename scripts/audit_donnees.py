import pandas as pd

STATIONS = pd.read_csv("./data/stations.csv")
TRAJETS = pd.read_csv("./data/trajets.csv")


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
