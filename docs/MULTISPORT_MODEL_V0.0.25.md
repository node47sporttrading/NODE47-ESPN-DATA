# NODE.47 SPORT ANALYST — V0.0.25 multisport model layer

## Scope and maturity

V0.0.25 connects the three sport modules to a shared Edge/EV and U staking layer. It does not claim that any of the current baselines is validated or profitable.

| Sport | Probability baseline | Current maturity | Primary limitations |
|---|---|---|---|
| Football | Independent Poisson using home/away goals-for and goals-against rates | Uncalibrated | No Dixon-Coles, xG, opponent-strength, lineup or injury adjustments |
| Basketball | Pace and points-for/against projection; normal approximation for margin/total | Uncalibrated | Inputs supplied by caller; default dispersions are placeholders; no historical point-in-time feed |
| Tennis | Elo logistic match-winner probability, surface Elo when supplied for both players | Uncalibrated | No serve/return, fatigue, injury, travel or tournament context; no set/game distribution |

All three model endpoints return exploratory probabilities. A sample-size flag is not validation. Tennis match winner is the only tennis market modelled; set betting, game handicap and totals are not inferred from the winner probability.

## Tennis model

- REST: `POST /v1/predictions/tennis`
- REST backtest: `POST /v1/backtests/tennis`
- MCP: `tennis_elo_predict`, `tennis_backtest`

Required player snapshots: `name`, `overall_elo`, `matches_played`. Optional `surface_elo` is used only when both players provide it. Supported surfaces: hard, clay, grass, carpet, unknown. Best-of-3/5 is recorded as match metadata and does not change the match-winner probability.

The model uses the Elo logistic transform:
`P(A wins) = 1 / (1 + 10^(-(Elo_A - Elo_B)/400))`.
The scale 400 is a fixed baseline assumption, not estimated or calibrated in this release.

The backtest sorts archived pre-match Elo snapshots chronologically and evaluates the latest holdout with Brier score, log loss and accuracy. It does not train or tune Elo ratings and cannot grant validation.

## Shared market and U decision layer

- REST no-vig: `POST /v1/decision/no-vig`
- REST Edge/EV: `POST /v1/decision/edge-ev`
- REST stake: `POST /v1/decision/staking/u`
- MCP: `node47_multisport_edge_ev`, `node47_multisport_stake_u`

The `sport` field must be football, basketball or tennis. Validation gates are independent:

- `NODE47_FOOTBALL_MODEL_VALIDATED=1` and `NODE47_FOOTBALL_VALIDATION_ID`
- `NODE47_BASKETBALL_MODEL_VALIDATED=1` and `NODE47_BASKETBALL_VALIDATION_ID`
- `NODE47_TENNIS_MODEL_VALIDATED=1` and `NODE47_TENNIS_VALIDATION_ID`

Both variables for the selected sport must be present. No client-supplied boolean can enable betting. All gates remain disabled by default.

Risk policy:
- Quarter Kelly maximum: 0.25.
- Per-selection maximum: 1.0 U.
- A caller may request lower limits but cannot raise either cap.
- If validation is absent or EV is non-positive, response is `NO BET` and `stake_u=0`.
- `bankroll_units` is supplied by the caller in U; 1 U remains user-defined and has no assumed currency value.

This is a per-selection stake calculator, not a portfolio ledger. V0.0.25 does not yet persist open positions, enforce correlated exposure across selections, or impose daily/weekly drawdown limits. Do not interpret the shared calculator as portfolio risk management.

## Validation required before enabling a sport

Each sport needs a separate signed/reviewed validation record with:
1. Point-in-time historical snapshots and provenance.
2. Strict chronological or rolling-origin evaluation with a final untouched holdout.
3. Sample size and competition/surface coverage.
4. Brier score, log loss, calibration/reliability analysis and confidence intervals.
5. Benchmark against no-vig closing market probabilities where timestamped prices exist.
6. Leakage audit, missing-data policy and model limitations.
7. Explicit approval and a unique validation ID.

No such validation is performed or certified by this code release. Keep all three validation gates disabled.

## Existing basketball and football routes

- Football: `POST /v1/predictions/football`, `POST /v1/backtests/football`.
- Basketball: `POST /v1/predictions/basketball`; historical evaluation utilities exist but no complete automated point-in-time basketball backtest pipeline is supplied by this release.

## Tests and deployment

Run `PYTHONPATH=src python -m unittest discover -s tests -v`. The release should not be merged or deployed unless CI passes. After deployment, verify:
- `GET /v1/health` reports version 0.0.25.
- OpenAPI contains all three prediction endpoints and shared decision endpoints.
- MCP `initialize`, `tools/list`, and real calls to tennis and shared staking tools succeed.
- Shared staking returns `NO BET` / `0 U` for all sports under default production configuration.
- SearXNG callback E2E remains healthy.

A health endpoint response alone does not prove MCP or SearXNG end-to-end health.
