# NODE.47 ESPN DATA — V0.0.9

Service de données multisport pour NODE.47 SPORT ANALYT. Collecte les scoreboards ESPN, normalise les événements, conserve les snapshots courants et expose une API REST ainsi qu'un serveur MCP Streamable HTTP en lecture seule.

> Les endpoints ESPN utilisés sont non officiels et non documentés. Ils peuvent changer sans préavis et ne disposent d'aucun SLA. Respecter les conditions d'utilisation ESPN. Une réponse vide ou une erreur ne doit jamais être convertie en donnée supposée.

## Persistance PostgreSQL / Supabase

Le service conserve SQLite comme backend local par défaut. Lorsqu'une variable `DATABASE_URL` est présente, il utilise automatiquement PostgreSQL via psycopg. Pour Supabase, utiliser la chaîne de connexion PostgreSQL du **pooler transactionnel** (port 6543), avec SSL. Ne jamais utiliser la clé `service_role` comme chaîne de connexion et ne jamais committer de secret.

Le schéma est créé automatiquement au démarrage : `events`, `coverage` et `service_meta`. Le payload événementiel est conservé en JSON texte afin de préserver le contrat REST/MCP existant.

### Migration initiale des données SQLite

Avant de configurer `DATABASE_URL` sur Render, exporter/sauvegarder le fichier SQLite existant. Puis exécuter, depuis un environnement qui peut lire le fichier SQLite et joindre Supabase :

```bash
DATABASE_URL='postgresql://…' PYTHONPATH=src python -m node47_espn.migrate_sqlite --source ./data/node47.sqlite3
```

L'import est idempotent : les événements, couvertures et métadonnées sont insérés ou mis à jour par leurs clés. Il n'efface pas les lignes PostgreSQL absentes du fichier source. Le script affiche uniquement les nombres de lignes, jamais la chaîne de connexion. Vérifier les nombres importés avant le basculement de Render.

Sur Render, ajouter ensuite `DATABASE_URL` comme variable secrète du service. Le service choisira PostgreSQL au prochain déploiement. Conserver le fichier SQLite exporté jusqu'à validation complète de l'API REST et du handshake MCP.

Variables : `DATABASE_URL` (optionnelle ; PostgreSQL si définie), `NODE47_DATA_PATH` (SQLite local si DATABASE_URL absente), `NODE47_API_KEY`, `NODE47_REFRESH_SECONDS=900`, `PORT`.

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

## Persistance et nettoyage des événements obsolètes

Les événements sont upsertés par identifiant ESPN. Après un snapshot complet (sans filtre date), le service supprime les anciens événements uniquement pour les routes dont la collecte a réussi (`ok` ou `empty`). Les routes `unavailable` conservent leurs données précédentes. Les collectes datées sont partielles et ne déclenchent jamais de suppression. Le nombre supprimé est exposé par `/v1/health`.

## Tennis — matchs individuels

Les réponses ATP/WTA regroupent les matchs à l'intérieur de `events[].groupings[].competitions[]`. Le normaliseur développe chaque compétition en événement individuel et conserve l'identifiant du match, l'identifiant du tournoi, le tableau/draw, le tour, l'horaire, le court et les deux joueurs lorsque les champs sont présents. Les tableaux sans deux participants identifiables sont exclus ou signalés ; aucun match n'est inventé. Les réponses tennis déjà structurées en événements individuels restent prises en charge.

Les champs disponibles restent tributaires des réponses ESPN. La surface, les statistiques service/retour et les cotes doivent être enrichies depuis des sources indépendantes avant une analyse NODE.47 complète.

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Les tests d'intégration PostgreSQL sont ignorés par défaut. Pour les exécuter contre une base de test jetable :

```bash
NODE47_TEST_DATABASE_URL='postgresql://…' PYTHONPATH=src python -m unittest tests.test_postgres_store -v
```

## GitHub Pages et API de production

Le workflow `.github/workflows/espn-pages.yml` publie des snapshots JSON et un manifeste de couverture sur GitHub Pages. Cela ne déploie pas l'application FastAPI. L'API REST/MCP nécessite un hébergement distinct (par exemple un service conteneurisé) et une URL de base configurée dans l'environnement du plugin. Ne pas considérer le snapshot Pages comme une API FastAPI ou un serveur MCP.

## Limites

- Pas de cotes, blessures, compositions, rosters complets ou statistiques avancées garanties.
- Les données ESPN ne remplacent pas les sources spécialisées propres aux modèles NODE.47.
- La connexion MCP native au plugin doit être configurée et testée séparément.
- Sans cote actuelle, ligne exacte et règles de règlement vérifiées, le moteur décisionnel doit conclure NO BET.

## Moteur prédictif NBA — V0.1 baseline

Un premier moteur déterministe de projection basketball est disponible via `POST /v1/predictions/basketball`. Il exige des agrégats d'équipe explicitement fournis par l'appelant et renvoie une projection marquée `baseline_uncalibrated`. Il ne récupère pas automatiquement les statistiques, ne constitue pas un modèle entraîné et ne valide aucun avantage de pari. Les métriques de backtest et les exigences de validation sont décrites dans [docs/NBA_PREDICTION_ENGINE.md](docs/NBA_PREDICTION_ENGINE.md).

**Cette version n'est pas encore déployée en production.** Elle doit passer les tests automatisés et une validation chronologique sur des données historiques avant tout usage opérationnel.

## Historique

- V0.0.7 : API HTTP, SQLite, catalogue et couverture.
- V0.0.8 : suppression prudente des événements obsolètes et normalisation des matchs individuels de tennis.
- V0.0.9 : outils MCP Streamable HTTP en lecture seule pour connexion native à NODE.47.
- Branche de migration PostgreSQL : backend psycopg optionnel, importateur SQLite idempotent et tests d'intégration PostgreSQL.
