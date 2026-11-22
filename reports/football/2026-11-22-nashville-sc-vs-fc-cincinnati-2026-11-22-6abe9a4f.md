# NODE.47 — Nashville SC vs FC Cincinnati
**Analyse complète — 22 novembre 2026 — Version de protocole 0.0.23**

## 1. Fiche événement
- Sport : football (soccer ESPN).
- Compétition : MLS — Audi 2026 MLS Cup Playoffs, Eastern Conference Round One, Game 1 (série au meilleur des trois).
- Participants : Nashville SC (domicile) vs FC Cincinnati.
- Date/heure : dimanche 22 novembre 2026, 16:00 ET / 21:00 UTC / 22:00 Africa/Douala.
- Lieu : GEODIS Park, Nashville, Tennessee.
- Statut à la collecte : programmé, pré-match.
- ESPN : compétition `usa.1`, statut du registre `verified`; couverture courante indiquée `ok` (3 événements collectés pour MLS), mais aucun événement correspondant dans le jeu collecté. L’ID ESPN communiqué par PropLine est `401933731`; `espn_event_detail` sur cet ID a renvoyé 404 « Event not found in the collected dataset ».
- PropLine : clé sport `soccer_mls`, ID événement `874119`, ID ESPN lié explicitement `401933731`. Le crosswalk fournisseur est univoque par l’ID explicite, malgré la lacune ESPN.
- Marché principal examiné : résultat 1X2 à 90 minutes (Nashville / nul / Cincinnati), sous réserve de confirmation de règlement par l’opérateur.

## 2. Journal des contrôles
- 2026-11-22 06:52 UTC environ — `espn_health`: OK; dernière actualisation 06:41:40 UTC, âge annoncé 655 s, intervalle 900 s.
- 2026-11-22 — `espn_competitions(sport=soccer,status=verified)`: 220 compétitions renvoyées; routage MLS `usa.1`.
- 2026-11-22 — `espn_coverage`: route MLS `ok`, trois événements; aucun Nashville–Cincinnati correspondant parmi les événements collectés.
- 2026-11-22 — `espn_events(soccer,usa.1,22 nov.–15 déc.)`: zéro événement.
- 2026-11-22 — `espn_event_detail(401933731)`: 404, absent du jeu collecté.
- 2026-11-22 — `propline_health`: OK et données de marché actives; fraîcheur variable par bookmaker.
- 2026-11-22 — `propline_sports`: clé MLS exacte `soccer_mls`.
- 2026-11-22 — `propline_module_events(football,soccer_mls)`: événement correspondant, horaire 21:00 UTC, événement ESPN lié.
- 2026-11-22 — `propline_module_event_markets(874119)`: marchés 1X2, spreads et totaux disponibles parmi les marchés listés.
- 2026-11-22 06:56:32 UTC — `propline_module_event_odds(874119,h2h,spreads,totals)`: prix observés; données de mouvement limitées aux timestamps de dernière modification, pas de série historique d’ouverture.
- 2026-11-22 — `searxng_health`: OK.
- 2026-11-22 — recherches SearXNG ciblées avec récupération de pages : page officielle MLS, aperçu officiel FC Cincinnati, pages officielles de club. Page content disponible pour MLS et FC Cincinnati.
- Limite : les pages retournées n’exposent pas de date de publication exploitable pour toutes les pages; heure de récupération consignée ci-dessus.

## 3. Données sportives et audit des lacunes
| Variable | État | Observation |
|---|---|---|
| Identité, horaire, lieu, format | Disponible et corroboré | MLS officiel et FC Cincinnati officiel; PropLine correspond |
| Classement/forme saisonnière | Partiellement disponible | MLS officiel décrit Nashville comme vainqueur du Supporters’ Shield avec 77 points; aperçu FCC indique 23-3-8 et Nashville premier à l’Est |
| Défense/attaque saisonnière | Partiellement disponible | MLS rapporte 25 buts encaissés par Nashville; Cincinnati a encaissé 75 selon l’aperçu MLS retourné |
| Matchs récents / H2H | Partiellement disponible | Cincinnati a gagné 3-1 à Orlando le 19 novembre selon MLS/FCC officiel; FCC dit que Nashville a gagné les deux rencontres régulières de 2026 |
| xG/xGA comparables, tirs/occasions ajustés | Indisponible dans les données ESPN récupérées | Pas de série complète fiable extraite |
| Compositions officielles, indisponibilités confirmées | Non établies à l’heure de capture | Le onze de départ n’est pas vérifié; informations d’effectif insuffisantes |
| Météo, état du terrain, arbitre | Indisponible / non requis pour le candidat principal | Pas de vérification exploitable |
| Prix, lignes et heures | Disponible partiellement | Cotes actuelles horodatées; ouverture/trajectoire complète et règles contractuelles indisponibles |

Les chiffres de saison soutiennent l’écart de profil, mais ils ne suffisent pas à construire un modèle de buts validé ni à isoler la performance à domicile/extérieur à niveau d’adversaires comparable.

## 4. Analyse tactique et qualitative
État : **EXÉCUTÉ — PARTIEL**, fondé sur des aperçus de match et de saison. Aucune formation, pressing précis ou duel individuel n’est inféré sans preuve.

| Facteur | Observation et preuve | Date / lecture | Effet possible sur 1X2 | Contre-argument / invalidation | Confiance |
|---|---|---|---|---|---|
| Solidité et avantage terrain de Nashville | L’aperçu MLS décrit Nashville comme champion du Supporters’ Shield, record de 77 points et seulement 25 buts encaissés; Cincinnati reconnaît l’avantage du terrain et la série de Nashville | Page MLS officielle lue (page content); aperçu FCC officiel lu; récupérés le 22 nov. | Soutient Nashville par capacité à limiter les occasions et imposer la pression à GEODIS Park | Match à élimination de série; avantage saisonnier ne garantit pas une victoire en 90 minutes; longue pause peut réduire le rythme | Moyenne |
| Vulnérabilité défensive de Cincinnati | MLS rapporte 75 buts concédés sur la saison par Cincinnati, parmi les plus hauts totaux de la ligue | Aperçu MLS lu; récupéré le 22 nov. | Soutient Nashville; expose l’arrière-garde aux séquences prolongées et aux erreurs | Peut être atténuée par un bloc plus bas et par la forme du gardien; donnée saisonnière agrégée | Moyenne |
| Transition et création de Cincinnati | En Wild Card, Cincinnati est revenu d’un retard pour gagner 3-1 à Orlando; Evander a inscrit un doublé et trois contributions au but selon l’article officiel du club | Récapitulatif FCC officiel extrait par SearXNG; page consultée | S’oppose à une confiance excessive sur Nashville et soutient la capacité de Cincinnati à punir les transitions | Orlando et Nashville ont des profils défensifs différents; réussite ponctuelle et fatigue possible | Moyenne |
| Repos / fraîcheur | L’aperçu FCC avance trois jours de repos pour Cincinnati et 22 jours pour Nashville; les chiffres exacts ne sont pas corroborés indépendamment et la séquence calendaire doit être vérifiée | Aperçu FCC officiel lu; récupéré le 22 nov. | Potentiellement soutien à Nashville en seconde période, mais pas utilisé comme signal décisif | Écart important de rythme : fraîcheur de Cincinnati contre rouille possible de Nashville; contradiction temporelle non résolue | Faible |
| H2H et confiance | FC Cincinnati rapporte que Nashville a remporté les deux duels de saison régulière 2026 | Aperçu FCC officiel lu; récupéré le 22 nov. | Soutient Nashville | Les scores détaillés ne sont pas repris ici faute de corroboration directe; les matchs précédents ne prédisent pas seuls le match | Faible à moyenne |

**Synthèse du mécanisme :** la meilleure hypothèse favorable à Nashville est que sa défense de saison et son avantage à domicile neutralisent la menace de transition de Cincinnati, dont la défense a concédé beaucoup. L’invalidation est une sortie rapide de Cincinnati, une nouvelle performance d’Evander, ou un nul après 90 minutes. Le règlement de la série prévoit une séance de tirs au but si le match est à égalité après le temps réglementaire, sans prolongation selon MLS; cela rend le 1X2 réglementaire distinct du qualifié.

## 5. Modèle quantitatif
**MODÈLE NON VALIDABLE.** Le modèle de buts de Poisson n’est pas calculé : pas de données comparables et vérifiées de xG/xGA, d’occasions récentes, de domicile/extérieur, de disponibilité et de gardiens permettant d’estimer les intensités. Aucune probabilité de modèle ni score projeté n’est inventé.

## 6. Marchés et prix
PropLine a retourné les marchés 1X2, spreads et totals. Les valeurs ci-dessous sont des exemples de prix courants extraits de captures; format original américain, conversion décimale locale uniquement.

- 1X2 — Nashville : environ -192 à -250 selon opérateur; exemple BetMGM -200 (décimal 1,50), capture bookmaker 06:50:21 UTC.
- 1X2 — nul : exemples +360 BetMGM; Cincinnati +425.
- Totaux : lignes principales variables selon opérateur (2,5 ou 3,5); par exemple AdmiralBet O/U 2,5 à -250 / +165, capture 06:51:28 UTC. Les lignes ne sont pas interchangeables.
- Spreads : par exemple Bet105 Nashville -1 à -124 / Cincinnati +1 à +108, capture 06:51:17 UTC.
- Période/règlement : champs période nuls dans le flux. La page MLS précise que le match nul après 90 minutes est départagé aux tirs au but; PropLine ne fournit pas le règlement complet de règlement du marché. Cette différence empêche de traiter le résultat du match et la qualification comme le même marché.
- Les prix sont des cotes observées et non des prévisions.

## 7. Historique et structure du marché
**SNAPSHOT SEUL** pour la trajectoire : dernières modifications horaires figurent dans certains enregistrements, mais aucune cote d’ouverture ni historique complet exploitable n’est fourni.
Les prix 1X2 disponibles dans une même capture varient, p. ex. Nashville -192 (Bet105) à -250 (AdmiralBet DE), et l’ensemble des issues varie également. Ceci confirme le statut de favori de Nashville mais ne constitue pas un mouvement directionnel. Pas de comparaison de lignes à règlement strictement équivalent pour les totaux à travers tous les bookmakers. Marge/no-vig calculable seulement sur un triplet de même bookmaker/capture : AdmiralBet autour de 06:51:28 UTC (-213 / +355 / +440) donne environ 62,7 % Nashville, 20,3 % nul, 17,1 % Cincinnati après normalisation. C’est une lecture de marché, pas une probabilité modèle.

## 8. Pourquoi ce prix maintenant
La cote courte de Nashville est compatible avec les données publiées : saison historique (77 points selon MLS), statut de tête de série, défense à 25 buts encaissés et terrain à domicile. Le club visiteur a concédé 75 buts selon l’aperçu MLS. Les prix de plusieurs opérateurs concordent sur le statut de favori.
- Statut de l’explication : **PLAUSIBLE**, non corroborée au sens strict du mouvement de prix.
- Explications alternatives : le marché peut intégrer le terrain, la forme saisonnière, les confrontations 2026 ou des informations d’effectif non accessibles dans ce flux.
- Inconnues : ouverture, séquence de mouvements complète, limites/liquidité, compositions officielles, exposition des opérateurs et règlement exact du marché.
- Ne pas attribuer le mouvement à des mises ou à une intention du bookmaker.

## 9. Matrice de convergence par marché et direction
Candidat : **Nashville 1X2 (90 minutes)**.

| Famille | Statut | Preuve / indépendance |
|---|---|---|
| SPORT / PERFORMANCE / MODÈLE | SOUTIENT partiellement | Avantage saisonnier Nashville (77 points, défense à 25 buts) et vulnérabilité de Cincinnati rapportée par MLS; modèle quantitatif indisponible |
| TACTIQUE / MATCHUP / SCÉNARIO | SOUTIENT partiellement | Mécanisme défensif domicile contre défense de Cincinnati, mais menace de transition d’Evander et conditions de repos incertaines |
| INFORMATIONS / DISPONIBILITÉ / CONDITIONS | INDISPONIBLE | Onze et absences confirmés absents; repos discordant |
| STRUCTURE DU MARCHÉ / PRIX | SOUTIENT Nashville | Favori dans les captures multi-bookmakers; snapshot et explication du prix seulement plausibles |

Convergence qualitative : **PARTIELLE**. Les signaux marché et performance ne compensent pas les inconnues de règlement et de disponibilité pour produire un pari autorisable.

## 10. Cohérence
- Événement et date : concordance entre MLS officiel, FC Cincinnati officiel et PropLine.
- Identité ESPN : incohérence opérationnelle limitée; PropLine rattache l’événement à un ID ESPN mais détail ESPN renvoie 404 et son collecteur n’a pas l’événement.
- Calendrier/repos : chiffre de 22 jours annoncé par l’aperçu FCC, non confirmé indépendamment et possiblement discordant avec les autres éléments de calendrier consultés; poids réduit.
- Statistiques : données saisonnières proviennent de pages de prévisualisation; elles sont cohérentes en ordre de grandeur mais insuffisantes à un modèle.
- Marché : captures et prix disponibles; lignes, opérateurs et timestamps varient. Aucun historique d’ouverture.
- Règlement : format des playoffs explicité par MLS; règles de règlement des prix PropLine non exposées.

## 11. Alignement
L’avantage domicile et la qualité défensive de Nashville s’alignent raisonnablement avec une victoire en 90 minutes, tandis que les concessions de Cincinnati offrent un mécanisme adverse plausible. Alignement **MOYEN**. Il faut distinguer victoire en temps réglementaire, nul après 90 minutes et qualification aux tirs au but. Une sélection « Nashville qualifié » n’a pas été vérifiée comme marché offert; elle ne doit pas être substituée au 1X2.

## 12. Confiance
**MOYENNE pour l’identité et le contexte de match; FAIBLE à MOYENNE pour un pari.** Horaire et affiche confirmés par les clubs/ligue. Statistiques saisonnières et match récent disponibles par sources officielles. Confiance de pari réduite par l’événement ESPN absent, les compositions/absences non confirmées, l’écart de repos non résolu, l’absence de modèle validable et le règlement fournisseur non exposé.

## 13. Edge / EV
**NON CALCULABLE.** Aucun modèle de buts validé; le no-vig est une mesure de marché et ne peut pas être utilisé comme probabilité prédictive.

## 14. Classement des marchés
1. Nashville 1X2 — meilleur candidat directionnel descriptif, mais pas validé pour miser.
2. Nashville -1 / -1,25 — trop dépendant de la marge de victoire et des prix/règlements spécifiques; modèle absent.
3. Total buts — signaux non convergents; marché et lignes variables, modèles de buts absents.
Aucun candidat ne satisfait toutes les préconditions décisionnelles.

## 15. Chemin décisionnel
- Événement confirmé par source primaire : oui.
- Marché et prix courant : oui, mais détail de période/règlement incomplet.
- Crosswalk PropLine : oui par identifiant ESPN explicite.
- Données suffisantes sur deux familles : oui pour une analyse descriptive.
- Analyse tactique effectuée : partielle, avec contre-scénarios.
- Convergence forte sans contradiction : non.
- Modèle/Edge valide : non.
- Précondition du règlement fournisseur : non satisfaite.
Application du moteur central : **NO BET**.

## 16. Mise
**NO BET = 0 U.** Mise non déterminée par le moteur.

## 17. Verdict final
**NO BET** — aucun pari recommandé.
Lecture sportive : Nashville est le favori logique en temps réglementaire au vu de la saison, de la défense et du terrain; Cincinnati reste dangereux après sa victoire 3-1 à Orlando. La cote observée reflète déjà largement le statut de Nashville et aucune probabilité indépendante ne permet de justifier un avantage de prix.
Risque majeur : Cincinnati peut profiter d’une transition ou d’une baisse de rythme de Nashville; un nul après 90 minutes mène aux tirs au but pour la série. Le prix PropLine n’expose pas son règlement exact et l’événement ESPN lié est absent du jeu collecté.
Données manquantes déterminantes : règlement bookmaker précis, onze/absences officiels, statistiques d’occasions/xG comparables et historique complet du prix.

### Sources et traçabilité
- Major League Soccer, « Nashville SC vs. FC Cincinnati: How to watch, stream Eastern Conference Round One Game 1 », page consultée le 22 nov. 2026, récupération SearXNG, contenu extrait : https://www.mlssoccer.com/playoffs/2026/news/nashville-sc-vs-fc-cincinnati-how-to-watch-stream-eastern-conference-round-one-game-1
- FC Cincinnati, « MATCHDAY PREVIEW presented by Kiesland | FC Cincinnati travel to Nashville for Round One opener of MLS Cup Playoffs », page consultée le 22 nov. 2026, récupération SearXNG, contenu extrait : https://www.fccincinnati.com/news/matchday-preview-presented-by-kiesland-fc-cincinnati-travel-to-nashville-for-round-one-opener-of-mls-cup-playoffs
- FC Cincinnati, récapitulatif officiel Orlando 1–3 Cincinnati, page consultée le 22 nov. 2026, contenu extrait via SearXNG : https://www.fccincinnati.com/news/recap-orlando-city-sc-1-fc-cincinnati-3-audi-2026-mls-cup-playoffs-eastern-conference-wild-card-match
- PropLine via NODE.47 : événement 874119, dernière mise à jour globale observée 2026-11-22T06:56:32Z; détail du prix et bookmakers consignés aux sections 6–8.
- ESPN via NODE.47 : health, catalogue, coverage, events et event_detail; réponses et lacune consignées en sections 1–2.
