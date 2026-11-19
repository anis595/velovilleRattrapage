#!/usr/bin/env bash
# Sauvegarde horodatée de la base PostgreSQL VéloVille.
set -euo pipefail

cd "$(dirname "$0")/.."

# pg_dump lit ces paramètres directement dans l'environnement.
: "${PGHOST:?Définir PGHOST avant de lancer la sauvegarde}"
: "${PGPORT:?Définir PGPORT avant de lancer la sauvegarde}"
: "${PGUSER:?Définir PGUSER avant de lancer la sauvegarde}"
: "${PGDATABASE:?Définir PGDATABASE avant de lancer la sauvegarde}"

mkdir -p sauvegardes
fichier="sauvegardes/veloville_$(date +%Y%m%d_%H%M%S).dump"

if ! pg_dump -Fc -f "$fichier"; then
    rm -f -- "$fichier"
    echo "La sauvegarde a échoué." >&2
    exit 1
fi

echo "Sauvegarde créée : $fichier"
