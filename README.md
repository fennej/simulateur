# Projet de SImulation
## aloha.py
cette partie simule le projet sans aucun ajout par rapport au sujet
### utilisation
Pour lancer une simulation en specifiant des paramètres(si un paramtre n'est pas specifier utilise des valeur par defaut)  
Donne e sortie 3 fichiers aloha_debis.pdf, aloha_pertes.pdf, aloha_ paquets qui sont des graqhique du debit par rapport au temps, des paquet perdus sur le nombre de paquet recus par rapport au temps, et le nombre de paquet prsent par rapport au temps
```shell
  python aloha.py --N 10 --K 100 --Tmax 100000 --tau 1 --simu courbes
```
Pour faire afficher le graphe du debit final en fonction de lmabda
```shell
  python aloha.py --simu lambda --min 0.1 --max 1.5 --pas 0.05 --Tmax 350000
```
Pour afficher des resultat de simulation en faisant varier le parametre N(le nombre de station emetrices)
entre deux nombre de station min et max avec un pas 
```shell
python aloha.py --simu N --min 1 --max 100 --pas 1
```
Pour Afficher des valeur de N avec un intervals de confiance à 95%
```shell
  python aloha.py --simu N_ic --min 80 --max 160 --pas 10
```

## Simulation.py
Cette partie simule un algorithme se rapprochant du CSMA/CD avec un backoff borné et un etat d'écoute du canal
### utilisation
S'utilise comme aloha.py

Pour lancer une simulation en specifiant des paramètres(si un paramtre n'est pas specifier utilise des valeur par defaut)  
Donne e sortie 3 fichiers csma_debis.pdf, csma_pertes.pdf, csma_ paquets qui sont des graqhique du debit par rapport au temps, des paquet perdus sur le nombre de paquet recus par rapport au temps, et le nombre de paquet prsent par rapport au temps
```shell
  python Simulation.py --N 10 --K 100 --Tmax 100000 --tau 1 --simu courbes
```
Pour faire afficher le graphe du debit final en fonction de lmabda
```shell
  python Simulation.py --simu lambda --min 0.1 --max 1.5 --pas 0.05 --Tmax 350000
```
Pour afficher des resultat de simulation en faisant varier le parametre N(le nombre de station emetrices)
entre deux nombre de station min et max avec un pas 
```shell
python Simulation.py --simu N --min 1 --max 100 --pas 1
```
Pour Afficher des valeur de N avec un intervals de confiance à 95%
```shell
  python Simulation.py --simu N_ic --min 80 --max 160 --pas 10
```
##Theorie.py
Fichier utiliser pour verifier si le debit est égal à un quand on utiliser une seule machine avec le mode CSMA\CD
##etude_parametrique.py
Donne les graphs pour le CSMA/CD car trop long d'utiliser le fichier Simulation.py
permet de voir l'évolution du débit en fonction du nombre de stations, ou par rapport au parametre lambda et si nous voulions faire varier la taille des paquets
