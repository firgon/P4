# Manager de Tournoi d'Echecs

Petite application console qui permet de créer, de gérer et de sauvegarder en local des tournois d'échecs sur un modèle de "Ronde Suisse"
(Au premier tour, le joueur le mieux classé affronte le mieux classé de la deuxième partie du classement, etc... 
Aux tours suivants, chaque joueur affronte un joueur de niveau similaire qu'il n'a pas encore affronté dans le tournoi.)

## Requirements.txt
L'application nécessite l'installation du module tinydb qui permet la création de mini bases de données en local. Pensez à l'installer sur votre machine avant de lancer l'application. 
```py -m pip install requirements.txt```

Pour lancer l'application, ouvrez une fenêtre cmd et lancez main.py.

Vous naviguerez entre les différents menus en tapant le numéro de l'option choisie ou en activant les commandes magiques disponibles à tout moment (du style /Q pour Quitter)

![image](https://user-images.githubusercontent.com/5315104/172361195-57c2b38c-f91b-4f63-9d61-026af02e7100.png)

## Respect PEP8

Afin de vous assurer que le projet respecte les standards de programmation python définis dans la PEP8, vous pouvez installer et lancer flake8-html afin d'obtenir (si tout se passe bien) un rapport de ce type :

![image](https://user-images.githubusercontent.com/5315104/172361993-4da0e7bd-6e35-4885-9a7e-64d5fec234be.png)


#### Installer flake8-html:
```py -m pip install flake8-html```

#### Lancer flake8-html
Placez-vous dans le répertoire d'installation de votre application et tapez sur votre invite de commande:

```flake8 --format=html --htmldir=flake-report```

This project is tested with BrowserStack.
