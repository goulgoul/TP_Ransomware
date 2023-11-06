# TP Ransomware

### Introduction

Ce devoir consiste en la fabrication guidée d'un ransomware. Les fonctionnalités seront détaillées dans les paragraphes suivants. S'y ajouteront des notes complémentaires sur ce que j'aurais voulu ajouter, en eus-je pris le temps plus tôt. 

### Chiffrement

**Q1** : L'algorithme est le chiffrement XOR. Il est peu robuste car les bits de sa clé sont répétés de manière cyclique. 

Il serait plus efficace d'utiliser un chiffrement robuste, comme les variantes de l'AES pour s'assurer que personne ne puisse retrouver ses données sans notre intervention.

### Setup

**Q3** : Il est préférable de vérifier qu'un token n'est pas déjà sauvegardé pour ne pas le remplacer par un autre token, ce qui aurait pour effet de rendre le déchiffrement impossible (impossible d'associer la clé saisie par l'utilisateur à un jeton authentique)

### Vérification de l'authenticité de la clé

**Q4** : pour vérifier que la clé est bonne, il suffit de calculer un token candidat en dérivant la clé saisie et le sel authentique puis de comparer ce jeton au jeton authentique. Si les deux dérivations sont les mêmes, alors la clé saisie est correcte. 

## Bonus

### Vol de fichiers

Pour voler les fichiers, on peut lire les données de chaque fichier chiffré, les convertir en base 64 et les récupérer sur le CNC 
