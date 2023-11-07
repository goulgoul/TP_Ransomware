# TP Ransomware

### Introduction

Ce devoir consiste en la fabrication guidée d'un ransomware. Les fonctionnalités seront détaillées dans les paragraphes suivants. S'y ajouteront des notes complémentaires sur ce que j'aurais voulu ajouter, en eus-je pris le temps plus tôt. 

### Chiffrement

**Q1** : L'algorithme est le chiffrement XOR. Il est peu robuste car les bits de sa clé sont répétés de manière cyclique. 

Il serait plus efficace d'utiliser un chiffrement robuste, comme les variantes de l'AES pour s'assurer que personne ne puisse retrouver ses données sans notre intervention.

**Q2** : Utiliser un HMAC permettrait de s'assurer qu'un message est authentique mais ne garantit pas que  

### Setup

**Q3** : Il est préférable de vérifier qu'un token n'est pas déjà sauvegardé pour ne pas le remplacer par un autre token, ce qui aurait pour effet de rendre le déchiffrement impossible (impossible d'associer la clé saisie par l'utilisateur à un jeton authentique)

### Vérification de l'authenticité de la clé

**Q4** : pour vérifier que la clé est bonne, il suffit de calculer un token candidat en dérivant la clé saisie et le sel authentique puis de comparer ce jeton au jeton authentique. Si les deux dérivations sont les mêmes, alors la clé saisie est correcte. 

## Bonus

### Vol de fichiers

Pour voler les fichiers, on peut lire les données de chaque fichier chiffré, les convertir en base 64 et les récupérer sur le CNC 

### Chiffrement

**B2** : La clé utilisée pour le XOR étant cyclique, il est possible de connaître la clé en compaprant un fichier sain avec un fichier chiffré. 
Donnée ^ Clé = Chiffré ; Chiffré ^ Clé = Donnée
Data ^ Chiffré = Clé
Ainsi, un script permettant de trouver la clédu chiffrement serait aussi simple que :
```py
with open(clear_file as c):
    clear_data = c.read()
with open(encrypted_data as e):
    encrypted_data = e.read()
key = clear_data ^ encrypted_data

logging.info(key)
```

**B3** : La bibliothèque cryptography nous offre d'autres options de chiffrement. La plus simple et sécurisée d'entre elles (pour un développeur junior comme nous) est le module Fernet, qui permet de chiffrer symétriquement et retourne un token unique permettant de vérifier l'authenticité du message.
Malgré leur plus grande sensibilité, il est également possible d'utiliser les fonctions comme AESxxx de cryptography.hazmat pour un contrôle plus fin des paramètres cryptographiques.

### Packer

**B4** : avec PyInstaller, il faut utiliser la commande `pyinstaller source/ransomware.py --onefile` depuis notre ordinateur ou `pyinsatller root/ransomware/ransomware.py --onefile` depuis le container (ce que je devais faire pour des raisons de compatibilité, _I use Arch, btw..._)

**B5** : le binaire créé se trouve dans dist/, monté dans root/bin dans le container
