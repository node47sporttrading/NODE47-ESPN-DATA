# NODE.47 — Liverpool vs Manchester United

## 1. Fiche événement
- Sport : football
- Compétition : English Premier League
- ESPN competition_id : eng.1
- ESPN event_id : 401878755
- PropLine sport_key / event_id : soccer_epl / 555685
- Participants : Liverpool (domicile) vs Manchester United (extérieur)
- Date/heure : 2026-11-22 16:30 UTC (17:30 Africa/Douala)
- Stade : Anfield
- Statut à la collecte : programmé, non commencé
- Collecte ESPN : fraîche, statut service ok ; couverture de la route eng.1 ok.

## 2. Journal des contrôles
- ESPN health : exécuté, ok, rafraîchi 2026-11-22T15:44:47.600461Z.
- Catalogue ESPN soccer : exécuté ; 220 compétitions retournées, sélection exacte eng.1.
- ESPN coverage : exécuté ; route eng.1 ok.
- ESPN event detail : exécuté ; identité, horaire, stade et statut confirmés.
- PropLine health/sports : exécutés ; soccer_epl disponible.
- Crosswalk : non ambigu, PropLine 555685 référence explicitement ESPN 401878755.
- Marchés disponibles : discovery exécutée.
- Cotes : snapshot pré-match obtenu ; historique d’ouverture complet non fourni.
- SearXNG health/search : exécutés, pages lues lorsque page_content disponible.
- Limite : pas de split domicile/extérieur suffisamment documenté pour activer proprement le Poisson.

## 3. Données sportives et audit des lacunes
Données lues :
- Liverpool : 18 points après 10 journées ; source de preview consultée, moyenne récente rapportée de 1,4 but marqué et 1,0 encaissé sur les dix derniers matchs.
- Manchester United : 8 points après 10 journées, 19e ; série de huit matchs de championnat sans victoire ; moyenne récente rapportée de 1,4 but marqué et 1,9 encaissé.
- Derniers résultats rapportés : Liverpool 3-1 Crystal Palace ; Manchester United 4-4 Aston Villa.
- Disponibilité rapportée : Liverpool sans Ekitike, Bradley et Leoni ; United sans Baleba, Šeško et Ugarte. Rashford et Shaw n’étaient pas disponibles dans la composition publiée ; Gakpo/Gravenberch faisaient l’objet d’incertitudes dans une source locale.
- Lacunes : pas de base complète et comparable pour les splits domicile/extérieur, xG/xGA natifs complets, météo/arbitre et historique des mouvements.

## 4. Analyse tactique et qualitative
La composition publiée par USA Today donne un 4-2-3-1 pour United : Lammens ; Yoro, De Ligt, Martínez, Dalot ; Mainoo, Tielemans ; Mbeumo, Fernandes, Dorgu ; Cunha. La preview Liverpool consultée rapporte un 4-2-3-1 avec Isak en pointe, Wirtz derrière lui et une défense renforcée par le retour de Van Dijk. Le statut de Gakpo/Gravenberch restait moins sûr dans une source locale ; cette incertitude ne doit pas être traitée comme une absence confirmée.

| Facteur | Observation/proof | Effet marché | Contre-argument | Confiance |
|---|---|---|---|---|
| Forme et structure | Liverpool 4e/18 pts, United 19e/8 pts et sans victoire sur 8 matchs selon USA Today et la preview consultée | Soutient Liverpool | Le derby réduit l’écart de forme ; United peut bénéficier du choc psychologique du changement d’entraîneur | Moyenne |
| Disponibilité | United privés de Baleba, Šeško et Ugarte ; Shaw absent de la XI publiée ; Liverpool conserve Van Dijk et plusieurs titulaires selon les pages lues | Soutient Liverpool | Gakpo/Gravenberch incertains dans une source, ce qui peut réduire la profondeur | Moyenne |
| Matchup de score | Le 4-2-3-1 des deux côtés suggère un match décidé par la qualité des sorties de pression et des transitions, mais aucune observation vidéo spécifique n’a été validée | Non établi | United possède Fernandes/Mbeumo pour attaquer les espaces si Liverpool perd le ballon | Faible |
| Contexte entraîneur | Premier match de Pochettino à United, avec très peu de préparation ; Iraola appelle publiquement à ne pas sous-estimer United | Soutient légèrement Liverpool | Un nouvel entraîneur peut provoquer une réaction immédiate | Moyenne-faible |
| Marché buts | Les books consultés donnent généralement Over 2,5 très favori et BTTS Yes favori | Neutre pour le 1X2 ; cohérent avec un scénario ouvert | Les prix sont très chargés et sans modèle validé, pas de sélection buts | Faible |

Synthèse tactique : EXÉCUTÉ — PARTIEL. Le mécanisme le plus robuste est l’avantage contextuel de Liverpool à domicile contre une équipe de United affaiblie et en transition de management. Le scénario d’invalidation est un United compact, discipliné et efficace en transition, ou une baisse de créativité de Liverpool si les incertitudes offensives se matérialisent.

## 5. Modèle quantitatif
MODÈLE NON VALIDABLE pour une sélection chiffrée : les taux domicile/extérieur vérifiés et comparables nécessaires au Poisson indépendant ne sont pas disponibles dans la collecte. Les moyennes « derniers dix matchs » ne sont pas substituées à ces splits.

## 6. Marchés et prix
Snapshot PropLine, horodatages autour de 2026-11-22 15:39–15:47 UTC :
- 1X2 : Liverpool généralement entre -119 et -143, Manchester United +275 à +350, nul +280 à +345 selon bookmaker.
- Meilleur prix Liverpool observé dans l’échantillon : -119, soit 1,840 en décimal ; plusieurs books étaient autour de -127/-128, soit environ 1,787–1,781.
- Total principal observé selon books : 2,5 ou 3,5, avec des prix non homogènes ; ne pas les comparer comme une même ligne.
- BTTS Yes souvent favori ; lignes et prix variables selon bookmaker.
- Règlement retenu : marché match/90 minutes pour 1X2 ; les prolongations ne s’appliquent pas à la Premier League.

## 7. Historique et structure du marché
SNAPSHOT SEUL pour cette analyse. Les cotes concurrentes soutiennent un favoritisme de Liverpool, mais l’ouverture et la trajectoire complète ne sont pas disponibles. No-vig calculable ponctuellement sur une capture complète, mais il s’agit d’une probabilité de marché, pas d’une probabilité modèle.

## 8. Pourquoi ce prix maintenant
Explication PLAUSIBLE, non corroborée par historique : le prix reflète probablement la combinaison domicile Anfield, écart de classement/forme, absences de United et changement de manager. Le mouvement exact ne peut pas être attribué à une information précise. Alternatives : réévaluation de la composition, ajustement concurrentiel ou marge propre à chaque bookmaker.

## 9. Matrice de convergence — Liverpool 1X2
- SPORT/PERFORMANCE/MODÈLE : SOUTIENT partiellement — classement, forme récente et défenses rapportées ; modèle Poisson indisponible.
- TACTIQUE/MATCHUP/SCÉNARIO : SOUTIENT partiellement — avantage contextuel et disponibilité ; matchup spécifique peu documenté.
- INFORMATIONS/DISPONIBILITÉ/CONDITIONS : SOUTIENT — United en transition de management et absences rapportées ; incertitudes Liverpool non nulles.
- STRUCTURE DU MARCHÉ/PRIX : SOUTIENT — Liverpool favori chez plusieurs books ; snapshot seul.
Convergence : PARTIELLE.

## 10. Cohérence
Cohérence temporelle : bonne pour ESPN, PropLine et les pages datées du 22 novembre.
Cohérence statistique : moyenne ; les chiffres de preview ne remplacent pas les splits requis.
Cohérence informationnelle : moyenne ; plusieurs sources concordent sur le contexte de United, mais certaines informations d’effectif restent indirectes.
Cohérence causale : moyenne ; l’avantage Liverpool est plausible, pas démontré par une base de tracking tactique.

## 11. Alignement
L’alignement est moyen : le 1X2 traduit directement l’avantage domicile/forme et le contexte d’effectif, mais la ligne de prix est déjà favorable à Liverpool et aucune probabilité modèle exacte n’est validée. Invalidation : but précoce de United, transitions réussies de Mbeumo/Bruno, ou absence effective de plusieurs créateurs de Liverpool.

## 12. Confiance
Confiance globale : MOYENNE-FAIBLE.
Qualité : événement et prix vérifiés ; preuves sportives et d’effectif partiellement sourcées.
Fraîcheur : élevée au moment de la collecte.
Couverture : insuffisante pour un modèle quantitatif complet.
Indépendance : moyenne ; certaines previews reprennent les mêmes informations de team news.

## 13. Edge / EV
NON CALCULABLE : modèle validé et aligné sur le marché exact indisponible. Ne pas convertir cette absence en Edge négatif.

## 14. Classement des marchés
1. Liverpool 1X2 : meilleur candidat directionnel, mais prix déjà comprimé.
2. Liverpool -0,5 : équivalent économique du 1X2, sans avantage démontré.
3. Totaux/BTTS : scénarios plausibles mais lignes hétérogènes et modèle non validé.
Aucun marché ne justifie une mise calculée.

## 15. Chemin décisionnel
Événement identifié : oui.
Marché, sélection, prix et règlement : oui pour Liverpool 1X2.
Au moins deux familles indépendantes : oui, partiellement.
Convergence forte : non.
Modèle et Edge validés : non.
Snapshot seul : oui.
Règle appliquée : BET PRUDENT au maximum, sans mise calculée.

## 16. Mise
NON DÉTERMINÉE PAR LE MOTEUR. Aucune mise calculée ; 0 U.

## 17. Verdict final
BET PRUDENT — Liverpool 1X2, uniquement si la cote disponible est au moins 1,80 en décimal (environ -125 ou mieux). À la capture, le meilleur prix observé était environ 1,84, mais les prix variaient rapidement.
Motif : avantage domicile, écart de forme/classement, contexte de transition à United et disponibilité globalement favorable à Liverpool.
Risque majeur : le caractère émotionnel du derby, le premier match de Pochettino et les incertitudes offensives de Liverpool.
Modèle : non validable ; aucune mise, 0 U.

### Sources lues
- ESPN event detail : https://www.espn.com/soccer/match/_/gameId/401878755/manchester-united-liverpool
- USA Today, team news et XI : https://www.usatoday.com/story/sports/soccer/epl/2026/11/22/manchester-united-lineup-liverpool-premier-league/92893016007/
- Liverpool.com, informations d’effectif : https://www.liverpool.com/liverpool-fc-news/features/liverpool-team-news-manutd-gakpo-34949729
- Preview/statistiques et prix publiés antérieurement, utilisés comme contexte et non comme snapshot courant : https://www.sportsgambler.com/betting-tips/football/liverpool-vs-manchester-united-prediction-lineups-odds-2026-11-22/
