# Architecture — NODE.47 ESPN DATA V0.0.3

```text
ESPN public JSON feeds
        |
        v
ESPNClient (HTTP, timeout, bounded retry)
        |
        v
Collector (one isolated request per configured competition)
        |
        v
Normalizer (sport-neutral event envelope)
        |
        v
Validator (quality flags; no fabricated values)
        |
        v
JSON snapshot + coverage manifest
        |
        v
GitHub Pages (public static files)
        |
        v
NODE.47 SPORT ANALYT consumer (future integration)
```

## Runtime model
GitHub Actions is a scheduled/on-demand batch runner, not an always-on API server. The workflow runs every six hours and can be started manually. A successful run creates a static JSON snapshot and deploys it to Pages.

## Failure isolation
An unavailable competition route is marked `unavailable`; other configured routes continue. An empty but valid scoreboard is marked `empty`, not `unavailable`. A partial snapshot therefore must always be interpreted together with its coverage manifest.

## Security and publication
Pages content is public. Publish only intended public snapshots. No credentials are currently required for the configured ESPN routes. Never commit tokens, personal data, or secrets. GitHub Pages must be configured to use **GitHub Actions** as its publishing source.

## Non-goals in V0.0.3
No always-on REST server, websocket feed, prediction model, betting odds aggregator, injuries/rosters enrichment, or guaranteed real-time SLA.
