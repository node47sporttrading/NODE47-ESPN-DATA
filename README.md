# NODE.47 ESPN DATA — V0.0.3

Connecteur multisport expérimental pour NODE.47 SPORT ANALYT. Il collecte les tableaux de scores ESPN, normalise les événements et publie des snapshots JSON statiques via GitHub Pages.

> **Important :** les endpoints ESPN utilisés sont non officiels et non documentés. Leur disponibilité varie selon le sport et la compétition. Une réponse vide ou une erreur HTTP n'est jamais transformée en donnée supposée. Vérifier les conditions d'utilisation ESPN avant toute collecte, republication ou réutilisation.

## Périmètre V0.0.3
- Football : compétitions configurées dans `config/competitions.json`.
- Basketball : NBA, WNBA et NCAA men configurés comme candidats.
- Tennis : ATP et WTA configurés comme candidats.
- Source primaire actuelle : scoreboard ESPN.
- Sorties : `site/data/latest.json`, `site/manifests/latest.json`, `site/index.json`, `site/index.html`.
- Exécution : GitHub Actions (planifiée et manuelle), publication GitHub Pages.

La configuration initiale est un **catalogue de routes candidates**, pas une déclaration de couverture ESPN garantie. Le rapport `coverage` conserve le statut de chaque compétition.

## Architecture
1. `client.py` effectue les requêtes HTTP avec timeout, User-Agent et retry limité.
2. `collector.py` interroge les scoreboards activés.
3. `normalizer.py` convertit les réponses ESPN en schéma NODE.47.
4. `validator.py` contrôle la structure et marque les anomalies.
5. `cli.py` écrit les snapshots et le manifeste de collecte.
6. GitHub Actions publie le dossier `site/` sur GitHub Pages.

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

## GitHub Pages
Dans **Settings → Pages → Build and deployment**, choisir **GitHub Actions** comme source. Le workflow `.github/workflows/espn-pages.yml` collecte les données puis déploie l'artefact Pages. Le site est public : ne jamais y placer de secrets, données personnelles ou identifiants.

URL attendue du projet : `https://node47sporttrading.github.io/NODE47-ESPN-DATA/` (disponibilité après activation et premier déploiement).

## Schéma de sortie
Chaque événement contient un identifiant source, le sport, la compétition, le statut, les équipes/participants si présents, l'horaire UTC si interprétable, le score si disponible, l'URL source et les indicateurs qualité. Les champs absents restent `null`.

## Limites connues
- V0.0.3 ne collecte pas encore les blessures, les rosters complets, les statistiques avancées, les cotes ni les compositions.
- Les routes de tennis sont exploratoires et doivent être validées par les exécutions réelles.
- Un scoreboard vide peut signifier absence d'événement à la date courante, compétition hors saison ou route non prise en charge. Le connecteur ne conclut pas automatiquement à une panne.
- Les données sont des snapshots, pas une API temps réel garantie.
- Les horaires sont conservés en UTC; les données ESPN non datées ne sont pas inventées.

## Roadmap
- V0.0.3 : socle de collecte et publication.
- V0.3.1 : matrice de couverture vérifiée et résumés d'événements.
- V0.3.2 : enrichissement équipes/joueurs/statistiques/blessures lorsque supportés.
- V0.3.3 : historique, détection de fraîcheur et contrôles de régression.
- V0.3.4 : contrat d'intégration avec le plugin NODE.47 SPORT ANALYT.
