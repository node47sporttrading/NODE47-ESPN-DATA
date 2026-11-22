# NODE.47 — NBA Prediction Engine V0.1 (baseline)

## Scope

This first implementation is a deterministic, explainable baseline. It is not a trained model and is not calibrated. It must not be presented as a validated betting model.

The caller supplies both teams' current points scored per game, points allowed per game and pace. These values must be snapshots available at or before the prediction timestamp. The endpoint does not scrape, infer or silently fill missing statistics.

## Model

Expected possessions:

`P = (pace_home + pace_away) / 2`

For each side, the model averages its offensive points-per-possession rating with the opponent's defensive points-allowed-per-possession rating, then multiplies by expected possessions. Home-court points are added to the home projection and subtracted from the away projection in equal halves.

The expected score difference is converted to a win probability using a normal approximation. The default margin and total standard deviations (12 and 18 points) are explicit placeholders, not fitted parameters. They must be estimated and calibrated on historical out-of-sample NBA games before operational use.

## REST endpoint

`POST /v1/predictions/basketball`

Example request:

```json
{
  "home": {
    "name": "Spurs",
    "points_for_per_game": 117.1,
    "points_against_per_game": 105.9,
    "pace": 97.7
  },
  "away": {
    "name": "Clippers",
    "points_for_per_game": 111.9,
    "points_against_per_game": 117.7,
    "pace": 99.0
  },
  "market_total": 225.5,
  "market_home_handicap": -15.5
}
```

Optional fields: `home_court_points`, `margin_standard_deviation`, `total_standard_deviation`, `market_total`, `market_home_handicap`.

The response includes projected possessions, team points, margin, total, win probabilities and (when supplied) probabilities relative to the market total and home handicap. It always labels this implementation `baseline_uncalibrated`.

## historical model evaluationing utilities

`node47_espn.evaluation.chronological_split` sorts observations by prediction timestamp and creates a forward-in-time split. `evaluate_predictions` reports Brier score, log loss, accuracy, reliability-bin summaries and score MAE/RMSE when scores are supplied.

The split helper is not a complete rolling-origin training pipeline. A valid evaluation must reconstruct each historical prediction using only information available before tip-off, preserve archived input snapshots and odds timestamps, and keep a final untouched test period. Do not randomly shuffle games across time.

## Required next phase

1. Ingest and persist historical NBA game results and time-stamped team-stat snapshots.
2. Build a point-in-time feature table with no post-game leakage.
3. Keep the baseline non-bet-eligible until an independent out-of-sample validation report has been reviewed and recorded.
4. Fit/calibrate variance and win probabilities on training/validation periods only.
5. Report sample size, Brier score, log loss, calibration, score errors and confidence intervals on a final holdout.
6. Add injuries, player availability, rest, travel and lineup adjustments only when their historical timestamps and provenance are available.

Until those gates pass, predictions are exploratory projections, not validated edges. No expected-value or bet recommendation should be emitted from this baseline alone.
