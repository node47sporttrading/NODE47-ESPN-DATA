# NODE.47 ESPN DATA — V0.0.9

Service de données multisport pour NODE.47 SPORT ANALYT. Collecte les scoreboards ESPN, normalise les événements, conserve les snapshots courants dans SQLite et expose une API REST ainsi qu'un serveur MCP Streamable HTTP en lecture seule.

> Les endpoints ESPN utilisés sont non officiels et non documentés. Ils peuvent changer sans préavis et ne disposent d'aucun SLA. Respecter les conditions d'utilisation ESPN. Une réponse vide ou une erreur ne doit jamais être convertie en donnée supposée.

## Périmètre et couverture
- Sports : football, basketball et tennis.
- Registre : 237 compétitions (220 football, 15 basketball, 2 tennis).
- Les routes activées sont des routes configurées, pas une garantie d'événements disponibles à chaque collecte.
- Statuts de collecte : `ok` (événements reçus), `empty` (réponse valide sans événement), `unavailable` (échec de la route).
- ESPN scoreboard est la source primaire des calendriers, participants, statuts et scores effectivement présents.

## API REST V0.0.9
Python 3.11+ recommandé.

```bash
pip install -r requirements.txt
PYTHONPATH=src NODE47_DATA_PATH=./data/node47.sqlite3 uvicorn node47_espn.api:app --host 0.0.0.0 --port 8000
```

OpenAPI : `/docs`.

| Route | Fonction |
|---|---|
| GET /v1/health | État, fraîcheur, événements conservés et nombre de suppressions obsolètes |
| GET /v1/competitions?sport=soccer | Registre et activation |
| GET /v1/coverage | Résultat du dernier cycle par route |
| GET /v1/events?sport=basketball&league=nba | Événements filtrables et paginés |
| GET /v1/events/{event_id} | Détail d'un événement |
| POST /v1/refresh | Rafraîchissement manuel protégé par X-API-Key |

## Connexion MCP NODE.47

Le serveur expose un endpoint MCP Streamable HTTP à :

`https://node47-espn-data.onrender.com/mcp/`

Outils MCP en lecture seule :
- `espn_health` : statut du service, dernière collecte, âge des données et nombre d'événements.
- `espn_competitions` : registre des compétitions et activation des routes.
- `espn_coverage` : statut du dernier cycle par compétition.
- `espn_events` : recherche paginée par sport, ligue, statut et période UTC.
- `espn_event_detail` : détail d'un événement par identifiant exact.

Le rafraîchissement manuel n'est volontairement pas exposé en MCP. Il reste protégé par `X-API-Key` sur l'API REST. Aucune clé n'est embarquée dans le plugin NODE.47. Le serveur MCP n'expose que des données de calendrier, d'identité, de statut et de scoreboard ; pas de cotes, blessures, compositions ou prédictions.

La connexion plugin doit pointer vers l'URL MCP ci-dessus (et non vers la racine REST ou GitHub Pages). Après déploiement Render, vérifier le handshake MCP et la présence des cinq outils avant de déclarer l'intégration opérationnelle.

Variables : `NODE47_API_KEY`, `NODE47_DATA_PATH=/data/node47.sqlite3`, `NODE47_REFRESH_SECONDS=900`, `PORT`. Monter un volume persistant sur `/data`.

## Persistance et nettoyage des événements obsolètes
Les événements sont upsertés par identifiant ESPN. Après un snapshot complet (sans filtre date), le service supprime les anciens événements uniquement pour les routes dont la collecte a réussi (`ok` ou `empty`). Les routes `unavailable` conservent leurs données précédentes. Les collectes datées sont partielles et ne déclenchent jamais de suppression. Le nombre supprimé est exposé par `/v1/health`.

## Tennis — matchs individuels
Les réponses ATP/WTA regroupent les matchs à l'intérieur de `events[].groupings[].competitions[]`. Le normaliseur développe chaque compétition en événement individuel et conserve l'identifiant du match, l'identifiant du tournoi, le tableau/draw, le tour, l'horaire, le court et les deux joueurs lorsque les champs sont présents. Les tableaux sans deux participants identifiables sont exclus ou signalés ; aucun match n'est inventé. Les réponses tennis déjà structurées en événements individuels restent prises en charge.

Les champs disponibles restent tributaires des réponses ESPN. La surface, les statistiques service/retour et les cotes doivent être enrichies depuis des sources indépendantes avant une analyse NODE.47 complète.

## Tests
```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## GitHub Pages et API de production
Le workflow `.github/workflows/espn-pages.yml` publie des snapshots JSON et un manifeste de couverture sur GitHub Pages. Cela ne déploie pas l'application FastAPI. L'API REST/MCP nécessite un hébergement distinct (par exemple un service conteneurisé) et une URL de base configurée dans l'environnement du plugin. Ne pas considérer le snapshot Pages comme une API FastAPI ou un serveur MCP.

## Limites
- Pas de cotes, blessures, compositions, rosters complets ou statistiques avancées garanties.
- Les données ESPN ne remplacent pas les sources spécialisées propres aux modèles NODE.47.
- La connexion MCP native au plugin doit être configurée et testée séparément.
- Sans cote actuelle, ligne exacte et règles de règlement vérifiées, le moteur décisionnel doit conclure NO BET.

## Historique
- V0.0.7 : API HTTP, SQLite, catalogue et couverture.
- V0.0.8 : suppression prudente des événements obsolètes et normalisation des matchs individuels de tennis.
- V0.0.9 : outils MCP Streamable HTTP en lecture seule pour connexion native à NODE.47.
