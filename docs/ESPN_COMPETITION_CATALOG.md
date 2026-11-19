# Registre complet des compétitions ESPN — NODE.47

## Source de découverte

Le registre NODE.47 cible les trois sports demandés : football (soccer), basketball et tennis. La découverte interroge les collections ESPN Core :

- https://sports.core.api.espn.com/v2/sports/soccer/leagues
- https://sports.core.api.espn.com/v2/sports/basketball/leagues
- https://sports.core.api.espn.com/v2/sports/tennis/leagues

Les références $ref de ces collections déterminent les identifiants ESPN. Le registre existant est fusionné afin de conserver les routes disponibles via Site API scoreboard même lorsqu’elles ne figurent pas dans le snapshot Core.

## Niveaux d’intégration

| Niveau | Signification |
|---|---|
| Découvert | La ligue est référencée par une collection ESPN Core ou conservée comme route Site API connue |
| Candidate | La route scoreboard n’a pas encore été validée |
| Verified | Au moins un probe Site API renvoie un objet JSON avec events de type liste |
| OK | La collecte courante contient des événements |
| Empty | Le scoreboard répond correctement, mais aucun événement n’est prévu dans la fenêtre demandée |
| Unavailable | La route scoreboard n’a pas répondu correctement lors de la collecte |

Un statut verified ne signifie pas qu’un match est actuellement disponible. Les résultats des collectes sont dans le manifeste espn_coverage.

## Activation

Seules les nouvelles routes verified sont activées automatiquement. Les routes précédemment activées restent configurées lors d’un échec temporaire de probe ; leur état réel est exposé dans la couverture de collecte.

## Utilisation depuis le plugin

1. Appeler espn_health.
2. Appeler espn_competitions avec sport=soccer, basketball ou tennis, status=verified et collection_enabled=true.
3. Appeler espn_coverage pour vérifier le statut réel de la route.
4. Appeler espn_events avec le sport et le competition_id exact, puis espn_event_detail avec event_id.
5. Ne jamais coder en dur une liste limitée de championnats ni déduire un identifiant ESPN d’un nom commercial.

Les IDs de ligue sont des identifiants ESPN. Ils ne doivent pas être confondus avec les clés de sport ou les IDs événementiels PropLine.
