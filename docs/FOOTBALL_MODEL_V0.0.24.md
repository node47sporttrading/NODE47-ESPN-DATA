# NODE.47 SPORT ANALYST — football model and staking policy V0.0.24

## Scope
V0.0.24 adds a reproducible football Poisson baseline and explicit REST/MCP interfaces. It does not claim that this baseline is trained, calibrated, or profitable.

## Probability construction
For a home team and an away team, using only pre-match home/away split rates:
- lambda_home = (home goals-for per home match + away goals-against per away match) / 2
- lambda_away = (away goals-for per away match + home goals-against per home match) / 2

The two score counts are modelled as independent Poisson variables. A finite score grid is normalized before 1X2, BTTS and O/U 2.5 probabilities are aggregated. This simple construction is auditable but omits Dixon-Coles low-score dependence, opponent-strength adjustment, xG, lineups, injuries, tactical state and other covariates.

A minimum split sample is a data-quality flag only. It does not confer validation.

## historical evaluationing contract
The caller supplies timestamped historical snapshots containing the features known before kickoff and the final score. Rows are sorted chronologically; the latest fraction is held out. The endpoint reports out-of-sample multiclass Brier Score and Log Loss, plus optional flat-1U paper ROI when all three 1X2 odds are provided.

The earlier rows are not used to fit parameters. The test is therefore an evaluation of this fixed baseline, not model training. No future data may be present in the pre-match feature snapshot. A paper ROI is descriptive and does not demonstrate a persistent edge.

## Validation gate
The baseline always returns validation_status=not_validated and betting_eligible=false. No REST caller may set a model_validated boolean to bypass this gate. The server enables betting only when a complete independent out-of-sample validation record exists in `config/model_validation.json`.
- Activation is controlled by a complete independent validation record in `config/model_validation.json`; legacy owner-controlled environment flags are ignored.
## Market calculations
For a complete mutually-exclusive market, raw implied probabilities are 1 / decimal odds. No-vig probabilities divide each raw implied probability by their sum. Edge (percentage points) = model probability - no-vig market probability. EV per unit = model probability × decimal odds - 1.

An EV number can be shown diagnostically while the model is unvalidated, but it is not a betting recommendation. The output is NO BET until the server-side validation gate is active and EV is positive.

## U policy
- The bankroll input is expressed in U.
- 1 U is an abstract user-defined risk unit; the service does not assume a currency value or force a bankroll percentage.
- Default stake: 0.25 Kelly (quarter Kelly), capped at 1.0 U per selection.
- If model validation is absent or EV is non-positive: stake = 0 U, decision = NO BET.
- The user must supply bankroll size in U. No default bankroll is invented.
- The endpoint calculates a single-selection stake. It does not yet enforce correlated exposure across simultaneous bets, daily drawdown limits, or portfolio-wide caps; these remain explicit V0.0.25+ work.

## Interfaces
- REST prediction: POST /v1/predictions/football
- REST no-vig: POST /v1/markets/no-vig
- REST Edge/EV: POST /v1/markets/edge-ev
- REST stake: POST /v1/staking/u
- REST historical evaluation: POST /v1/historical evaluations/football
- MCP tools: football_poisson_predict, football_edge_ev, football_stake_u, football_historical evaluation, node47_runtime_info

## MCP transport release gate
The public endpoint remains /mcp/ using Streamable HTTP. Deployment verification must perform:
1. MCP initialize request and confirm a successful protocol response plus session handling.
2. notifications/initialized.
3. tools/list and confirm the V0.0.24 football tools plus ESPN, SearXNG and PropLine tools.
4. A real read-only tool call such as node47_runtime_info.
5. A real searxng_health call, which verifies the GitHub Actions dispatch, ephemeral SearXNG execution and authenticated callback to the waiting Render request.

An HTTP /health response alone does not prove the MCP transport or SearXNG callback works. Do not label the release fully operational until all five checks pass.