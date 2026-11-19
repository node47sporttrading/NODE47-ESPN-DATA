# ESPN endpoint strategy

## Scoreboards
The connector currently uses the public-facing, undocumented ESPN site API pattern:

`GET https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard`

Optional `dates=YYYYMMDD` is passed when a date is requested. The route and payload are not a stable, official API contract. Keep route failures visible in the collection manifest.

## Initial route catalogue

| Sport slug | League slug | Scope | Initial confidence |
|---|---|---|---|
| soccer | eng.1 | English Premier League | Candidate |
| soccer | esp.1 | LaLiga | Candidate |
| soccer | ger.1 | Bundesliga | Candidate |
| soccer | ita.1 | Serie A | Candidate |
| soccer | fra.1 | Ligue 1 | Candidate |
| soccer | uefa.champions | UEFA Champions League | Candidate |
| soccer | usa.1 | MLS | Candidate |
| basketball | nba | NBA | Candidate |
| basketball | wnba | WNBA | Candidate |
| basketball | mens-college-basketball | NCAA Men's Basketball | Candidate |
| tennis | atp | ATP Tour | Exploratory |
| tennis | wta | WTA Tour | Exploratory |

These are configured probes, not guarantees of coverage. In particular, tennis routes require empirical confirmation from Actions logs and should not be relied upon until then.

## Future enrichment routes
When scoreboard collection is stable, evaluate per-event summary routes:
`/apis/site/v2/sports/{sport}/{league}/summary?event={event_id}`

Only add statistics, injuries, rosters, odds or play-by-play after response-shape validation, licensing review, and sport-specific tests. Do not silently treat missing fields as zero.

## Data-use warning
These routes are unofficial and may change or become unavailable. Public accessibility is not a license to republish or commercially reuse ESPN content. Review ESPN's applicable terms and applicable law before public distribution.
