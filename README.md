# NODE.47 ESPN DATA — V0.0.25

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
- Snapshot initial du registre : 237 compétitions (220 soccer, 15 basketball, 2 tennis) ; le catalogue est évolutif.
- Les routes activées sont des routes configurées, pas une garantie d'événements disponibles à chaque collecte.
- Statuts de collecte : `ok` (événements reçus), `empty` (réponse valide sans événement), `unavailable` (échec de la route).
- ESPN scoreboard est la source primaire des calendriers, participants, statuts et scores effectivement présents.

## Registre ESPN complet — football, basketball et tennis

Le catalogue `config/registry.json` est construit à partir de l’énumération ESPN Core `sports.core.api.espn.com/v2/sports/{sport}/leagues` pour les trois sports NODE.47 : `soccer` (football), `basketball` et `tennis`. Le snapshot actuellement commité recense **237 identifiants ESPN** : 220 soccer, 15 basketball et 2 tennis. Ce nombre décrit l'état du catalogue au moment de la découverte ; il ne constitue pas une limite codée en dur.

`tools/discover.py` réénumère les ligues ESPN Core. `tools/probe_registry.py` vérifie chaque route contre le scoreboard ESPN Site API. Une ligue découverte n'est pas automatiquement exploitable : le statut `verified` exige une réponse JSON valide contenant un champ `events` de type liste. Les ligues non vérifiées restent visibles dans le registre mais ne sont pas activées comme nouvelles routes de collecte.

Les routes déjà activées sont conservées dans la configuration pendant un échec temporaire de probe. La couverture réelle reste distincte du recensement et est exposée par `espn_coverage` (`ok`, `empty`, `unavailable`). Le workflow hebdomadaire de synchronisation ouvre une Pull Request pour revue ; il ne pousse pas directement les changements sur `main`.

## API REST V0.0.14
Python 3.11+ recommandé.

```bash
pip install -r requirements.txt
PYTHONPATH=src NODE47_DATA_PATH=./data/node47.sqlite3 uvicorn node47_espn.api:app --host 0.0.0.0 --port 8000
```

OpenAPI : `/docs`.

| Route | Fonction |
|---|---|
| GET /v1/health | État, fraîcheur, événements conservés et nombre de suppressions obsolètes |
| GET /v1/competitions?sport=soccer&status=verified&collection_enabled=true | Registre complet, filtres sport/statut/catégorie/genre/zone/activation |
| GET /v1/coverage | Résultat du dernier cycle par route |
| GET /v1/events?sport=basketball&league=nba | Événements filtrables et paginés |
| GET /v1/events/{event_id} | Détail d'un événement |
| POST /v1/refresh | Rafraîchissement manuel protégé par X-API-Key |

## Connexion MCP NODE.47

Le serveur expose un endpoint MCP Streamable HTTP à :

`https://node47-espn-data.onrender.com/mcp/`

Outils MCP en lecture seule :
- `espn_health` : statut du service, dernière collecte, âge des données et nombre d'événements.
- `espn_competitions` : recensement ESPN complet (soccer, basketball, tennis), filtrable par sport, statut, catégorie, genre, zone et activation du collecteur.
- `espn_coverage` : statut du dernier cycle par compétition.
- `espn_events` : recherche paginée par sport, ligue, statut et période UTC.
- `espn_event_detail` : détail d'un événement par identifiant exact.
- `searxng_health` : vérifie la configuration requise et exécute une recherche témoin via le workflow GitHub Actions, jusqu'au callback authentifié vers Render.
- `searxng_search` : déclenche une recherche web à la demande dans un conteneur SearXNG éphémère sur un runner GitHub Actions. Par défaut, le runner tente aussi de récupérer et d'extraire le contenu des six premières pages publiques (avec validation des redirections et blocage des IP privées/locales). Les champs `page_content`, `page_title`, `page_published_date` et `fetch_status` distinguent le contenu effectivement lu du simple extrait de recherche. Les pages inaccessibles restent explicitement signalées ; les contenus récupérés sont des preuves non fiables à dater, croiser et auditer.

Le rafraîchissement manuel n'est volontairement pas exposé en MCP. Il reste protégé par `X-API-Key` sur l'API REST. Aucune clé n'est embarquée dans le plugin NODE.47. Le serveur MCP expose les outils ESPN en lecture seule, les outils SearXNG `searxng_health` / `searxng_search`, et les outils PropLine de consultation des marchés et cotes bruts. PropLine ne produit pas les prédictions NODE.47 ; les endpoints payants (historique/closing/+EV) ne sont pas activés dans cette intégration Free.

### Recherche web SearXNG à la demande

Le chemin de production ne dépend plus d'un service SearXNG permanent sur Render. Render déclenche `.github/workflows/searxng-search.yml`; le runner GitHub démarre une image SearXNG épinglée, effectue la recherche et transmet uniquement les résultats normalisés (ou une erreur bornée) au callback HTTPS authentifié de Render. Le conteneur est supprimé à la fin du workflow.

Configurer sur le service API Render : `GITHUB_ACTIONS_TOKEN` (jeton limité au dépôt avec `Actions: Read and write`), `NODE47_RENDER_CALLBACK_URL`, `SEARXNG_CALLBACK_SECRET` et, facultativement, `SEARXNG_ACTION_TIMEOUT`. Dans les secrets GitHub Actions du dépôt, configurer `NODE47_RENDER_CALLBACK_SECRET` avec exactement la même valeur que `SEARXNG_CALLBACK_SECRET`. Ne jamais exposer ces valeurs dans Git ou dans le plugin.

Les recherches en attente sont conservées en mémoire dans le processus API : garder une seule instance Render tant qu'un stockage partagé ou une file de tâches n'est pas implémenté. L'ancien service SearXNG Render et les fichiers `searxng/` sont conservés temporairement comme secours jusqu'à la réussite d'un véritable test de bout en bout ; ils ne sont pas utilisés par le nouveau chemin.

La connexion plugin doit pointer vers l'URL MCP ci-dessus (et non vers la racine REST ou GitHub Pages). Après déploiement Render, vérifier le handshake MCP et la présence des outils ESPN, SearXNG et PropLine avant de déclarer l'intégration opérationnelle.

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
- V0.0.9 : outils MCP Streamable HTTP ESPN.
- V0.0.11 : client PropLine avec authentification par variable d'environnement et outils MCP de consultation des événements/cotes.
- Branche de migration PostgreSQL : backend psycopg optionnel, importateur SQLite idempotent et tests d'intégration PostgreSQL.


## PropLine sport modules (v0.0.13)

PropLine is exposed through three validated adapters:

- **Football:** pass the exact PropLine soccer key returned by `propline_sports` (for example, a `soccer_...` key). The adapter offers 1X2/moneyline, spreads, totals, BTTS, double chance, draw-no-bet, corners, cards and supported player markets.
- **Basketball:** pass the exact `basketball_...` provider key. The stable defaults are moneyline, spreads and totals; optional player props are discovered per event and requested only when that event actually offers them.
- **Tennis:** use the single provider key `tennis` across ATP, WTA, Challenger and ITF. Stable defaults are match winner, game handicap and game total. Optional tennis markets are discovered per event before any odds request; no unverified tennis prop key is assumed.

MCP tools: `propline_module_events`, `propline_module_odds`, `propline_module_event_markets`, and `propline_module_event_odds`. Event-specific odds requests first discover and validate actual per-event offerings. Period filters are forwarded to PropLine only when supported by the selected sport. ESPN event IDs and PropLine event IDs are provider-specific and must not be interchanged. Historical odds, closing lines and paid +EV endpoints are not part of the Free-tier integration.


## NODE.47 football model, validation, EV and staking — V0.0.24

### Football Poisson baseline
- REST: `POST /v1/predictions/football`; MCP: `football_poisson_predict`.
- Inputs are explicit pre-match home/home and away/away goals-for and goals-against averages, with sample sizes.
- The model computes `lambda_home` and `lambda_away` as the mean of each attack rate and the opponent's corresponding concession rate. It returns 1X2, Over/Under 2.5 and BTTS probabilities from independent Poisson distributions.
- This is a transparent baseline, **not a trained or calibrated model**. It does not automatically infer missing xG, lineups, injuries, tactical effects or opponent-strength adjustments. Minimum sample adequacy is not validation.

### Chronological backtesting
- REST: `POST /v1/backtests/football`; MCP: `football_backtest`.
- Supply timestamped historical pre-match snapshots and final scores. The endpoint sorts by prediction time, holds out the latest fraction and reports multiclass Brier Score, Log Loss and optional flat-1U paper ROI when all three 1X2 prices are present.
- The result is explicitly labelled `evaluation_only_not_model_validation`. It does not train the model, prove future profitability or automatically authorize betting. Do not use post-kickoff information in input snapshots.

### Market normalization, Edge and EV
- REST: `POST /v1/markets/no-vig` and `POST /v1/markets/edge-ev`; MCP: `football_edge_ev`.
- Decimal odds are converted to implied probabilities and normalized to remove the bookmaker overround. Edge is the difference between model probability and no-vig market probability; EV per unit is (p_{model} \times cote - 1).
- Market comparison may be displayed while the model is unvalidated, but the result remains `NO BET`.

### Staking in U
- REST: `POST /v1/staking/u`; MCP: `football_stake_u`.
- `bankroll_units` is the user's bankroll expressed in U. The default policy is quarter Kelly (`kelly_fraction=0.25`) with a maximum stake of `1.0 U` per selection. Both are configurable in the request; the service never assumes the user's monetary value for 1 U.
- Without an explicit deployment-level validation record, the result is always `NO BET` and `stake_u=0`. A client cannot self-declare the model validated.
- Betting can be enabled only by setting both `NODE47_FOOTBALL_MODEL_VALIDATED=1` and a non-empty `NODE47_FOOTBALL_VALIDATION_ID` in the API environment after a documented independent out-of-sample review. These variables are intentionally not enabled by default. The current V0.0.24 baseline therefore remains non-bet-eligible.

### MCP and SearXNG operational verification
- MCP remains Streamable HTTP at `/mcp/`. The release must pass a real `initialize` + `tools/list` handshake and execute at least one tool call after deployment; a 200 response from `/health` alone does not prove MCP transport health.
- SearXNG already exposes `searxng_health`, which dispatches a real GitHub Actions search and waits for the authenticated Render callback. It must be run against the deployed service with the production secrets configured; workflow success alone is not proof that the callback reached the waiting MCP request.
- Render health-check path: `/health`. It is an HTTP liveness/readiness response and is distinct from the MCP and SearXNG end-to-end checks.

### V0.0.24 safety status
The football engine is a provisional baseline. Until sufficient historical data has been evaluated out of sample, calibration and market-relative performance have been reviewed, and a validation record has been issued, it must not generate a positive stake. Never interpret a paper ROI from a small holdout as evidence of a durable edge.


## NODE.47 SPORT ANALYST — V0.0.25 multisport layer

V0.0.25 adds a tennis Elo baseline, independent football/basketball/tennis validation gates, and shared REST/MCP Edge/EV and U staking tools. All three sport models remain uncalibrated and non-bet-eligible by default. The shared staking policy caps requests at quarter Kelly and 1.0 U per selection; otherwise it returns NO BET / 0 U. See [docs/MULTISPORT_MODEL_V0.0.25.md](docs/MULTISPORT_MODEL_V0.0.25.md) for model assumptions, routes, validation requirements and remaining portfolio-risk limitations.


## Baseline activation and live research fallback (V0.0.26)

- The owner has explicitly confirmed the profitability of the football, basketball and tennis baselines. Each sport is activated independently using its own `NODE47_<SPORT>_MODEL_VALIDATED=1` and `NODE47_<SPORT>_VALIDATION_ID` settings. The API reports this as `user_confirmed_baseline`; it is not represented as an independent statistical audit.
- Chronological backtesting remains available only as an optional diagnostic. It is not required to activate a baseline and must not block analysis or staking when the per-sport owner-confirmation gate is enabled.
- If SearXNG is unavailable, returns no useful sources, or leaves an important evidence gap, the AI assistant continues with its own current online search capability. It must cite sources, record dates, cross-check conflicting information, and mark unresolved facts explicitly. Missing information must never be fabricated.
- Shared decisions remain sport-specific: no-vig market probabilities, Edge/EV, quarter-Kelly maximum, and a hard cap of 1 U per selection. A missing price, invalid probability, or non-positive EV remains `NO BET` / `0 U`.
