# NODE.47 — Rapport d'analyse : Norwich City vs Cardiff City (Championship, 21/11/2026)

Version moteur : node47-core V0.0.23 / node47-decision-engine V0.0.21. Rapport factuel, audit trail (pas de chaîne de pensée privée). Analyse réalisée le 2026-11-21 avant le coup d'envoi (collecte des cotes PropLine à ~08:24 UTC).

---

## 1. Fiche événement

| Champ | Valeur |
|---|---|
| Sport (ESPN) | soccer |
| Compétition | English League Championship — `competition_id` ESPN = `eng.2` |
| Tour | Journée 16 de Championship (source : Goal.com, page lue) |
| Rencontre | Norwich City (domicile, ESPN team id 381) vs Cardiff City (extérieur, id 347) |
| Date / heure | 2026-11-21 12:30 UTC (= 12:30 GMT, heure de Norwich) |
| Lieu | Carrow Road, Norwich |
| Statut ESPN | `pre` / STATUS_SCHEDULED (non commencé), `quality_flags` = [] |
| ID événement ESPN | `401880155` |
| ID événement PropLine | `720671` (sport_key `soccer_championship`) |
| Crosswalk | Non ambigu : `espn_event_id` explicite = 401880155 dans PropLine ; participants (Norwich / Cardiff) et heure UTC identiques |
| Statut registre ESPN | `eng.2` : verified, collection_enabled = true, last_verified 2026-11-19 |
| Couverture ESPN | route `eng.2` : ok, 11 événements, collecte 2026-11-21T08:16:23Z |

---

## 2. Journal des contrôles

| # | Étape | Outil | Résultat |
|---|---|---|---|
| 1 | Lecture des protocoles | node47-core, football, espn-catalog, data-integration, tactical-qualitative, decision-engine | Lus |
| 2 | Santé ESPN | `espn_health` | status ok, v0.0.16, last_refresh 2026-11-21T08:16:23Z, âge 474 s, 838 événements |
| 3 | Catalogue ESPN | `espn_competitions` (sport=soccer, status=verified, collection_enabled=true) | 220 entrées soccer retournées (registry v0.0.5, généré 2026-11-19T10:30:10Z). Seul ce filtre a été parcouru (pas les 237 entrées multisport). `eng.2` sélectionné par ID exact |
| 4 | Couverture ESPN | `espn_coverage` | 237 routes, toutes `ok` ; `eng.2` ok |
| 5 | Événements | `espn_events` (league=eng.2, 2026-11-19→2026-11-30) | 11 événements ; Cardiff City at Norwich City = 401880155 |
| 6 | Détail événement | `espn_event_detail` 401880155 | Confirmé (pré-match, Carrow Road) |
| 7 | Santé SearXNG | `searxng_health` | ok (GitHub Actions) |
| 8 | Recherches web | `searxng_search` ×7 (fetch_pages=true) | Voir §3. Moteurs non répondants à chaque requête : duckduckgo (CAPTCHA), reuters (HTTP error) |
| 9 | Santé PropLine | `propline_health` | ok ; clé `soccer_championship` active ; fraîcheur bookmakers < 30 min |
| 10 | Événements PropLine | `propline_module_events` (football, soccer_championship) | Événement 720671 retrouvé, crosswalk non ambigu |
| 11 | Marchés de l'événement | `propline_module_event_markets` | 35 marchés disponibles (h2h, spreads, totals, BTTS, corners, cartes, joueurs…) |
| 12 | Cotes | `propline_module_event_odds` (h2h, totals, spreads, both_teams_to_score) | 95 bookmakers ; `last_update` événement 2026-11-21T08:24:12Z |
| 13 | Calculs | Python (no-vig, dispersion inter-books, inversion de Poisson des totaux d'équipe Pinnacle) | Exécutés (lectures de marché uniquement) |

Pages non lisibles (limites documentées, pas des preuves négatives) : WhoScored (http_403, extrait seul), DAZN (http_403), Oddschecker (http_403), site officiel Cardiff (limited_text, vide), Facebook (limited_text), MSN (limited_text), BBC live Bristol City–Norwich (page_too_large).

---

## 3. Données sportives et audit des lacunes

### 3.1 Sources consultées (statut de lecture)

| ID | Source / titre | Date | Lecture | Contenu utile |
|---|---|---|---|---|
| S1 | BBC Sport « Pick of the stats: Norwich City v Cardiff City » (Opta) https://www.bbc.com/sport/football/articles/cwr5g35z2dy0o | 2026-11-19 | Page lue (page_content) | Norwich : 4 victoires de suite avec ≥3 buts à chaque match (15 buts), après 5 défaites ; Cardiff 14e, 2 points en 7 matchs à l'extérieur ; Norwich a gagné 10 des 14 confrontations de championnat depuis 2013-14 ; Cardiff n'a gagné que 3 de ses 30 déplacements à Norwich ; Cardiff a encaissé 3+ buts lors de ses 3 derniers matchs de championnat (3-3 West Ham, 5-4 Burnley, + Wolves) |
| S2 | Yahoo/Hayters TV « Clement provides positive Norwich City fitness updates… » https://sports.yahoo.com/articles/clement-provides-positive-norwich-city-154000162.html | 2026-11-20 15:40 UTC | Page lue | Topić, Crnac, McLean, Mattsson, Yongwa à l'entraînement ; pas de nouveau blessé ; Yongwa apte ; Papa Diallo encore absent |
| S3 | Yahoo/Hayters TV « Barry-Murphy gives fresh updates… » https://sports.yahoo.com/articles/barry-murphy-gives-fresh-updates-161200194.html | 2026-11-20 16:12 UTC | Page lue | Lawlor, Osho, Chambers absents ; Davies (ischio) encore 3-4 semaines |
| S4 | WalesOnline « Barry-Murphy reveals Cardiff City injury latest… » https://www.walesonline.co.uk/sport/football/football-news/brian-barry-murphy-reveals-cardiff-34934801 | 2026-11-19 11:00 UTC | Page lue | Mêmes absents ; Robertson, Ng, Fish « proches » du retour (Fish jugé apte) ; Callum Robinson écarté des 5 derniers groupes ; objectif première victoire à l'extérieur, approche offensive maintenue |
| S5 | The72 via Yahoo UK « Norwich City team news and predicted XI… » https://uk.sports.yahoo.com/news/norwich-city-team-news-predicted-142401244.html | 2026-11-20 14:24 UTC | Page lue | Norwich 12e, 21 pts/15 matchs ; Touré (épaule) de retour vers le début de l'année, Ahmed (LCA) longue durée, Diallo absent ; McLean apte ; XI probable 4-2-3-1 : Grimshaw ; Stacey, Darling, McConville, Chrisene ; Field, Wright ; Brooks, Maghoma, Musaba ; Kvistgaarden ; 2 clean sheets d'affilée ; défense « parfois friable » |
| S6 | SportsGambler preview https://www.sportsgambler.com/betting-tips/football/norwich-vs-cardiff-prediction-lineups-odds-2026-11-21/ | publié 2026-11-19 10:57 | Page lue (tiers, affiliée) | Tableau : Norwich 12e 7V-0N-8D, 32-24 ; Cardiff 14e 4V-6N-5D, 27-27 ; 10 derniers matchs : Norwich 2,4 buts marqués / 1,6 encaissés ; Cardiff 2,1 / 1,8, 57,4 % de possession ; XI probable Cardiff 4-2-3-1 (Trott ; Ng, Fish, Bielik, Scanlon ; Robertson, Colwill ; Tanner, Moylan, Willock ; Salech) |
| S7 | BetBrain preview https://www.betbrain.com/football-predictions/norwich-city-vs-cardiff-city-fc-championship-21-11-2026 | métadonnée 2026-11-07 (contenu mis à jour ultérieurement) | Page lue (tiers, affiliée) | Liste des 5 dernières confrontations et des 5 derniers résultats de chaque équipe (scores utilisés après vérification arithmétique) ; texte narratif internement contradictoire (voir §10) |
| S8 | Evening News / Ben Lee « tactical analysis of Watford win » https://www.eveningnews24.co.uk/sport/26693035.norwich-city-ben-lee-tactical-analysis-watford-win/ | match du 2026-10-31 | Page lue | Norwich en 4-2-3-1 habituel ; constructions 2-3-5 ; vulnérabilités en transition défensive (rest defence à 2 axiaux, parfois 2-1) ; contre-pressing déterminant ; Kvistgaarden décisif dans les duels et passes vers la dernière ligne |
| S9 | Evening News « Derby 0-4 Norwich City : Clement » | 2026-11-03/04 | Page lue | Premier clean sheet depuis mars 2026 à Derby |
| S10 | Yahoo/FromTheSpot « Bristol City look to fix home form against Norwich » | 2026-11-06 | Page lue | Touré blessé depuis septembre (épaule), retour attendu en janvier |
| S11 | WhoScored preview | ~2026-11-21 | Extrait seul (http_403) | Extrait : Salech probable titulaire après son doublé ; Bagan purge un match de suspension (phrase tronquée) — NON LU |
| S12 | ScoreGPT (agrégateur de prédictions IA) | 2026-11-20 | Page lue | Opinions de modèles IA : NON utilisées comme preuve. Affirmations factuelles (Cardiff 6 buts en 7 déplacements ; défaites à domicile de Norwich contre Portsmouth et Southampton ; Bagan suspendu « probable mais non confirmé ») = tiers non corroboré |
| S13 | BBC Sport page Cardiff City | 2026-11-19 | Page lue | 14e, une seule défaite sur les 6 derniers matchs de championnat ; Bielik apte à jouer en défense ou au milieu ; commentaires de supporters (non retenus comme preuve) |
| S14 | Goal.com « Norwich City vs Cardiff City: TV channel… » | 2026-11-20 | Page lue (générique, assistée) | Contexte : journée 16, Norwich gagne 4 de ses 5 derniers, 5-0 à Bristol City ; Cardiff 5-4 Burnley ; Norwich 12e, Cardiff 14e |

Résultats récents recoupés (S7, scores vérifiés cohérents avec S1 et S5) :
- Norwich : 5-0 à Bristol City (07/11), 4-0 à Derby (03/11), 3-2 Watford (31/10), 3-1 à Charlton (24/10), 0-1 Portsmouth à domicile (17/10).
- Cardiff : 5-4 Burnley à domicile (07/11), 3-3 West Ham à domicile (04/11), 0-3 à Wolves (31/10), 1-0 Birmingham (24/10), 2-2 à Middlesbrough (17/10).
- 5 dernières confrontations (S7) : 25/08/2026 Cardiff 1-2 Norwich (EFL Cup), 03/05/2025 Norwich 4-2, 02/11/2024 Cardiff 2-1 Norwich, 17/02/2024 Norwich 4-1, 11/11/2023 Cardiff 2-3 Norwich. Les 5 ont produit ≥3 buts (moyenne 4,4 buts) et BTTS = oui (vérifié sur les scores listés).

### 3.2 Matrice des lacunes

| Variable | Statut | Note |
|---|---|---|
| Identité, statut, horaire, stade | Disponible | ESPN + PropLine |
| Forme récente, résultats, buts | Disponible (S1, S7) | Primaire partiel (Opta/BBC) + tiers |
| Statistiques domicile/extérieur détaillées | Partiel | Norwich domicile : 13 buts en 7 matchs et moyenne 3,57 buts/match (S7, tiers non recoupé). Cardiff extérieur : 2 points en 7 matchs (S1 confirmé) ; « 6 buts en 7 » (S12, non confirmé) |
| xG / xGA saison | INDISPONIBLE | Seul un xG isolé (Norwich–Watford, S8) |
| Absences Norwich | Disponible (S2, S5, S10) | Touré, Ahmed, Diallo ; McLean de retour |
| Absences Cardiff | Disponible (S3, S4) | Osho, Lawlor, Chambers, Davies ; Ng/Robertson incertains ; Fish apte |
| Suspension Bagan (Cardiff) | NON CONFIRMÉE | Extrait tronqué WhoScored (S11) + tiers (S12) ; non lue à la source |
| Compositions officielles | NON DISPONIBLE | Publiées vers 11:30 UTC ; seuls des XI probables existent (S5, S6) |
| Analyse tactique détaillée de Cardiff | NON ÉTABLI | Pas d'analyse tactique primaire trouvée ; seulement possession moyenne (S6), formation 4-2-3-1 probable (S6/S7), « approche offensive agressive » (S4) |
| Arbitre | NON ÉTABLI | Non recherché : non critique pour 1X2/AH/totaux/BTTS (critique pour cartons, hors périmètre) |
| Météo / terrain | NON ÉTABLI | Non recherché |
| Historique de cotes (ouverture/trajectoire) | INDISPONIBLE | Voir §7 |

---

## 4. Analyse tactique et qualitative

Statut : **EXÉCUTÉ — PARTIEL** (preuves tactiques directes sur Norwich ; preuves tactiques sur Cardiff indirectes ; compositions non confirmées).

### 4.1 Mécanismes retenus
1. Norwich (4-2-3-1) construit patiemment puis attaque verticalement vers Kvistgaarden/Musaba/Maghoma ; sa dernière série (15 buts, ≥3 buts par match) en est la trace statistique (S1, S5, S8).
2. La charnière de Cardiff est amputée (Osho, Lawlor, Chambers absents ; Bagan à confirmer ; Bielik/Fish probables). Cardiff a encaissé 3+ buts dans ses 3 derniers matchs (S1).
3. Réciproquement, Norwich est vulnérable en transition défensive (S8) et a connu des matchs ouverts (3-2 Watford). Cardiff joue haut en possession (57 % sur 10 matchs, S6), presse et attaque (S4, S7), avec Moylan, Salech, Willock, Colwill.
4. Contre-poids : Cardiff n'a pris que 2 points en 7 déplacements (S1) et a perdu 0-3 à Wolves lors du dernier déplacement (S7) ; Norwich a perdu 0-1 à domicile contre Portsmouth le 17/10 (S7).

### 4.2 Matrice tactique/qualitative — marché candidat A : Total buts, Plus de 2,5

| Facteur | Observation | Preuve / URL | Date | Lecture | Effet sur le marché | Contre-argument | Confiance |
|---|---|---|---|---|---|---|---|
| Attaque verticale de Norwich | 15 buts en 4 victoires, ≥3 buts à chaque fois | S1 (BBC/Opta) | 19/11 | Page lue | Soutient ≥3 buts | Touré (meilleur buteur) absent ; sample de 4 matchs | Moyenne-élevée |
| Défense de Cardiff amoindrie | 3 axiaux absents ; 3+ buts encaissés ×3 | S1, S3, S4 | 19-20/11 | Pages lues | Soutient ≥3 buts | Composition réelle inconnue ; Bielik/Fish probables | Moyenne |
| Transitions de Norwich | Rest defence fragile, 2 clean sheets récents seulement | S8, S5, S9 | 31/10-20/11 | Pages lues | Ouvre le jeu des deux côtés | Source tactique unique, match du 31/10 ; 2 clean sheets récents | Faible-moyenne (fragile) |
| Style de Cardiff | Possession haute, pressing, approche offensive ; matchs à 9, 6 buts à domicile | S4, S6, S7, S1 | 19/11 | Pages lues (tiers) | Soutient matchs ouverts | À l'extérieur, peu prolifique (0-3 Wolves ; 2 pts/7) | Moyenne |
| Historique direct | 5/5 dernières rencontres ≥3 buts | S7 (scores vérifiés) | — | Page lue (tiers) | Soutient | Échantillon de 5, rencontres à Carrow Road avec effectifs différents | Moyenne |
| Scénario d'invalidation | Norwich mène tôt 2-0 et gère, ou Cardiff peu efficace en déplacement (0-3 à Wolves) → ≤2 buts | S1, S7 | — | — | Fait basculer le marché | — | — |

### 4.3 Matrice — marché candidat B : Norwich handicap asiatique -0,75

| Facteur | Observation | Preuve | Effet | Contre-argument | Confiance |
|---|---|---|---|---|---|
| Écart de forme et d'effectif | Norwich 4 victoires ; Cardiff 2 pts/7 à l'extérieur, 3 axiaux absents | S1, S3, S5 | Soutient Norwich | Norwich : 0 nul en 15 matchs, volatil ; 0-1 à domicile vs Portsmouth | Moyenne |
| Bilan historique | Norwich 10 victoires sur 14 ; Cardiff 3/30 à Norwich | S1 | Soutient Norwich | Effectifs différents | Moyenne |
| Exigence de marge | -0,75 : victoire à +2 = gain complet ; à +1 = demi-gain | Règle du marché | Plus exigeant que 1X2 | Cardiff marque (5-4, 3-3 récents) ; Norwich a gagné 3-2 | — |

### 4.4 Matrice — marché candidat C : Les deux équipes marquent — Oui

| Facteur | Observation | Preuve | Effet | Contre-argument | Confiance |
|---|---|---|---|---|---|
| Historique BTTS | 5/5 dernières confrontations | S7 | Soutient | Échantillon | Moyenne |
| Défense de Norwich | 1,6 but encaissé/match sur 10 ; 2 clean sheets récents | S6, S9, S5 | Neutre | — | Faible-moyenne |
| Cardiff à l'extérieur | 2 pts/7 ; 0-3 à Wolves ; « 6 buts/7 » non confirmé | S1, S7, S12 | S'oppose en partie | Cardiff marque beaucoup à domicile | Moyenne |

### 4.5 Synthèse
- Mécanisme « matchs ouverts, Norwich supérieur en attaque face à une défense amoindrie » : **SOUTIENT** Plus de 2,5 (confiance moyenne), **NEUTRE** pour AH -0,75, **NEUTRE à S'OPPOSE partiel** pour BTTS Oui.
- Aucune formation, consigne ou duel individuel n'est affirmé sans source ; les XI sont des XI probables.

---

## 5. Modèle quantitatif

Statut : **MODÈLE NON VALIDABLE**. Raisons : pas de xG/xGA ni de tirs cadrés comparables sur la saison ; échantillons courts (4-7 matchs) ; splits domicile/extérieur uniquement via sources tierces non recoupées ; compositions non confirmées. Aucune probabilité « modèle » n'est produite.

**Lecture de marché (ce n'est PAS une probabilité modèle).** Inversion de Poisson des totaux d'équipe Pinnacle (no-vig) :
- Norwich : P(≥3 buts) no-vig = 38,2 % → espérance implicite ≈ 2,22 buts.
- Cardiff : P(≥2 buts) no-vig = 42,8 % → espérance implicite ≈ 1,46 but.
- Total implicite ≈ 3,68 buts ; P(total ≥3) ≈ 71,1 % (Pinnacle no-vig sur Plus de 2,5 : 70,9 %), P(total ≥4) ≈ 50,1 % (ligne principale 3,5 : 51,2 %). Les lignes sont donc internement cohérentes.

Éléments descriptifs (non validés comme modèle) : Norwich 10 derniers matchs 2,4 marqués / 1,6 encaissés ; Cardiff 2,1 / 1,8 (S6).

---

## 6. Marchés et prix

Prix PropLine, match complet (period = null), bookmaker de référence **Pinnacle** (`last_update` 2026-11-21T08:23:01Z ; `last_change_at` des issues 08:00–08:14 UTC), Betfair Exchange à titre de comparaison. Aucun marché suspendu retenu.

### 6.1 1X2 (h2h)

| Book | Norwich | Nul | Cardiff | Marge |
|---|---|---|---|---|
| Pinnacle | -126 (1,794) | +331 (4,31) | +312 (4,12) | 3,23 % |
| Betfair Ex. | -119 (1,84) | +340 (4,40) | +330 (4,30) | — |
| Pinnacle no-vig | 54,0 % | 22,5 % | 23,5 % | |

Dispersion « Norwich gagne » sur 93 books : 1,51–1,855, médiane 1,752.

### 6.2 Total de buts (Pinnacle)

| Ligne | Over | Under | No-vig Over |
|---|---|---|---|
| 1,5 | -985 (1,102) | +674 (7,74) | 87,5 % |
| **2,5** | **-282 (1,355)** | +230 (3,30) | **70,9 %** |
| 3,0 | -196 (1,51) | +167 (2,67) | 63,9 % |
| 3,25 | -142 (1,704) | +124 (2,24) | 56,8 % |
| **3,5 (ligne principale)** | -111 (1,901) | -101 (1,99) | 51,2 % |
| 3,75 | +111 (2,11) | -128 (1,781) | 45,8 % |
| 4,0 | +147 (2,47) | -171 (1,585) | 39,1 % |

Plus de 2,5 : Betfair Ex. 1,38 / Moins 3,45. Dispersion sur 77 books (Over 2,5) : 1,25–1,389, médiane 1,333 ; probabilité no-vig 67,9–72,2 %, médiane 69,7 %.

### 6.3 Handicap asiatique (Pinnacle)
Ligne principale : Norwich -0,75 à -101 (1,99) ; Cardiff +0,75 à -109 (1,917) (08:14 UTC). Alternatives : Norwich -0,5 à -127 (1,787) / Cardiff +0,5 à +113 ; Norwich -1,0 à +128 (2,28) / Cardiff +1,0 à -145 ; Norwich -1,25 à +157. Règlement -0,75 : victoire par 2+ buts = gain complet ; par 1 but = demi-gain ; nul/défaite = perte.

### 6.4 Les deux équipes marquent (BTTS)
Pinnacle : Oui -262 (1,382) / Non +218 (3,18) ; no-vig Oui 69,7 %. Betfair Ex. : Oui 1,429 / Non 3,20. Dispersion sur 74 books (Oui) : 1,20–1,429, médiane 1,364 ; no-vig 65,8–71,1 %, médiane 68,0 %.

### 6.5 Totaux d'équipe (Pinnacle)
Norwich Plus de 2,5 : +152 (2,52) / Moins -179 (1,559). Cardiff Plus de 1,5 : +125 (2,25) / Moins -146 (1,685).

Règlement : marchés « match complet » (period = null), temps réglementaire standard d'un match de championnat ; le texte de règlement propre à Pinnacle n'est pas fourni par l'API (limite mineure, voir §10).

---

## 7. Historique et structure du marché

**SNAPSHOT SEUL** pour PropLine : aucune ouverture ni trajectoire fournies. Seuls des `last_change_at` par issue existent (ex. Pinnacle 08:00–08:14 UTC), insuffisants pour reconstituer une trajectoire.

Instantanés tiers non comparables (bookmaker non précisé, horodatages différents) : SportsGambler (19/11 10:57) : Norwich -137 / Nul +320 / Cardiff +290, Over 2,5 -312, BTTS Oui -286, AH -0,75 à -115/-119 ; BetBrain (page datée du 07/11, contenu actualisé ensuite) : -125 / +330 / +300. Ils ne permettent **aucune conclusion de mouvement** (livres et horaires différents).

Structure : cohérence forte entre books (Over 2,5 entre 1,25 et 1,389 ; dispersion étroite) ; marge Pinnacle : 3,23 % (1X2), 4,13 % (Over/Under 2,5), 3,82 % (BTTS). Marché dominé par un scénario à ~3,7 buts attendus.

---

## 8. Pourquoi ce prix maintenant

- **Fait corroboré** : Norwich a marqué ≥3 buts à chacune de ses 4 victoires (S1) ; Cardiff a encaissé 3+ buts dans ses 3 derniers matchs de championnat (S1) ; Cardiff déplore trois défenseurs centraux absents (S3, S4) ; 5/5 dernières confrontations ≥3 buts (S7, scores vérifiés).
- **Hypothèse plausible** : le prix très court de Plus de 2,5 (~71 % no-vig) et la ligne principale à 3,5 reflètent ces séries et la fragilité défensive de Cardiff.
- **Explications alternatives** : l'information (blessés, séries) est publique et déjà intégrée par le marché ; absence de preuve que le marché sous-estime la probabilité.
- **Inconnues** : mises, exposition, motivation des bookmakers, mouvements depuis l'ouverture.

Statut de l'explication du prix : **PLAUSIBLE** (non corroborée par historique).

---

## 9. Matrice de convergence (par marché et direction)

| Famille | A. Plus de 2,5 buts | B. Norwich AH -0,75 | C. BTTS Oui |
|---|---|---|---|
| SPORT / PERFORMANCE / MODÈLE | SOUTIENT (S1, S7 ; séries de buts) | SOUTIENT (S1) | NEUTRE (historique BTTS 5/5 vs Cardiff peu prolifique à l'extérieur) |
| TACTIQUE / MATCHUP / SCÉNARIO | SOUTIENT — partiel, fragile (S8 un seul match ; S4) | NEUTRE (atouts de Norwich contre fragilités en transition) | SOUTIENT — fragile |
| INFORMATIONS / DISPONIBILITÉ / CONDITIONS | SOUTIENT — modéré (Cardiff sans 3 axiaux ; compos non confirmées) | SOUTIENT — modéré | NEUTRE |
| STRUCTURE DU MARCHÉ / PRIX | NEUTRE (prix cohérent mais court, snapshot seul, même information que les autres familles) | NEUTRE | NEUTRE |
| **Convergence** | **PARTIELLE** (3 familles, dégradée par fragilité tactique et indépendance limitée des sources) | **PARTIELLE** (2 familles) | **FAIBLE à PARTIELLE basse** |

Indépendance : les familles SPORT et INFO reposent sur des sources distinctes (statistiques Opta/BBC vs conférences de presse), la famille TACTIQUE repose sur une source unique (S8) plus des tiers dérivés (S4, S6, S7). Les prédictions d'IA (S12) et les « tips » de sites d'affiliation n'ont pas été comptés comme signaux. La famille marché n'est pas comptée comme soutien pour éviter le double comptage d'une information déjà intégrée aux prix.

---

## 10. Cohérence

Niveau : **MOYENNE**.
- Compatibles : séries de buts (S1), résultats (S7), absences (S3, S4, S5), prix (§5 : cohérence interne des lignes Pinnacle).
- Contradictions/limites : (a) BetBrain affirme dans son texte qu'un match « peu prolifique » est probable alors que ses propres chiffres et tips soutiennent Plus de 2,5 → source tierce à faible fiabilité ; (b) BetBrain indique « Cardiff a perdu ses 5 matchs à l'extérieur », alors que BBC/Opta indique 2 points en 7 déplacements (donc 2 nuls) → retenu : BBC ; (c) suspension de Bagan non confirmée ; (d) Cardiff peu prolifique à l'extérieur (0-3 à Wolves ; « 6 buts en 7 » non confirmé) vs profil général très offensif ; (e) règlement bookmaker non fourni par l'API ; (f) horodatages hétérogènes entre sources tierces.
- Aucune contradiction matérielle non résolue sur le marché retenu (Plus de 2,5), mais une contrepreuve réelle sur la capacité de Cardiff à marquer à l'extérieur.

---

## 11. Alignement

Niveau : **MOYEN**.
- Plus de 2,5 : le mécanisme (attaque verticale de Norwich contre défense de Cardiff amputée, jeu ouvert à domicile) se traduit directement par ≥3 buts ; ligne entière sans remboursement ; ne dépend pas d'un score exact. Lien plausible mais partiel (Cardiff doit ou non marquer, composition à confirmer).
- AH -0,75 : lien plausible mais plus exigeant (marge de 2 buts pour gain complet) ; alignement moyen à faible.
- BTTS Oui : dépend du fait que Cardiff marque à l'extérieur, point non établi → alignement faible à moyen.
- Scénarios d'invalidation (Plus de 2,5) : 1-0, 2-0, 1-1, 0-1, 0-2, 0-0 (par exemple Norwich contrôle sans marquer 3 fois, ou Cardiff stérile comme à Wolves).

---

## 12. Confiance

Niveau : **MOYENNE**.
- Fraîcheur : bonne (articles du 19-20/11, cotes du jour 08:24 UTC).
- Traçabilité : statistiques primaires (Opta via BBC) + conférences de presse reprises par des médias ; plusieurs sources tierces dérivées.
- Couverture : partielle (compositions officielles absentes, xG absent, suspension de Bagan non confirmée, tactique de Cardiff non documentée).
- Indépendance : limitée sur la famille tactique.

---

## 13. Edge / EV

**NON CALCULABLE** : modèle non validé (§5), donc aucun écart entre probabilité modèle et prix. Les probabilités no-vig sont des lectures de marché. Un Edge non calculable n'est pas converti en Edge négatif.

---

## 14. Classement des marchés

| Rang | Marché | Direction | Ligne | Convergence | Cohérence | Alignement | Statut |
|---|---|---|---|---|---|---|---|
| 1 | Total de buts | Plus de | 2,5 | PARTIELLE | MOYENNE | MOYEN | Candidat retenu |
| 2 | Handicap asiatique | Norwich | -0,75 | PARTIELLE | MOYENNE | MOYEN-FAIBLE | Non retenu (marge exigée, volatilité de Norwich à domicile : 0 nul en 15 matchs, défaite 0-1 vs Portsmouth) |
| 3 | BTTS | Oui | — | FAIBLE à PARTIELLE basse | MOYENNE | FAIBLE-MOYEN | Non retenu (dépend du scoring de Cardiff à l'extérieur) |

---

## 15. Chemin décisionnel (node47-decision-engine V0.0.21)

Préconditions :
- Événement et participants identifiés : OK.
- Marché, sélection, ligne exacts : OK (Total buts, Plus de 2,5, match complet).
- Prix actuel disponible et horodaté : OK (Pinnacle 08:23:01Z ; 77 books).
- Crosswalk non ambigu : OK.
- Au moins deux familles indépendantes évaluables : OK (SPORT et INFO indépendantes ; TACTIQUE partielle).
- Règlement : standard, texte bookmaker non fourni (limite mineure, période = match complet non ambiguë en championnat).

Critères :
- Convergence PARTIELLE ; pas FORTE → pas de BET.
- Cohérence MOYENNE (≥ moyenne) ; alignement MOYEN (≥ moyen) ; confiance MOYENNE (≥ moyenne) ; prix vérifié ; explication du prix PLAUSIBLE ; snapshot seul explicitement signalé ; aucune contradiction critique.
- Edge non calculable : n'est ni un veto ni un soutien.

Règle appliquée : **BET PRUDENT** (convergence partielle, cohérence/alignement/confiance ≥ moyens, prix vérifié, snapshot seul signalé).

---

## 16. Mise

**NON DÉTERMINÉE PAR LE MOTEUR** (aucune politique d'exposition définie ; modèle non validé donc Kelly inapplicable). Aucune mise inventée.

---

## 17. Verdict final

**BET PRUDENT**

- Marché : Total de buts (match complet), **Plus de 2,5**.
- Prix de référence : Pinnacle 1,355 (-282), capturé 2026-11-21T08:23:01Z ; fourchette inter-books 1,25–1,389 (77 books), médiane 1,333.
- Motif déterminant : séries de buts de Norwich (≥3 buts lors de ses 4 victoires), Cardiff avec 3+ buts encaissés lors de ses 3 derniers matchs et trois défenseurs centraux absents, 5/5 dernières confrontations à ≥3 buts ; mécanisme de match ouvert aligné avec la ligne.
- Risques : (1) prix court (~71 % no-vig) et information déjà intégrée par le marché ; Edge non calculable ; (2) Cardiff peu prolifique à l'extérieur (2 points en 7 déplacements, 0-3 à Wolves) ; (3) compositions non confirmées, suspension de Bagan non confirmée, Ng/Robertson incertains ; (4) snapshot seul, aucun historique de prix ; (5) tactique de Cardiff insuffisamment documentée.
- Données manquantes : compositions officielles (vers 11:30 UTC), xG, historique de cotes, texte de règlement du bookmaker, météo/terrain.
- Marchés non retenus : Norwich AH -0,75 et BTTS Oui (voir §14).
