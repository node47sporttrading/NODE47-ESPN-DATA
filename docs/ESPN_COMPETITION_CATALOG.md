# Catalogue ESPN complet — NODE.47 SPORT ANALYT

## Source et périmètre

Le recensement est obtenu en énumérant les collections ESPN Core :

- `https://sports.core.api.espn.com/v2/sports/soccer/leagues`
- `https://sports.core.api.espn.com/v2/sports/basketball/leagues`
- `https://sports.core.api.espn.com/v2/sports/tennis/leagues`

Les identifiants de ligue sont extraits des références `$ref` ESPN. Les noms commerciaux ne servent jamais à fabriquer un ID. Le catalogue est un instantané évolutif ; le nombre de compétitions ne doit pas être codé en dur.

Le snapshot courant du dépôt contient 237 identifiants : 220 soccer, 15 basketball et 2 tennis.

## États de l'intégration

| État | Signification |
|---|---|
| `candidate` | ESPN Core référence la ligue, mais le scoreboard n'a pas encore été validé |
| `verified` | Le scoreboard Site API répond avec un objet JSON et un champ `events` de type liste |
| `unavailable` | Les probes n'ont pas réussi pendant la dernière vérification |

Un scoreboard vide (`events: []`) reste une réponse valide et donc une route vérifiée. Cela ne signifie pas qu'un match est programmé à l'instant. Le statut opérationnel de chaque route est distinct et visible dans `espn_coverage`.

## Activation et résilience

Les nouvelles routes ne sont activées qu'après vérification du schéma scoreboard. Les routes déjà actives restent configurées en cas d'échec temporaire de probe ; elles apparaissent alors comme `unavailable` dans le registre et leur résultat de collecte réel est indiqué dans la couverture. Les routes candidates non vérifiées ne sont pas activées.

## Outils MCP utilisés par NODE.47

1. `espn_health` — contrôler l'état et la fraîcheur du service.
2. `espn_competitions` — découvrir le catalogue complet et filtrer par sport, statut, catégorie, genre, zone ou activation.
3. `espn_coverage` — contrôler l'état de collecte effectif des routes.
4. `espn_events` — rechercher les matchs par sport et ID de ligue ESPN.
5. `espn_event_detail` — récupérer le détail d'un événement à partir de son ID ESPN exact.

Pour chaque analyse, sélectionner la ligue dans le catalogue, contrôler la couverture, puis interroger les événements. Ne jamais coder en dur un sous-ensemble de championnats ni supposer qu'un ID PropLine est égal à un ID ESPN.

## Synchronisation

`tools/discover.py` énumère les collections Core. `tools/probe_registry.py` vérifie les scoreboards. `tools/build_registry.py` reconstruit le registre et `tools/activate_verified_competitions.py` active les nouvelles routes validées. Le workflow hebdomadaire soumet les changements dans une Pull Request pour revue humaine.
