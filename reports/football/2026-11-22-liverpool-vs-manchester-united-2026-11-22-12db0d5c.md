# NODE.47 SPORT ANALYST — Liverpool vs Manchester United

## 1. Fiche événement
- Sport : football ; compétition : English Premier League ; compétition ESPN : `eng.1`.
- Match : Liverpool (domicile) — Manchester United (extérieur), Anfield.
- Date/heure : 2026-11-22 16:30 UTC, soit 17:30 Africa/Douala.
- Statut : programmé, pré-match.
- ESPN event_id : `401878755`. PropLine sport_key : `soccer_epl`. PropLine event_id : `555685`.
- Identité confirmée par ESPN et crosswalk PropLine explicite via `espn_event_id`.

## 2. Journal des contrôles
- ESPN health : OK, dernière actualisation 2026-11-22T16:12:31Z, âge 368 s lors du contrôle.
- Registre ESPN soccer : 220 compétitions recensées ; compétition exacte `eng.1`, statut verified et collection activée.
- ESPN coverage : consultée ; route opérationnelle selon la collecte de l’événement.
- ESPN events puis event_detail : OK ; participants, horaire, lieu et statut confirmés.
- PropLine health/sports : OK ; sport EPL disponible.
- PropLine module events, markets et odds : OK ; événement et marchés réellement offerts confirmés.
- SearXNG health/search : OK ; recherches ciblées avec lecture de pages lorsque l’extraction était disponible.
- Runtime : modèle football independent_poisson_baseline_uncalibrated ; validation hors échantillon absente ; staking désactivé.
- Limites : aucun historique complet d’ouverture fourni ; composition Liverpool et informations médicales exhaustives non établies dans une source officielle lisible.

## 3. Données sportives et audit des lacunes
- Liverpool : 5e, 18 points après 10 matches, bilan 5-3-2, 14 buts marqués et 10 encaissés. Source lue : https://www.stat-football.com/en/t/eng10.php
- Liverpool à domicile : 1 victoire, 2 nuls, 2 défaites ; 4 buts marqués, 6 encaissés en 5 matches. Source lue : https://www.statmuse.com/fc/ask/liverpool-home-record-this-year?l=pl
- Manchester United : 19e, 8 points après 10 matches, bilan 1-5-4, 14 buts marqués et 19 encaissés. Source lue : https://www.statmuse.com/fc/ask/man-united-goals-conceded?l=pl
- Manchester United à l’extérieur : 0 victoire, 3 nuls, 2 défaites ; 4 buts marqués, 8 encaissés en 5 matches. Source lue : https://www.footballmatchstats.com/team/manchester-united/away
- Forme récente rapportée : Liverpool a gagné 6 de ses 10 derniers matches ; United une seule fois sur les 10 derniers. Source lue : https://nerdytips.com/blog/liverpool-vs-manchester-united-prediction-2026-11-22/
- Absences : USA Today rapporte Baleba, Šeško et Ugarte absents pour United ; Shaw/Rashford en retour possible ; Maguire/Dorgu de retour à l’entraînement. Source lue : https://www.usatoday.com/story/sports/soccer/epl/2026/11/22/manchester-united-lineup-liverpool-premier-league/92893016007/
- Changement de banc : Mauricio Pochettino prépare son premier match avec United, après une prise de fonction récente ; la préparation tactique est donc peu documentée. Source lue : https://www.bbc.com/sport/football/articles/cqn70v814ke6o
- Non établi : météo, arbitre, composition officielle complète de Liverpool, historique de prix d’ouverture et mouvements intermédiaires.

## 4. Analyse tactique et qualitative
| Facteur | Observation et preuve | Effet marché | Contre-argument | Confiance |
|---|---|---|---|---|
| Structure de match | United arrive avec un nouvel entraîneur et peu de séances de préparation, selon The Standard et BBC. | Soutient prudence/Under au départ. | Un changement de coach peut créer un surcroît d’intensité. | Moyenne |
| Production à domicile | Liverpool n’a inscrit que 4 buts en 5 matches à Anfield ; source StatMuse lue. | Soutient Under et limite la confiance dans Liverpool 1X2. | Échantillon de cinq matches et adversaire de prestige. | Moyenne |
| Production extérieure | United n’a marqué que 4 buts en 5 déplacements et encaissé 8 ; source Football Match Stats lue. | Soutient Under et Liverpool léger favori. | United peut exploiter les transitions et l’effet “nouveau coach”. | Moyenne |
| Pressing/transitions | Le scénario le plus plausible est Liverpool dominant davantage le territoire, United cherchant sorties rapides et transitions ; ceci est une hypothèse tactique appuyée par les splits de buts, pas une observation vidéo du match. | Favorise un match à faible volume si Liverpool contrôle sans convertir. | Un but précoce peut casser le plan et ouvrir la rencontre. | Faible à moyenne |
| Matchups individuels | Non établi sans compositions officielles et rôles stabilisés. | Neutre/indisponible. | — | Faible |
| Coups de pied arrêtés | Non établi. | Neutre/indisponible. | — | Faible |

Synthèse : avantage structurel Liverpool, mais son rendement à Anfield et le faible rendement extérieur de United soutiennent davantage un scénario 1-0, 1-1 ou 2-0 qu’un match à quatre buts. La nouveauté du banc de United est le principal facteur d’invalidation.

## 5. Modèle quantitatif
- Baseline : Poisson indépendant non calibré.
- Taux utilisés : Liverpool domicile GF 0,80 ; GA 1,20 ; Manchester United extérieur GF 0,80 ; GA 1,60 ; cinq matches par split.
- Lambda résultants : Liverpool 1,20 ; Manchester United 1,00.
- Probabilités modèle : Liverpool 40,6 % ; nul 28,9 % ; Manchester United 30,5 % ; Over 2,5 37,7 % ; Under 2,5 62,3 % ; BTTS Oui 44,2 % ; BTTS Non 55,8 %.
- Limites : petit échantillon, indépendance des buts, absence d’ajustement Dixon-Coles, force des adversaires, compositions, fatigue et validation hors échantillon non intégrées. Probabilités descriptives, non éligibles aux mises.

## 6. Marchés et prix
Snapshot PropLine récupéré autour de 2026-11-22T16:23Z ; prix bruts américains, conversion décimale locale.
- 1X2 : Liverpool environ -111 à -143 (1,90 à 1,70), nul environ +280 à +330 (3,80 à 4,30), United environ +275 à +360 (3,75 à 4,60).
- Totaux : Over 2,5 observé -208 (1,48) chez AdmiralBet ; Under 2,5 +145 (2,45). D’autres opérateurs proposaient une ligne 3,0 ou 3,5 ; comparaison non mélangée.
- BTTS : Oui environ -189 à -250 (1,53 à 1,42), Non environ +134 à +178 (2,34 à 2,78).
- Règlement : marchés pré-match, match complet, sous réserve du règlement propre au bookmaker.

## 7. Historique et structure du marché
- Snapshot courant multi-bookmakers ; historique d’ouverture complet non fourni.
- Dernières mises à jour observées sur les books : environ 16:20–16:24 UTC.
- Marge/no-vig calculable sur une capture complète AdmiralBet : 1X2 marge approximative 3,9 % ; no-vig Liverpool 52,5 %, nul 24,0 %, United 23,5 %. Totaux 2,5 marge approximative 8,4 % ; no-vig Over 62,3 %, Under 37,7 %.
- Statut : SNAPSHOT SEUL ; aucune trajectoire fiable d’ouverture ne doit être reconstruite.

## 8. Pourquoi ce prix maintenant
- Fait corroboré : Liverpool est favori à domicile et United est 19e avec un faible bilan extérieur.
- Fait rapporté : United change d’entraîneur juste avant ce déplacement ; les absences rapportées peuvent aussi influencer la structure.
- Hypothèse plausible : le marché valorise l’écart de classement, l’avantage d’Anfield et le risque de désorganisation de United.
- Inconnue : sans historique d’ouverture et sans données de liquidité, la cause exacte des mouvements de prix est inconnue.

## 9. Matrice de convergence
| Marché/direction | Sport/modèle | Tactique/scénario | Infos/conditions | Prix | Statut |
|---|---|---|---|---|---|
| Liverpool 1X2 | Neutre : modèle 40,6 % seulement | Soutient légèrement | Soutient légèrement | S’oppose à la valeur au prix favori | Faible |
| Under 2,5 | Soutient : 62,3 % | Soutient modérément | Soutient légèrement | S’oppose : marché no-vig Over 62,3 % | Partielle/contradictoire |
| BTTS Non | Soutient : 55,8 % | Soutient légèrement | Neutre | S’oppose : marché favorise BTTS Oui | Faible à partielle |

## 10. Cohérence
- Cohérence des splits de buts : compatible avec un match contenu, mais échantillons courts.
- Contradiction principale : le modèle et les splits défensifs penchent Under alors que la structure de prix 2,5 penche Over.
- Cohérence temporelle : prix observés avant le coup d’envoi et après la publication des informations de banc/lineups.
- Données de composition incomplètes : confiance réduite.

## 11. Alignement
- Under 2,5 traduit bien le mécanisme “faible production domicile de Liverpool + faible production extérieure de United”.
- L’alignement reste moyen car un but précoce, une erreur individuelle ou l’effet émotionnel du derby peuvent produire un match ouvert.
- Le 1X2 est moins bien aligné avec les données : Liverpool est favori, mais ses performances à Anfield sont faibles.

## 12. Confiance
- Qualité : moyenne.
- Fraîcheur : bonne au moment de la collecte.
- Couverture : identité, marché et splits principaux disponibles ; compositions et météo incomplètes.
- Indépendance : plusieurs familles de sources, mais certaines statistiques proviennent de bases secondaires.
- Confiance globale : moyenne-faible.

## 13. Edge / EV
- Le calcul descriptif modèle-prix n’est pas autorisé comme Edge de mise : modèle non validé côté serveur.
- Under 2,5 à +145 impliquerait une EV théorique positive avec 62,3 %, mais cette EV n’est pas bet-eligible et est fortement sensible aux hypothèses.
- Edge officiel : NON CALCULABLE pour une mise ; validation football `not_validated`.

## 14. Classement des marchés
1. Lean analytique : Under 2,5, mais conflit direct avec le prix de marché et sans validation.
2. Lean secondaire : BTTS Non, moins robuste car un seul but de chaque côté suffit à invalider.
3. Liverpool 1X2 : favori logique mais prix comprimé et historique domicile insuffisant.

## 15. Chemin décisionnel
- Événement, participants, horaire, marché et crosswalk : satisfaits.
- Prix actuel : satisfait, mais snapshot seul.
- Deux familles indépendantes : présentes.
- Convergence forte, cohérence forte, alignement fort et confiance haute : non satisfaits.
- Contradiction prix/modèle non résolue et validation hors échantillon absente : décision limitée par le moteur.

## 16. Mise
- NON DÉTERMINÉE PAR LE MOTEUR.
- Mise : 0 U.
- Aucune mise calculée : modèle football non validé et prix/ligne en contradiction avec la lecture statistique.

## 17. Verdict final
**NO BET — 0 U.**

Lean football : match plutôt fermé, avec préférence descriptive pour Under 2,5 et score-type 1-0 / 1-1 / 2-0. Le marché favorise toutefois l’Over 2,5 et le BTTS Oui, le modèle est non calibré/non validé, les compositions et la dynamique du nouveau staff de United ajoutent de l’incertitude. Le prix ne fournit donc pas une convergence suffisante pour une sélection officielle.
