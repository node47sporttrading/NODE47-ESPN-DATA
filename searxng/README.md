# NODE.47 SearXNG — compatibilité historique

Le nouveau chemin de recherche web NODE.47 est exécuté à la demande par GitHub Actions. Le workflow `.github/workflows/searxng-search.yml` démarre un conteneur SearXNG éphémère sur le runner, effectue la recherche et transmet uniquement les résultats structurés au callback HTTPS authentifié de l'API Render. Le conteneur est supprimé à la fin du workflow.

## Service Render historique

Le service autonome `node47-searxng-xm7g` reste temporairement conservé comme secours pendant la validation du nouveau chemin. Les fichiers `Dockerfile`, `settings.yml` et `render.yaml` de ce dossier sont maintenus pour permettre son redémarrage et le test de construction CI. Ils ne sont pas utilisés par les nouveaux appels MCP `searxng_health` et `searxng_search`.

Ne pas configurer `SEARXNG_URL` sur l'API NODE.47 pour le nouveau chemin : l'API déclenche GitHub Actions et reçoit les résultats via `/v1/searxng/callback`.

## Retrait du service historique

Ne supprimer le service Render historique et ces fichiers qu'après avoir vérifié un appel réel `searxng_search` depuis MCP, une exécution réussie de `searxng-search.yml`, la réception du callback authentifié et le retour des URL sources dans la réponse MCP.
