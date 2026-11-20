# NODE.47 SearXNG — smoke test et solution de secours

Ce dossier contient une configuration SearXNG autonome conservée pour les tests du conteneur et comme solution de secours temporaire. **Le chemin de recherche de production est désormais exécuté à la demande par GitHub Actions** : voir `.github/workflows/searxng-search.yml`.

## Recherche de production

1. L'API Render déclenche le workflow GitHub Actions `searxng-search.yml`.
2. Le runner démarre une image SearXNG épinglée dans un conteneur éphémère.
3. SearXNG effectue la recherche et le workflow normalise les résultats.
4. Le runner transmet les résultats à `/v1/searxng/callback` via HTTPS, avec le secret de callback.
5. Le conteneur est supprimé à la fin du workflow.

Aucun `SEARXNG_URL` n'est requis pour ce chemin.

## Smoke test du conteneur

Le workflow `.github/workflows/searxng-deploy.yml` construit l'image de ce dossier, démarre un conteneur local sur le runner et vérifie l'API JSON. Malgré son ancien nom, il ne déploie pas de service Render permanent.

## Service Render autonome historique

Si le service Render autonome est encore actif, il doit être considéré comme un fallback temporaire. Il est public, sans authentification HTTP, et son limiteur est désactivé faute de Valkey. Ne pas le réactiver comme chemin de production sans authentification ou limitation de débit appropriée.

Ne supprimer le service de secours qu'après un test de bout en bout réussi du chemin GitHub Actions -> callback Render et confirmation que NODE.47 fonctionne sans lui.
