# NODE.47 — River Plate vs Lanús — 22 novembre 2026

## 1. Fiche événement
- Sport : football. Compétition : Argentine Liga Profesional de Fútbol, Clausura — 8es de finale (libellé confirmé par la page consultée FotMob).
- Match : River Plate (domicile) — Lanús (extérieur), dimanche 22 novembre 2026, 22:00 UTC / 23:00 Africa/Douala.
- Stade : Estadio Más Monumental, Buenos Aires. ESPN : statut **Scheduled** lors du relevé; ID événement `401933761`; compétition ESPN `arg.1`.
- PropLine : `soccer_argentina_primera`, ID `723681`; crosswalk explicite `espn_event_id=401933761`; coup d’envoi identique.
- Arbitre, météo et onze officiel : NON FOURNI par ESPN. Une page FotMob lue mentionne Pablo Dóvalo et 26 °C ; cette donnée reste secondaire, non confirmée par une source primaire.

## 2. Journal des contrôles
- ESPN health : **ok**, refresh 2026-11-22T14:23:53Z, âge 422 s au contrôle, 821 événements.
- Catalogue ESPN : `sport=soccer`, statut `verified`, collecte activée. Couverture consultée; événement recherché et détail ESPN lu.
- SearXNG health : **ok**; recherches ciblées avec `fetch_pages=true` exécutées (effectifs, forme, statistiques, tactique).
- PropLine health et sports : **ok**, données fraîches; séquence événements → crosswalk → catalogue marchés → cotes exécutée.
- Limite : aucun historique complet d’ouverture/variation ni règlement détaillé de chaque bookmaker dans les réponses. Statut marché : **SNAPSHOT SEUL**.

## 3. Données sportives et audit des lacunes
- Données disponibles, lues : résultats récents, moyennes domicile/extérieur et indicateurs de tirs via Scores24; tendances et agrégats via Sportsgambler/TipMan; disponibilités rapportées par FotMob.
- Lacunes matérielles : séries brutes complètes et provenance méthodologique des agrégats non vérifiées; xG comparables indépendants non disponibles; compositions officielles, consignes d’équipes, repos exact et météo officielle non confirmés.
- Les moyennes de buts ne sont **pas** assimilées à des xG.

## 4. Analyse tactique et qualitative — EXÉCUTÉ — PARTIEL
| Facteur | Observation / statut | Preuve lue | Effet attendu sur Under 2.5 | Invalidation | Confiance |
|---|---|---|---|---|---|
| Volume récent / maîtrise de River | River est rapporté avec une possession élevée et 6,3 tirs cadrés moyens sur dix matchs de championnat; nature tactique précise NON ÉTABLIE. | Sportsgambler, publication 20 nov., page extraite; https://www.sportsgambler.com/betting-tips/football/river-plate-vs-lanus-prediction-lineups-odds-2026-11-22/ | S’OPPOSE légèrement : un volume élevé peut créer 3+ buts. | Conversion précoce de River. | Faible-moyenne (site affilié). |
| Défense / rythme de Lanús | Lanús est décrit avec six Under 2.5 consécutifs et une moyenne de 0,5 but encaissé sur dix; aucune organisation sans ballon effectivement documentée. | Scores24, publié 21 nov., page extraite; https://scores24.live/en/soccer/m-22-11-2026-river-plate-atletico-lanus-prediction | SOUTIENT indirectement un match fermé. | River force Lanús à sortir après un but. | Moyenne-faible (agrégateur). |
| Disponibilités | FotMob affiche Montiel suspendu et plusieurs joueurs River indisponibles/douteux; Canale et Romero indisponibles côté Lanús. Rôles/impact réel au coup d’envoi NON ÉTABLIS. | FotMob, date non affichée, page extraite le 22 nov.; https://www.fotmob.com/matches/river-plate-vs-lanus/3cz4g3 | NEUTRE : sens de l’effet non démontré. | Onze officiel différent. | Moyenne pour le statut, faible pour l’impact. |
| Pressing, construction, transitions, CPA, matchups | **NON ÉTABLI** : recherche tactique spécifique exécutée mais ne fournit pas de source récente exploitable et indépendante. | SearXNG, requête « River Plate Lanus tactical analysis pressing 2026 », 22 nov.; résultats surtout vidéo/pages inexploitables. | Aucun signal compté. | Sans objet. | Non évaluable. |

**Synthèse tactique :** Lanús peut soutenir un scénario sobre par ses tendances défensives rapportées, mais il n’existe pas de preuve tactique spécifique suffisante sur le pressing, les transitions ou les matchups. Le volume offensif rapporté de River est un contre-argument. Ce volet ne compte donc pas comme famille favorable indépendante.

## 5. Modèle quantitatif
- Baseline : Poisson indépendant, statut `baseline_uncalibrated`, `betting_eligible=false`, validation `not_validated`.
- Entrées vérifiées dans la source lue : River à domicile 1,53 but marqué / 0,89 encaissé; Lanús à l’extérieur 1,12 marqué / 1,00 encaissé; 10 matchs annoncés pour chaque split.
- Sortie : victoire River 42,3 %, nul 28,3 %, victoire Lanús 29,4 %; Under 2.5 **60,4 %**, BTTS Non 54,5 %.
- Limites : source tierce, force des adversaires/effet des absences non ajustés; indépendance des buts; baseline non validée. Probabilités non utilisables pour calculer une mise.

## 6. Marchés et prix
Relevé PropLine à 2026-11-22T14:30:45Z, plein match, règlement détaillé non fourni.
- 1X2 River : env. -152 à -192; nul +250 à +280; Lanús +467 à +500 selon bookmaker.
- Total 2,5 : Under environ -164 à -175 (décimal ~1,57–1,61); Over +115 à +135 (2,15–2,35).
- BTTS Non : exemples -154 à -182; BTTS Oui +100 à +125.
- Handicap : lignes disponibles, dont River -1 et Lanús +1, mais règlement exact de push non vérifié dans la réponse. Aucun handicap retenu.

## 7. Historique et structure du marché
- **SNAPSHOT SEUL.** Plusieurs bookmakers comparables et horodatés montrent la même zone de prix pour Under 2,5; les derniers changements affichés sont intrajournaliers mais pas une histoire d’ouverture fiable.
- La marge/no-vig exacte dépend du bookmaker. Exemple AdmiralBet : Under 2,5 -175 / Over +120 donne une probabilité no-vig approximative Under 61,3 %. Ce n’est pas une probabilité modèle.

## 8. Pourquoi ce prix maintenant
- Fait observé : les books convergent vers Under 2,5 favori et River favori net.
- Hypothèse prudente : le prix semble refléter les profils de buts bas rapportés et l’avantage domicile; l’intention du bookmaker est **INCONNUE**.
- Aucune justification d’un mouvement d’argent n’est avancée.

## 9. Matrice de convergence — Under 2,5
| Famille | Statut | Preuve / indépendance |
|---|---|---|
| Sport / performance / modèle | SOUTIENT, mais limité | tendances récentes et baseline 60,4 %, provenant en partie d’agrégateurs; modèle non validé. |
| Tactique / matchup / scénario | INDISPONIBLE | recherche exécutée, aucune preuve tactique spécifique suffisamment étayée. |
| Informations / disponibilité / conditions | NEUTRE | absences rapportées, mais onze et impact non établis. |
| Structure marché / prix | NEUTRE | prix réel frais et cohérent, mais snapshot seul, sans valeur démontrée. |

## 10. Cohérence
Cohérence **moyenne** : sources concordent sur un total bas et un match à élimination, mais les statistiques sont principalement des agrégats de sites tiers; aucune contradiction éliminée sur les effectifs. Pas de contradiction matérielle sur l’horaire, les participants ou les prix.

## 11. Alignement
Alignement **moyen** : Under 2,5 correspond bien à une rencontre supposée prudente et aux tendances de buts. Il reste fragile car le mécanisme tactique spécifique n’est pas établi et River possède le volume pour casser le total. Scénarios d’invalidation : but rapide, transition mal défendue, ou efficacité élevée de River.

## 12. Confiance
**Faible à moyenne.** Identité, heure et prix sont solides; preuves tactiques, compositions officielles et validation du modèle insuffisantes.

## 13. Edge / EV
**NON CALCULABLE.** La baseline est explicitement non validée et le prix/règlement pleinement comparable n’a pas été confirmé pour une EV. Aucune EV positive n’est établie.

## 14. Classement des marchés
1. Under 2,5 — lecture descriptive la plus cohérente, mais non admissible.
2. BTTS Non — prix plus court et mécanisme moins documenté.
3. River -1 — écart de scénario plus exigeant, non retenu.

## 15. Chemin décisionnel
Événement et crosswalk : satisfaits. Prix actuel : satisfaits. Deux familles indépendantes favorables : non satisfaites. Convergence : **FAIBLE**. Tactique étayée : non satisfaite. Edge/EV : non calculable. Règle moteur appliquée : **NO BET**.

## 16. Mise
**0 U.** Le modèle est non validé et aucune EV strictement positive n’est démontrée.

## 17. Verdict final
**NO BET — 0 U.**
- Marché observé : Under 2,5 buts, plein match, prix indicatif ~1,57–1,61.
- Motif : le scénario de faible total est plausible, mais convergence insuffisante : tactique spécifique non établie, absences/onces non confirmés et baseline non admissible à la mise.
- Risque majeur : le volume offensif de River et un but précoce peuvent invalider la lecture.
