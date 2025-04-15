# Traçabilité dans Bitcoin  
Le projet a pour but de pouvoir générer un graphe de transactions à partir d'une transaction de départ donnée.

### Lancement du programme  
1) Il faut lancer le serveur Flask [src/server.py](src/server.py).  
2) Dans un autre terminal, lancer le [src/main.py](src/main.py) avec les paramètres de votre choix.

### Explication du rendu du graphe

Dans le graphe généré :

- **Les formes :**  
  - Les **carrés** représentent des **transactions**.  
  - Les **ronds** représentent des **adresses**.

- **Couleurs des éléments :**  
  - La **transaction initiale** est colorée en **violet**.  
  - Les **transactions** sont en **vert** par défaut.  
  - Les **adresses** sont en **bleu** par défaut.  

- **Cas particuliers pour les adresses :**  
  - **Noir** : adresse associée à un **exchange**.  
  - **Rouge** : adresse **suspecte** (les tags associés sont visibles au survol).

- **Interaction :**  
  - Un **clic sur un nœud** permet de retracer le **chemin jusqu'à la transaction initiale**.

### Structure de fichiers
#### src/  
- [src/main.py](src/main.py) : classe principale pour lancer la génération de graphe (après avoir lancé le serveur). Vous pouvez préciser dedans les 4 champs détaillés dans la [section html](#html)  
- [src/mixers.py](src/mixers.py) : classe principale de la génération de graphe.  
- [src/render_graph.py](src/render_graph.py) : classe principale pour le rendu du graphe (avec Pyvis)  
- [src/server.py](src/server.py) : serveur Flask pour gérer les interactions avec la page Web.  
- [src/scrapp_arkham.py](src/scrapp_arkham.py) et [src/collect_tags.py](src/collect_tags.py) : modules pour le scraping des tags associés aux adresses BTC

#### html/:  
Contient les graphes générés par nos tests. La structure de nommage des fichiers HTML est la suivante :  
`graph_{1}_{2}_{3}_{4}.html` où :  
- **1** : Soit `depth` pour dire que la génération de graphe a été faite selon une profondeur maximale donnée, soit `nb` pour dire que le graphe a été généré selon un nombre de nœuds maximal.  
- **2** : C'est un entier qui représente soit la profondeur max, soit le nombre de nœuds max du graphe selon le choix de la première option.  
- **3** : Dans le cas d'un parcours avec une profondeur maximale donnée, ce champ n'existe pas.  
  Dans l'autre cas, il représente le type de parcours utilisé pour générer le graphe : `BFS`, `DFS` ou `PQ` (file de priorité).  
- **4** : les 5 premiers caractères de la transaction source  

#### json/:  
Contient des tags scrappés pour l’étiquetage du graphe.
