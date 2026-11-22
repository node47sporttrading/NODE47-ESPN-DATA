# NODE.47 multisport baselines and robot-native risk engine — V0.0.28

## Model scope
The backend provides transparent, uncalibrated baseline projections for football, basketball and tennis. They are exploratory estimates, not trained or calibrated probabilities. Input quality, market identity and model assumptions remain explicit in each analysis.

| Module | Baseline | Status |
|---|---|---|
| Football | Independent Poisson from home/away goals-for and goals-against rates | Uncalibrated |
| Basketball | Pace/efficiency normal baseline from supplied team aggregates | Uncalibrated |
| Tennis | Elo logistic baseline with optional surface adjustment | Uncalibrated |
| Corners/cartons | Separate football-derived robot module | Uses its own market-specific inputs |

A sample-size or input-coverage flag describes data adequacy; it does not alter the risk formula.

## Shared market calculations
- REST: `POST /v1/decision/no-vig`, `POST /v1/decision/edge-ev`.
- MCP: `node47_multisport_edge_ev`.
- Edge compares model probability with the no-vig market probability. EV per unit is `p × odds - 1`.

## Shared robot-native stake calculation
- REST: `POST /v1/decision/staking/robot`.
- MCP: `node47_robot_stake_u`.
- Supported modules: football, basketball, tennis and corners_cartons.
- The implementation mirrors `robot/src/55-risque.mjs::miseDe` and is the only backend stake calculator.
- Inputs: `p_final`, confidence (0–100 or null), exact decimal reference odds, push probability, profile and risk parameters.
- Conservative probability: `pCons = max(0.01, pFinal - ((100-confidence)/100 × CONF_PENALTY_PTS/100))`; null confidence applies the full penalty.
- Push-aware Kelly: `fStar = (pCons × odds + pPush - 1)/(odds - 1)`.
- Final stake: `round_quart(min(STAKE_SCALE × fStar, STAKE_MAX))`; below `STAKE_MIN` returns `NO BET` / 0 U.

### Profile defaults
| Profile | Default STAKE_MAX |
|---|---:|
| PRUDENT | 2 U |
| STANDARD | 3 U |
| FREQUENT | 3 U |
| CUSTOM | Explicit value required |

Default risk parameters are `STAKE_SCALE=25`, `CONF_PENALTY_PTS=5`, `STAKE_MIN=0.5 U`. There is no generic 1 U cap or separate quarter-Kelly override. The profile values are authoritative.

## Portfolio limitations
This is a per-selection calculator, not a portfolio ledger. It does not itself persist open positions, enforce correlated exposure across selections, or impose daily/weekly drawdown limits. The robot runtime's own passage/day budgets and pause controls remain separate.

## Runtime tools
- `node47_runtime_info`: reports model baselines and the shared robot-native risk contract.
- `node47_robot_stake_u`: returns the complete stake calculation and applied profile parameters.
- `node47_multisport_edge_ev`: returns EV and edge for market comparison.
