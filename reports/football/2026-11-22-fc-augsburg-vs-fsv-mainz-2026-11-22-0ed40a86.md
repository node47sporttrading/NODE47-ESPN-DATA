# NODE.47 — FC Augsburg vs FSV Mainz

## 1. Fiche événement
- Sport : football
- Compétition : German Bundesliga, ESPN competition_id `ger.1`, registre verified, collection_enabled true
- Match : FC Augsburg — FSV Mainz
- Date : 2026-11-22, 14:30 UTC / 15:30 Africa/Douala
- Stade : WWK Arena, Augsburg
- Statut : scheduled, pré-match
- ESPN event_id : `401884733`
- PropLine sport_key : `soccer_bundesliga`
- PropLine event_id : `684155`

## 2. Journal des contrôles
- ESPN health : OK, dernière actualisation 2026-11-22T13:55:08Z, fraîcheur 486 s au contrôle.
- Catalogue ESPN soccer : 220 compétitions recensées ; German Bundesliga sélectionnée par ID exact `ger.1`.
- Couverture ESPN : 237/237 routes OK ; la recherche événement par fenêtre de date n’a pas retourné le match, mais le détail exact ESPN et le crosswalk PropLine concordent.
- PropLine health/sports : OK ; marchés football disponibles.
- PropLine event markets : OK ; h2h, spreads, totals et BTTS disponibles.
- SearXNG health/search : OK ; pages lues quand `page_content` était disponible.
- Limites : pas d’historique complet d’ouverture disponible dans le snapshot ; modèle Poisson non validé et split extérieur Mainz de 4 matches.

## 3. Données sportives et audit des lacunes
- Augsburg : 14e, 9 points après 9 matches ; forme de championnat rapportée L-L-D-L-D, dernière défaite 2-5 à Leipzig.
- Mainz : 12e, 10 points après 9 matches ; série rapportée de quatre défaites toutes compétitions, dernière défaite 1-2 contre Bayern.
- Splits rapportés : Augsburg à domicile 1,80 but marqué / 1,40 encaissé ; Mainz à l’extérieur 2,75 marqué / 1,75 encaissé.
- Absences/conditions : Augsburg sans Massengo ni Matsima ; Gouweleeuw signalé incertain dans l’aperçu. Mainz : Kohr absent, Mwene de retour de suspension ; les compositions publiées indiquent les titulaires.
- Lacunes : pas de xG comparable ni de données propriétaires de tirs/qualité des occasions ; météo non intégrée ; historique bookmaker complet non fourni.

Sources lues :
- OneFootball, « FC Augsburg vs FSV Mainz 05 – Prediction… », publié le 2026-11-22 : https://onefootball.com/en/betting/predictions/fc-augsburg-vs-fsv-mainz-05-22-11-2026 — page consultée ; données de forme, splits, absences rapportées.
- Bulinews via Yahoo Sports, « FC Augsburg vs. Mainz 05 preview… », 2026-11-21 : https://sports.yahoo.com/articles/fc-augsburg-vs-mainz-05-181900305.html — page consultée ; contexte, absences.
- Bulinews via Yahoo Sports, « Confirmed lineups… », 2026-11-22 : https://sports.yahoo.com/articles/confirmed-lineups-fc-augsburg-vs-133500749.html — page consultée ; compositions confirmées.
- Soccerway, « Augsburg v Mainz », récupéré le 2026-11-22 : https://www.soccerway.com/match/augsburg-fTVNku3I/mainz-EuakNmc1/ — page consultée ; forme, splits et H2H.
- ESPN event detail : https://www.espn.com/soccer/match/_/gameId/401884733/mainz-fc-augsburg — donnée native, statut et lieu.

## 4. Analyse tactique et qualitative
- Augsburg annoncé en 3-4-2-1 : Dahmen ; Keitel, Bah, Behrens ; Fellhauer, Schnitzer, Rieder, Wolf ; Kade, Claude-Maurice ; Gregoritsch.
- Mainz annoncé en 3-5-2 : Zentner ; da Costa, Posch, Potulski ; Caci, Nebel, Sano, Amiri, Mwene ; Tietz, Becker.
- Mécanisme favorable à Over 2.5 : les données de forme rapportées montrent deux défenses perméables ; Augsburg a encaissé au moins deux buts dans six de ses sept derniers matches de championnat, tandis que les deux équipes ont des profils de matches récents élevés en buts. Confiance moyenne.
- Mécanisme favorable à Mainz +0/-0.25 : Mainz possède un meilleur historique récent face à Augsburg et une production extérieure rapportée forte ; l’absence de Matsima et l’incertitude Gouweleeuw affaiblissent la stabilité défensive d’Augsburg. Confiance moyenne.
- Contre-argument : Mainz arrive aussi sur une série négative ; Augsburg reste compétitif à domicile et le match peut se fermer si l’enjeu prime.
- Statut : EXÉCUTÉ — PARTIEL, car les preuves tactiques détaillées indépendantes sont limitées.

Matrice synthétique :
| Marché | Facteur | Effet | Contre-argument | Confiance |
|---|---|---|---|---|
| Over 2.5 | Défenses vulnérables, splits offensifs élevés | SOUTIENT | Réaction prudente après série de défaites | Moyenne |
| Mainz +0/-0.25 | H2H récent, avantage extérieur, défense d’Augsburg remaniée | SOUTIENT | Forme récente de Mainz défavorable | Moyenne |
| 1X2 Mainz | Prix et contexte légèrement favorables | SOUTIENT faiblement | Nul plausible, avantage domicile | Faible à moyenne |

## 5. Modèle quantitatif
- Baseline : Poisson indépendant, non calibré, USER_CONFIRMED_BASELINE mais validation serveur inactive.
- Taux utilisés : Augsburg domicile 1,80 marqué / 1,40 encaissé ; Mainz extérieur 2,75 marqué / 1,75 encaissé.
- Lambda : Augsburg 1,775 ; Mainz 2,075.
- Probabilités baseline : Augsburg 33,7 %, nul 20,9 %, Mainz 45,4 % ; Over 2.5 73,9 % ; BTTS Oui 72,6 %.
- Échantillon : 5 matches domicile Augsburg, 4 matches extérieur Mainz ; minimum requis 5 non atteint pour le split extérieur.
- Limite : probabilités descriptives, non autorisées pour une mise.

## 6. Marchés et prix
Snapshot PropLine au 2026-11-22 vers 14:05 UTC :
- 1X2 : meilleur prix observé Mainz 2,35 ; Augsburg 3,10 ; nul 4,00, avec variations selon opérateur.
- Mainz -0.25 : environ 2,02 chez Pinnacle ; ligne équivalente à vérifier selon règlement.
- Over 2.5 : environ 1,45 ; Under 2.5 environ 3,00.
- Over 3.5 : environ 2,22 ; Under 3.5 environ 1,87.
- BTTS Oui : environ 1,43.
- Les prix sont des snapshots multi-bookmakers ; format fournisseur américain converti localement en décimal. Règlement exact à contrôler chez l’opérateur.

## 7. Historique et structure du marché
- SNAPSHOT SEUL : pas d’ouverture complète ni trajectoire consolidée.
- Le marché favorise Mainz et un total de buts élevé.
- No-vig exact non retenu pour une décision de mise, car les meilleures cotes proviennent de fournisseurs différents et les prix/conditions ne constituent pas toujours une capture homogène.
- Structure du marché : SOUTIENT légèrement Mainz et Over 2.5, mais signal limité par l’absence d’historique.

## 8. Pourquoi ce prix maintenant
- Explication plausible : Mainz bénéficie du H2H récent, de sa production extérieure et d’une défense d’Augsburg remaniée.
- Explication concurrente : la série de défaites de Mainz empêche une cote plus basse ; l’avantage domicile d’Augsburg est intégré.
- Pour le total, les défenses et les splits offensifs rapportés sont compatibles avec un Over 2.5.
- Statut : PLAUSIBLE, pas corroboré par un historique complet.

## 9. Matrice de convergence
| Marché/direction | Sport/modèle | Tactique/scénario | Info/conditions | Prix | Convergence |
|---|---|---|---|---|---|
| Over 2.5 | SOUTIENT | SOUTIENT | NEUTRE | SOUTIENT | PARTIELLE |
| Mainz +0.25 | SOUTIENT faiblement | SOUTIENT | SOUTIENT | SOUTIENT | PARTIELLE |
| Mainz 1X2 | SOUTIENT faiblement | SOUTIENT faiblement | NEUTRE | SOUTIENT | FAIBLE à PARTIELLE |

## 10. Cohérence
- Cohérence temporelle : bonne, informations du 21–22 novembre 2026 et prix capturés avant le coup d’envoi.
- Cohérence statistique : moyenne ; les sources secondaires concordent sur les positions, séries et splits, mais certaines statistiques sont agrégées automatiquement.
- Contradiction principale : Mainz est favori malgré quatre défaites récentes ; cela réduit la confiance plutôt que d’invalider le signal.

## 11. Alignement
- Over 2.5 : alignement moyen à fort ; production offensive et vulnérabilités défensives peuvent produire au moins trois buts.
- Mainz +0.25 : alignement moyen ; protège partiellement contre le nul, mais reste sensible à l’avantage domicile.
- 1X2 Mainz : alignement moyen-faible, car le nul est un scénario important.

## 12. Confiance
- Qualité : moyenne.
- Fraîcheur : élevée.
- Couverture : bonne pour événement, compositions et prix ; partielle pour données avancées.
- Indépendance : moyenne ; plusieurs sources reprennent des flux de match similaires.
- Confiance finale : moyenne-faible à moyenne.

## 13. Edge / EV
- Edge de mise : NON CALCULABLE / non autorisé, car la baseline n’est pas validée et le split extérieur Mainz n’atteint pas le minimum requis.
- Les probabilités Poisson ne doivent pas être transformées en mise.
- Mise calculée : 0 U.

## 14. Classement des marchés
1. Over 2.5 — meilleur alignement statistique et tactique, mais prix court.
2. Mainz +0.25 — protection contre le nul et soutien contextuel, mais forme récente négative.
3. Mainz 1X2 — rendement supérieur, mais variance du nul trop importante.

## 15. Chemin décisionnel
- Événement, participants, horaire et marché : satisfaits.
- Prix actuel : vérifié, mais snapshot seul.
- Deux familles indépendantes : satisfaites pour Over 2.5 et Mainz +0.25.
- Confiance haute / validation modèle / historique prix complet : non satisfaits.
- Règle appliquée : BET PRUDENT au maximum, sans mise calculée.

## 16. Mise
- Mise calculée : NON DÉTERMINÉE PAR LE MOTEUR.
- Recommandation de risque : 0 U compte tenu du modèle non validé et du snapshot seul.
- NO BET financier : 0 U.

## 17. Verdict final
**BET PRUDENT — Over 2.5 buts, ligne 2.5, autour de 1.45 maximum acceptable uniquement si le règlement et le prix sont confirmés.**
Motif déterminant : baseline descriptive à 73,9 % et contexte tactique/qualitatif compatible avec un match ouvert.
Risque majeur : prix court, échantillon limité et données de forme issues en partie de sources secondaires.
Alternative plus spéculative : Mainz +0.25 autour de 2.02, mais confiance inférieure.
Aucune mise calculée : 0 U.
