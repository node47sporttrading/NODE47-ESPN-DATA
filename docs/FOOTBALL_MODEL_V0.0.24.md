# NODE.47 Football Poisson baseline and robot-native staking

## Model scope
The football baseline estimates 1X2, BTTS and Over/Under 2.5 from supplied home/away goals-for and goals-against rates. The two score counts are modelled as independent Poisson variables. A finite score grid is normalized before the market probabilities are aggregated.

This is a transparent, uncalibrated baseline. It does not infer missing xG, lineups, injuries, tactical effects, opponent strength or other covariates. A sample-size flag describes input coverage only.

## Market value
EV per unit is (p_{model} \times odds - 1). Edge compares the model probability with the no-vig market probability. These quantities describe the supplied probability and price; they do not replace the NODE.47 decision process.

## Stake sizing — single source of truth
- REST: `POST /v1/decision/staking/robot`.
- MCP: `node47_robot_stake_u`.
- Source formula: `robot/src/55-risque.mjs::miseDe`.
- Inputs: module, final probability, confidence, exact decimal reference odds, push probability and active robot profile.
- Conservative probability: `pCons = max(0.01, pFinal - ((100-confidence)/100 × CONF_PENALTY_PTS/100))`. If confidence is absent, the full confidence penalty is applied.
- Kelly fraction with push: `fStar = (pCons × odds + pPush - 1)/(odds - 1)`.
- Stake: `round_quart(min(STAKE_SCALE × fStar, STAKE_MAX))`; if the result is below `STAKE_MIN`, the decision is `NO BET` and the stake is 0 U.

## Native profile defaults
- PRUDENT: `STAKE_MAX=2 U`.
- STANDARD: `STAKE_MAX=3 U`.
- FREQUENT: `STAKE_MAX=3 U`.
- CUSTOM: default `STAKE_MAX=3 U`, explicitly overridable.
- Default `STAKE_SCALE=25`, `CONF_PENALTY_PTS=5`, `STAKE_MIN=0.5 U`.

The service does not assume a currency value for 1 U. The shared tool calculates a single selection stake; it is not a portfolio ledger and does not itself enforce correlated exposure, daily drawdown or bankroll-wide limits.

## Routes and tools
- REST prediction: `POST /v1/predictions/football`.
- MCP prediction: `football_poisson_predict`.
- MCP market comparison: `football_edge_ev`.
- MCP stake sizing: `node47_robot_stake_u`.
