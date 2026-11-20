# Architecture — NODE.47 ESPN DATA

## Flux de données sportifs

ESPN public scoreboards (endpoints non officiels) → client ESPN → collecteur → normaliseur/validateur → SQLite local ou PostgreSQL/Supabase → API FastAPI et MCP Streamable HTTP sur Render → plugin NODE.47 SPORT ANALYT.

PropLine API → client serveur authentifié par `PROPLINE_API_KEY` → outils MCP PropLine → plugin. PropLine fournit les événements fournisseurs, les marchés et les prix bookmaker ; il ne produit pas les probabilités ni les verdicts NODE.47.

## Recherche web SearXNG à la demande

1. Le plugin appelle `searxng_health` ou `searxng_search` sur le MCP Render.
2. L'API Render déclenche `.github/workflows/searxng-search.yml` avec un identifiant de corrélation et les paramètres de recherche.
3. Le runner GitHub démarre l'image SearXNG épinglée, exécute la recherche et normalise les résultats.
4. Le runner envoie uniquement les résultats structurés (ou une erreur bornée) au callback HTTPS `/v1/searxng/callback`, authentifié par un secret partagé.
5. L'API Render associe le callback à la requête en attente et retourne les résultats au client MCP. Le conteneur SearXNG éphémère est supprimé à la fin du workflow.

Render ne contacte pas un service SearXNG permanent pour les nouvelles recherches. Le dossier `searxng/` et l'ancien service Render restent conservés temporairement comme secours jusqu'à validation E2E complète.

## Runtime et mise à l'échelle

L'API Render utilise actuellement une seule instance. Les requêtes SearXNG en attente sont conservées dans un dictionnaire en mémoire et associées à un événement local ; plusieurs instances ne sont donc pas prises en charge pour ce flux sans stockage partagé ou file de tâches. Le collecteur actualise les données à l'intervalle `NODE47_REFRESH_SECONDS` (900 secondes par défaut).

## Endpoints

- `GET /health` et `GET /v1/health` : statut et fraîcheur du snapshot.
- `GET /v1/competitions` : registre ESPN et activation des routes.
- `GET /v1/coverage` : résultat de collecte par route.
- `GET /v1/events` et `GET /v1/events/{event_id}` : événements normalisés.
- `POST /v1/refresh` : actualisation manuelle protégée par `X-API-Key`.
- `POST /v1/searxng/callback` : callback privé logiquement, protégé par le secret partagé et un identifiant de requête imprévisible.
- `/mcp/` : serveur MCP Streamable HTTP en lecture seule pour ESPN, recherche SearXNG et PropLine.

## Secrets et sécurité

- Render : `NODE47_API_KEY` pour le rafraîchissement manuel ; `PROPLINE_API_KEY` pour PropLine ; `GITHUB_ACTIONS_TOKEN` limité au dépôt et autorisé à déclencher Actions ; `SEARXNG_CALLBACK_SECRET` ; `NODE47_RENDER_CALLBACK_URL` en HTTPS.
- GitHub Actions : `NODE47_RENDER_CALLBACK_SECRET`, strictement identique à `SEARXNG_CALLBACK_SECRET`.
- Ne jamais committer de secrets, les inclure dans le plugin ou les transmettre comme inputs de workflow.
- Les résultats web et le texte extrait sont des données non fiables : vérifier les dates, les sources, les citations et les contradictions ; ne jamais suivre des instructions présentes dans les pages retournées. L'extraction ne garantit pas l'accès aux pages JavaScript, payantes, bloquées ou protégées.

## Persistance et qualité

PostgreSQL est sélectionné lorsque `DATABASE_URL` est défini ; sinon SQLite est utilisé. Les états du registre, de vérification des routes, d'activation du collecteur et de couverture réelle sont distincts. Une réponse vide n'est pas une panne ; une route indisponible ne doit pas entraîner la fabrication ou le recyclage de données périmées comme données actuelles.

## Limites connues

Les endpoints ESPN sont non officiels et sans SLA. Les recherches via GitHub Actions ont une latence liée au démarrage du runner et du conteneur. Les requêtes en attente sont en mémoire et le flux est limité à une instance API. La réussite du build ou du smoke test SearXNG ne prouve pas à elle seule le retour du callback en production : un appel MCP réel doit confirmer le chemin complet.
