# NODE.47 — Nashville SC vs FC Cincinnati
Pré-match, protocole V0.0.23. Capture de l’analyse : 2026-11-22 00:13 UTC.

## 1. Fiche événement
- Soccer, MLS (`usa.1`, registre ESPN vérifié et collecte activée).
- Nashville SC (domicile) – FC Cincinnati, Game 1 du premier tour Est des playoffs MLS, série au meilleur de trois.
- Coup d’envoi : 22 novembre 2026, 16 h ET / 21 h UTC ; GEODIS Park, Nashville.
- Règlement : pas de prolongation en cas d’égalité après 90 minutes ; tirs au but. Le marché 1X2 porte sur le temps réglementaire : le nul est une issue distincte et la sélection Nashville perd si le match est nul après 90 minutes.
- ESPN event ID transmis explicitement dans le crosswalk PropLine : `401933731`, mais fiche absente du dataset ESPN.
- PropLine : `sport_key=soccer_mls`, event `874119`; équipes et IDs d’équipes correspondants : Nashville `espn.soccer:18986`, Cincinnati `espn.soccer:18267`. Statut fournisseur `live=false`.

## 2. Journal des contrôles
| Contrôle | Résultat |
|---|---|
| `espn_health` | OK ; dernière collecte 2026-11-22 00:04:47.956 UTC ; âge 559 s, intervalle 900 s ; 830 événements. |
| `espn_competitions` | Catalogue soccer filtré sur `verified` et `collection_enabled=true` ; MLS `usa.1` vérifiée/activée. |
| `espn_coverage` | Route MLS `usa.1` : `ok`, 3 événements, collecte 00:04:47.956 UTC. Nashville–Cincinnati absent. |
| `espn_events` | Recherche MLS du 19 au 25 novembre : 3 événements, rencontre absente. |
| `espn_event_detail(401933731)` | Échec 404 : événement non trouvé dans le dataset collecté. |
| `searxng_health` | OK. Requêtes ciblées sur l’avant-match, le contexte tactique, les absences et les données saisonnières ; pages récupérées et lues pour MLS, FC Cincinnati et Cincinnati Soccer Talk. |
| PropLine health/sports | OK ; `soccer_mls` listé actif. |
| PropLine événement/marchés/cotes | Événement exact `874119`, crosswalk ESPN explicite, marchés découverts et cotes récupérées. Une requête avec `period=full_game` a été rejetée ; reprise sans période explicite, valeur renvoyée `null`. |
| `node47_report_save` | Première tentative rejetée : outil attend `sport=football`, pas `soccer`. Cette version est soumise avec le sport canonique. |

## 3. Données sportives et lacunes
**Disponibles :** identité via PropLine et MLS ; saison et format via MLS ; forme récente via pages MLS et médias de club. Nashville : 77 points, 23 victoires, 3 défaites ; à domicile 15V-0D-2N, 48 buts marqués, 14 encaissés et 8 clean sheets. Nashville a concédé 25 buts sur la saison ; Cincinnati 75. Le trio Mukhtar-Surridge-Espinoza a combiné 42 buts et 25 passes décisives. Cincinnati a battu Orlando 3-1 le 19 novembre ; Evander a signé 2 buts et 1 passe décisive. Nashville a battu Cincinnati 2-0 le 7 novembre.
**Absents ou incertains :** Cincinnati Soccer Talk rapporte Teenage Hadebe absent (jambe), Robinson et Hagglund disponibles malgré leur remplacement à la pause à Orlando ; ce remplacement ne prouve pas une blessure. Compositions officielles non disponibles à l’heure de capture. Nashville avait joué le 7 novembre (15 jours avant) et Cincinnati le 19 (3 jours avant). Une page officielle de Cincinnati parle de 22 jours de repos pour Nashville, incohérent avec les dates de matchs consultées ; 15 jours est le calcul cohérent du 7 au 22 novembre. Météo et état du terrain non vérifiés.
**Manquants :** fiche ESPN exacte et statistiques de cette fiche, xG/xGA comparables, splits domicile/extérieur complets, compositions confirmées et rapport médical officiel complet.

## 4. Analyse tactique et qualitative
**Statut : EXÉCUTÉ — PARTIEL.** Les sources étayent un matchup de forces et de faiblesses, pas des systèmes ou consignes spécifiques ; aucune formation, pression ou observation vidéo n’est inventée.

| Facteur / observation | Preuve, date et lecture | Effet / contre-argument | Confiance |
|---|---|---|---|
| Création de Nashville contre défense faible de Cincinnati : trio offensif à 42 buts et 25 passes combinés ; Cincinnati a concédé 75 buts | MLS, « 5 biggest storylines », page consultée (`fetch_status=ok`), publication non exposée, récupérée le 22 nov. [MLS](https://www.mlssoccer.com/playoffs/2026/news/nashville-sc-vs-fc-cincinnati-5-biggest-storylines-for-eastern-conference-round-one) | Soutient Nashville 1X2 ; agrégats saisonniers, ils ne décrivent pas les occasions exactes du match | Moyenne |
| Avantage domicile : Nashville invaincu à GEODIS Park (15-0-2), 48-14 en buts, 8 clean sheets | Même page MLS, consultée | Soutient l’hôte ; une pause de 15 jours peut aussi amener de la rouille et le format éliminatoire augmente la variance | Moyenne |
| Menace de transition de Cincinnati : Evander, 31 contributions de but en saison et 2 buts + 1 passe contre Orlando | Même page MLS et [compte rendu Cincinnati Soccer Talk](https://cincinnatisoccertalk.com/2026/11/19/for-fiona-fc-cincinnati-clinical-in-play-in-victory-over-orlando/), publié le 20 nov. 2026 04:03 UTC, page consultée | S’oppose à une victoire Nashville tenue pour acquise et à un handicap lourd ; Nashville n’a encaissé que 25 buts et a gagné 2-0 la dernière confrontation | Moyenne |
| Défense visiteuse et disponibilité : 75 buts encaissés ; Hadebe rapporté absent ; Robinson/Hagglund restent disponibles | [Cincinnati Soccer Talk, aperçu du 21 nov.](https://cincinnatisoccertalk.com/2026/11/21/fc-cincinnatis-tall-postseason-task-begins-at-nashville-sc/), page consultée, publication le 21 nov. à 18:41 UTC | Soutient Nashville si la défense manque de continuité ; disponibilité de Robinson/Hagglund réduit ce signal et aucun onze n’est confirmé | Faible à moyenne |
| Repos et gestion : Nashville depuis le 7 nov., Cincinnati depuis le 19 nov. ; coach Pat Noonan évoque la gestion des situations de match | [Avant-match officiel Cincinnati](https://www.fccincinnati.com/news/matchday-preview-presented-by-kiesland-fc-cincinnati-travel-to-nashville-for-round-one-opener-of-mls-cup-playoffs), page consultée, date de publication non exposée ; calendrier corroboré par MLS | Soutient préparation de Nashville ; la rouille est un contre-scénario ; le décompte « 22 jours » de l’article est incompatible avec les matchs consultés | Moyenne |
| Règlement/scénario | [Page officielle MLS Game 1](https://www.mlssoccer.com/playoffs/2026/news/nashville-sc-vs-fc-cincinnati-how-to-watch-stream-eastern-conference-round-one-game-1), page consultée : égalité à 90 min suivie de tirs au but, sans prolongation | Confirme que le nul reste une issue distincte sur le 1X2 ; la sélection Nashville ne couvre pas la séance | Élevée |

**Synthèse :** avantage de saison, création et terrain favorisent Nashville ; Evander et la récente performance de Cincinnati rendent risquée une lecture de victoire facile. Les mécanismes ne sont documentés qu’au niveau des performances/du matchup, pas du système tactique détaillé.

## 5. Modèle quantitatif
**MODÈLE NON VALIDABLE.** Pas de Poisson ni de probabilité modèle : données ESPN exactes absentes, splits/xG comparables incomplets, compositions et disponibilités non confirmées. Les seuls totaux de saison ne suffisent pas pour construire des intensités de buts fiables pour ce match de playoffs.

## 6. Marchés et prix
Snapshots PropLine, période renvoyée `null`, relevés avant le coup d’envoi. Cotes américaines et conversion décimale :

| Opérateur | Marché / issue | Cote | Décimale | Mise à jour |
|---|---|---:|---:|---|
| Pinnacle | 1X2 Nashville | -195 | 1,513 | 22 nov. 00:11:55 UTC |
| Pinnacle | 1X2 nul | +372 | 4,720 | 22 nov. 00:11:55 UTC |
| Pinnacle | 1X2 Cincinnati | +493 | 5,930 | 22 nov. 00:11:55 UTC |
| DraftKings | 1X2 Nashville | -215 | 1,465 | 22 nov. 00:11:49 UTC |
| DraftKings | 1X2 nul | +360 | 4,600 | 22 nov. 00:11:49 UTC |
| DraftKings | 1X2 Cincinnati | +450 | 5,500 | 22 nov. 00:11:49 UTC |
| Pinnacle | Total principal : plus/moins 3,25 | -119 / +104 | 1,840 / 2,040 | 22 nov. 00:11:55 UTC |
| Pinnacle | BTTS oui/non | -187 / +155 | 1,535 / 2,550 | 22 nov. 00:11:55 UTC |

Les lignes de total varient : DraftKings listait 3,5 à +100/-125 ; BetOnline.ag 3,5 à -108/-118 (snapshot vers 00:12:16 UTC). Elles ne sont pas assimilées à la ligne 3,25 Pinnacle.

## 7. Historique et structure du marché
**SNAPSHOT SEUL.** Plusieurs opérateurs favorisent Nashville. Fourchette observée dans les snapshots pour Nashville : environ -192 à -270 selon opérateur. Pas d’ouverture, de trajectoire historique, de limites ni de liquidité accessibles. No-vig calculé uniquement sur les trois issues d’une même capture : Pinnacle, Nashville 63,4 %, nul 20,3 %, Cincinnati 16,2 % ; DraftKings, environ 63,1 %, 20,1 %, 16,8 %. Ces probabilités reflètent le marché, pas un modèle NODE.47.

## 8. Pourquoi ce prix maintenant
Explication **PLAUSIBLE mais incomplète** : tête de série, record de 77 points, invincibilité à domicile et faiblesse défensive de Cincinnati concordent avec la faveur de Nashville ; le repos relatif est aussi pertinent. Sans cote d’ouverture ni historique, aucune cause de mouvement n’est établie et aucune intention, mise ou exposition du bookmaker n’est supposée.

## 9. Convergence — Nashville 1X2 temps réglementaire
| Famille | Statut | Éléments / réserve |
|---|---|---|
| Sport / performance / modèle | SOUTIENT | Classement, défense et bilan à domicile ; pas de probabilité modèle |
| Tactique / matchup / scénario | SOUTIENT, limité | Création de Nashville contre défense vulnérable ; Evander est une menace opposée ; pas de preuve détaillée des systèmes |
| Informations / disponibilité / conditions | SOUTIENT partiellement | Repos favorable à Nashville ; Hadebe absent selon média local ; statuts d’autres défenseurs et onze incertains |
| Structure du marché / prix | SOUTIENT | Plusieurs opérateurs cotent Nashville favori ; snapshot seul |

Convergence **PARTIELLE**, malgré la direction cohérente, car le soutien tactique est indirect, la fiche ESPN manque et l’Edge n’est pas estimable.

## 10. Cohérence
- Chronologie : snapshots du 22 nov. vers 00:12 UTC, avant le coup d’envoi de 21:00 UTC ; sources d’avant-match datées surtout des 20–21 nov.
- Données : statistiques MLS et résultats antérieurs cohérents avec le favori, sans valeur de probabilité propre.
- Repos : 15 jours du match du 7 au match du 22, non 22 jours ; la divergence source est signalée.
- ESPN : route opérationnelle mais événement omis, détail 404 ; ID exact fourni par crosswalk PropLine.
- Règlement : marché 1X2 à trois issues et tirs au but après match nul réglementaire sont compatibles.
- Causalité : contexte explique la faveur, mais pas un mouvement de prix.
**Cohérence globale : MOYENNE.**

## 11. Alignement
**MOYEN à FORT.** L’issue Nashville en 90 minutes correspond à son avantage saisonnier, à son rendement à domicile et à l’écart défensif. Le nul reste un risque central ; Evander, le court repos visiteur et le caractère éliminatoire empêchent un alignement fort sans réserve. Le règlement écarte les tirs au but du résultat 1X2 retenu.

## 12. Confiance
**MOYENNE.** Statistiques et règlement officiels MLS, actualités de club/média local lues, prix multi-opérateurs récents. Réductions : événement ESPN absent, xG et lineups manquants, informations physiques partielles, contradiction de repos, pas d’historique des prix.

## 13. Edge / EV
**NON CALCULABLE.** Aucun modèle validé aligné sur le marché, la ligne et le règlement. Les probabilités no-vig sont des prix de marché, non un Edge indépendant.

## 14. Classement des marchés
1. Nashville 1X2 temps réglementaire : meilleur candidat par convergence sport, domicile et prix ; risque principal, le nul.
2. Total de buts : non retenu ; lignes principales 3,25/3,5 variables et prix partagés, pas de modèle de buts.
3. BTTS : non retenu ; le marché penche vers Oui, mais la défense de Nashville et les deux confrontations sans but de Cincinnati donnent un scénario contraire non résolu.

## 15. Chemin décisionnel
Événement/participants identifiés par crosswalk explicite et pages MLS ; marché 1X2, issue, prix et règlement définis ; plusieurs familles indépendantes évaluables ; tactique réellement exécutée mais partielle ; convergence partielle ; cohérence et alignement au moins moyens ; confiance moyenne ; explication plausible, historique signalé SNAPSHOT SEUL. Application du moteur unique : **BET PRUDENT**. L’absence d’Edge calculable n’est pas interprétée comme un Edge négatif.

## 16. Mise
**NON DÉTERMINÉE PAR LE MOTEUR.** Pas de mise chiffrée ni de Kelly sans modèle validé et politique d’exposition.

## 17. Verdict final
**BET PRUDENT — Nashville SC gagne en 90 minutes (1X2).** Prix de référence observé : Pinnacle -195 (1,513), DraftKings -215 (1,465), snapshots du 22 nov. vers 00:12 UTC. La supériorité de saison et à domicile, le différentiel défensif et le repos soutiennent l’hôte. Risque majeur : nul après 90 minutes, notamment face à la forme d’Evander et à l’aléa des playoffs. La séance de tirs au but ne compte pas pour cette sélection. Mise non déterminée.

## Sources principales consultées
- MLS, Game 1, horaire, lieu et règles : https://www.mlssoccer.com/playoffs/2026/news/nashville-sc-vs-fc-cincinnati-how-to-watch-stream-eastern-conference-round-one-game-1
- MLS, cinq axes de matchup et chiffres saisonniers : https://www.mlssoccer.com/playoffs/2026/news/nashville-sc-vs-fc-cincinnati-5-biggest-storylines-for-eastern-conference-round-one
- FC Cincinnati, avant-match et repos : https://www.fccincinnati.com/news/matchday-preview-presented-by-kiesland-fc-cincinnati-travel-to-nashville-for-round-one-opener-of-mls-cup-playoffs
- Cincinnati Soccer Talk, aperçu et disponibilités rapportées, 21 nov. : https://cincinnatisoccertalk.com/2026/11/21/fc-cincinnatis-tall-postseason-task-begins-at-nashville-sc/
- Cincinnati Soccer Talk, compte rendu Orlando, 19 nov. : https://cincinnatisoccertalk.com/2026/11/19/for-fiona-fc-cincinnati-clinical-in-play-in-victory-over-orlando/
