# Projet de SImulation
## aloha.p
cette partie simule le projet sans aucun ajout par rapport au sujet
### utilisation
Pour lancer une simulation en specifiant des paramètres(si un paramtre n'est pas specifier utilise des valeur par defaut)  
Donne e sortie 3 fichiers aloha_debis.pdf, aloha_pertes.pdf, aloha_ paquets qui sont des graqhique du debit par rapport au temps, des paquet perdus sur le nombre de paquet recus par rapport au temps, et le nombre de paquet prsent par rapport au temps
```shell
  python aloha.py --N 10 --K 100 --Tmax 100000 --tau 1 --simu courbes
```
Pour afficher des resultat de simulation en faisant varier le parametre N(le nombre de station emetrices)
entre deux nombre de station min et max avec un pas 
```shell
python aloha.py --simu N --min 1 --max 100 --pas 1
```
Pour faire afficher le graphe des 
