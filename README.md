# NODE.47 ESPN DATA — V0.0.7

Service de données multisport pour NODE.47 SPORT ANALYT. Il collecte les tableaux de scores ESPN, normalise les événements, les conserve dans SQLite et expose une API HTTP versionnée. GitHub Pages reste disponible pour les snapshots et le manifeste de couverture.

> Important : les endpoints ESPN utilisés sont non officiels et non documentés. Vérifier les conditions d'utilisation ESPN avant toute collecte, republication ou réutilisation. Une réponse vide ou une erreur HTTP n'est jamais transformée en donnée supposée.

## Périmètre
- Sports : football, basketball et tennis.
- Registre ESPN : 237 compétitions répertoriées dans la base V0.0.5.
- Collecte réellement activée dans la configuration de référence : 12 routes (voir config/competitions.json).
- Source primaire : ESPN scoreboard (site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard).
- Batch : GitHub Actions et GitHub Pages.
- Service : FastAPI, SQLite et rafraîchissement périodique (15 minutes par défaut).
- La présence dans le registre ou le statut verified ne signifie pas que la compétition est activement collectée.

## API V0.0.7
Python 3.11+ recommandé.

~~~bash
pip install -r requirements.txt
PYTHONPATH=src NODE47_DATA_PATH=./data/node47.sqlite3 uvicorn node47_espn.api:app --host 0.0.0.0 --port 8000
~~~

La documentation OpenAPI est disponible sur /docs.

| Route | Fonction |
|---|---|
| GET /v1/health | État du service, fraîcheur, nombre d'événements |
| GET /v1/competitions?sport=soccer | Registre avec collection_enabled distinct de verified |
| GET /v1/coverage | Résultat du dernier cycle par route |
| GET /v1/events?sport=basketball&league=nba | Événements filtrables et paginés |
| GET /v1/events/{event_id} | Détail d'un événement |
| POST /v1/refresh | Rafraîchissement manuel protégé par X-API-Key |

Variables de production : NODE47_API_KEY (requise pour le refresh manuel), NODE47_DATA_PATH=/data/node47.sqlite3, NODE47_REFRESH_SECONDS=900, PORT (fourni par l'hébergeur). Monter un volume persistant sur /data.

Les routes de lecture exposent uniquement les données publiques collectées. Les événements et la couverture sont conservés dans SQLite ; les champs absents restent nuls et les anomalies restent signalées.

## Registre et collecte
- verified : endpoint sondé et schéma validé.
- candidate : endpoint identifié mais non sondé.
- unavailable : endpoint sondé et non exploitable.
- ok : route collectée avec événements.
- empty : réponse valide sans événement.
- unavailable dans le manifeste de collecte : échec de la route lors du dernier cycle.

Le registre reste distinct de la collecte active. Le service ne prétend donc pas collecter les 237 compétitions simplement parce qu'elles sont recensées.

## Reconstruire le registre
~~~bash
python3 tools/discover.py
python3 tools/probe_registry.py --dates 20261122,20261125,20261128
python3 tools/build_registry.py
~~~

Les champs category, gender et zone sont dérivés des noms/slugs ESPN et ne sont pas des signaux du moteur décisionnel.

## Tests
~~~bash
PYTHONPATH=src python -m unittest discover -s tests -v
~~~

## GitHub Pages
Dans Settings → Pages → Build and deployment, choisir GitHub Actions. Le workflow publie les snapshots sous site/. Ne jamais publier de secrets.

## Limites connues
- ESPN utilise ici des endpoints non officiels/non documentés, sans SLA.
- Pas de cotes, blessures, rosters complets, compositions ou statistiques avancées en V0.0.7.
- Les routes tennis sont vérifiées au niveau tournoi ; cela ne garantit pas une couverture des matchs.
- Les 12 routes actives ne représentent pas les 237 compétitions du registre.
- L'API REST ne prouve pas, à elle seule, une connexion MCP native au plugin ; cette connexion doit être configurée et testée séparément.

## Roadmap
- V0.0.3 à V0.0.5 : collecte initiale, registre, découverte et sondes.
- V0.0.6 : extension progressive des routes de collecte (à poursuivre).
- V0.0.7 : API HTTP, SQLite, endpoints de consultation, fraîcheur, couverture et authentification du refresh.
- V0.0.8 : connexion MCP native du plugin, extension vérifiée de la couverture et métriques de service.
