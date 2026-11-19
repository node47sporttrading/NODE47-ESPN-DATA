# NODE.47 ESPN DATA — V0.0.5

Connecteur multisport expérimental pour NODE.47 SPORT ANALYT. Il collecte les tableaux de scores ESPN, normalise les événements et publie des snapshots JSON statiques via GitHub Pages.

> **Important :** les endpoints ESPN utilisés sont non officiels et non documentés. Leur disponibilité varie selon le sport et la compétition. Une réponse vide ou une erreur HTTP n'est jamais transformée en donnée supposée. Vérifier les conditions d'utilisation ESPN avant toute collecte, republication ou réutilisation.

## Périmètre V0.0.5
- Football, basketball, tennis : **toutes** les compétitions actuellement énumérées par ESPN pour ces trois sports.
- `config/competitions.json` : les routes effectivement collectées (12 routes vérifiées).
- `config/registry.json` : le **registre multisport** recensant les 237 compétitions ESPN des trois sports, avec statut de vérification, catégorie, genre, zone et dernière vérification.
- Source primaire : scoreboard ESPN (`site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard`).
- Sorties : `site/data/latest.json`, `site/manifests/latest.json`, `site/index.json`, `site/index.html`.
- Exécution : GitHub Actions (planifiée et manuelle), publication GitHub Pages.

## Registre multisport (V0.0.4 + V0.0.5)
Le registre est la source de vérité du recensement. Règle du projet : une compétition n'est « vérifiée » que si son endpoint a été identifié, sondé et si son schéma a été validé en réel. Rien n'est inventé.

- `verified` : endpoint testé par sondes réelles (HTTP 200 + schéma validé) — 237/237 au 2026-11-19.
- `candidate` : présent dans l'énumération ESPN mais pas encore sondé.
- `unavailable` : sondé et non exploitable via le scoreboard (conservé dans le registre, jamais fabriqué).

Un scoreboard vide reste une réponse légitime (jour sans match / hors saison) : vide ≠ indisponible.

### Reconstruire le registre
```bash
# 1. Énumération live (source : sports.core.api.espn.com, liste officielle ESPN)
python3 tools/discover.py
# 2. Sondes (fenêtres dates personnalisables ; checkpointé et reprenable)
python3 tools/probe_registry.py --dates 20261122,20261125,20261128
# 3. Registre (statuts + classification dérivée)
python3 tools/build_registry.py
```

Les champs `category`, `gender`, `zone` sont une couche éditoriale **dérivée** des noms et slugs ESPN (voir `tools/build_registry.py`) ; sans signal explicite, la valeur est `unspecified`. Cette couche n'alimente jamais le moteur décisionnel.

## Architecture
1. `client.py` effectue les requêtes HTTP avec timeout, User-Agent et retry limité.
2. `collector.py` interroge les scoreboards activés.
3. `normalizer.py` convertit les réponses ESPN en schéma NODE.47.
4. `validator.py` contrôle la structure et marque les anomalies.
5. `cli.py` écrit les snapshots et le manifeste de collecte.
6. `tools/` : découverte (`discover.py`), sondes de vérification (`probe_registry.py`), construction du registre (`build_registry.py`).
7. GitHub Actions publie le dossier `site/` sur GitHub Pages.

## Exécution locale
Python 3.11+ recommandé.

```bash
python -m pip install -r requirements.txt
PYTHONPATH=src python -m node47_espn.cli --config config/competitions.json --output site
```

## Tests
```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
Les tests incluent les contrats du registre (`tests/test_registry.py`) : cohérence des statuts, unicité des identifiants, preuves de vérification et correspondance avec les routes activées.

## GitHub Pages
Dans **Settings → Pages → Build and deployment**, choisir **GitHub Actions** comme source. Le workflow `.github/workflows/espn-pages.yml` collecte les données puis déploie l'artefact Pages. Le site est public : ne jamais y placer de secrets, données personnelles ou identifiants.

URL attendue du projet : `https://node47sporttrading.github.io/NODE47-ESPN-DATA/` (disponibilité après activation et premier déploiement).

## Schéma de sortie
Chaque événement contient un identifiant source, le sport, la compétition, le statut, les équipes/participants si présents, l'horaire UTC si interprétable, le score si disponible, l'URL source et les indicateurs qualité. Les champs absents restent `null`.

## Limites connues
- V0.0.5 ne collecte pas encore les blessures, les rosters complets, les statistiques avancées, les cotes ni les compositions.
- Les routes de tennis sont vérifiées au niveau tournoi ; le mapping niveau match reste un chantier sport-spécifique.
- Un scoreboard vide peut signifier absence d'événement à la date courante, compétition hors saison ou route non prise en charge. Le connecteur ne conclut pas automatiquement à une panne.
- Les données sont des snapshots, pas une API temps réel garantie.
- Les horaires sont conservés en UTC ; les données ESPN non datées ne sont pas inventées.

## Roadmap
- V0.0.3 : socle de collecte et publication (fait).
- V0.0.4 : expansion du catalogue et registre multisport (fait — 237 compétitions recensées).
- V0.0.5 : découverte automatique des endpoints et vérification par sondes réelles (fait — 237/237 vérifiées).
- V0.0.6 : collecte étendue — intégrer progressivement les compétitions vérifiées au collecteur (au-delà des 12 routes).
- V0.0.7 : qualité et couverture — saisons, doublons, données manquantes, fraîcheur du registre.
- Ensuite : contrat d'intégration avec le plugin NODE.47 SPORT ANALYT.
