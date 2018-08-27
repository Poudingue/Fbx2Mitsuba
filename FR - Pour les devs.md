# Format FBX

Le format FBX est un format contenant la majeure partie des informations d'une scène 3D.
À l'heure actuelle, converter.py peut prendre -d ou --debug en argument pour exporter sous forme d'un fichier XML le contenu du fichier FBX pour une meilleure lisibilité de la part d'un humain. Cependant, sur des gros fichiers FBX, l'export peut être long, à cause de ma fonction de prettyprint XML qui est peu efficace.

Le format FBX contient 7 sections principales, mais seules les sections «Objects» et «Connections» nous sont utiles à l'heure actuelle. GlobalSettings est utilisé une fois pour les informations sur l'axe vertical.

## Objects

Objects contient tous les objets de la scène. C'est ici que l'on trouvera toutes les infos importantes. Les noms des objets tels que référencés dans la scène sont indiqués.

### Geometry

Les objets de type Geometry contiennent les informations sur les formes 3D.
Ils contiendront généralement une liste de sommets (Vertices), des faces référençant ces sommets (PolygonVertexIndex), des arrètes (Edges), des normales (contenues dans LayerElementNormal), et des coordonées de texture pour l'uv mapping (contenues dans LayerElementUV). Dans le cas où plusieurs matériaux différents sont appliqués sur un même objet géométrique, ils seront référencés par face dans la section «LayerElementMaterial».

### NodeAttribute

Ces objets contiennent les paramètres d'un Node. Les nodes peuvent référencer différentes choses. Ici, on ne retiendra que les nodes «Light», «Camera», et «Null». Les nodes Null semblent être les cibles des caméras ou des spotlight. Il semblent qu'ils servent aussi pour l'origine des caméras de type «Physical».

### Model

Contient des informations de placement dans l'espace. Grâce aux connections, on peut appliquer ces transformations aux objets concernés.

### Material

Contient tout simplement les informations de matériaux. «ShadingModel» est censé indiquer le type de matériau utilisé, mais en dehors des matériaux standards basiques, il n'indique en général que  «unknown».

### Video

Il semblerait que ce soit équivalent à «Texture», avec moins d'infos.

### Texture

Référence une image. Le chemin est disponible en relatif et en absolu. Donne également les informations de tiling.

### Autres objets

Il existe d'autres objets que nous n'utilisons pas à l'heure actuelle : Implementation, BindingTable, BindingOperator, AnimationLayer, AnimationCurveNode.

## Connections

Connections contient les connections entre différents objets, et permet de reconstituer la structure de la scène. À chaque fois, les objets sont référencés par id. L'id 0 est tout simplement la «racine» de la scène, les objets qui en dépendent sont placés dans la scène.
Les commentaires donnent les noms des objets tels que référencés dans la scène.

Il existe deux types de connections :

- Les connections simples (commençant par OO), qui dénotent une simple dépendance entre 2 objets. Si la scène a une hiérarchie, elle sera assurée par ce type de connection. Le premier objet est subordonné au second.

- Les connections paramètres (commençant par OP), qui indiquent qu'un objet prend un autre en paramètre (par exemple un matériau qui prend une texture). Le premier objet est pris comme paramètre par le second.

  Le paramètre est spécifié.

# Déroulement du programme

Dans un premier temps, le programme interprète les arguments qui lui sont passés. Un impératif est l'utilisation d'un fichier FBX en argument. Les paramètres sont ensuite stockés dans un fichier «config.py» pour accès par les différents modules.

La première étape est l'extraction des informations du FBX. Le fichier est parcouru et une structure en arbre est créée par fbx2tree. Cette structure peut être exportée au format XML avec l'option -d.

La seconde étape est l'écriture du fichier de sortie. La fonction builder_fromfbx.build est en charge de cette tâche, et va appeler uns à uns tous les modules nécessaires.

## tools.py

Le fichier tools.py contient plein de petites fonctions utiles à différents instants du programme. Certaines de ces fonctions sont utilisées par toutes les sections, et servent à faire un code plus léger et lisible.

D'autres sont spécifiques à certaines sections, ou utilisées une seule fois, mais sont placées ici pour ne pas encombrer les parties principales du code et les garder les plus lisibles possibles.

## builder_fromfbx.py

La fonction builder_fromfbx.build va dans un premier temps extraire de l'arbre tous les objets qui nous seront utiles. Elle va ensuite extraire les connections entre les objets, et utiliser tools.extract_links pour obtenir des dictionnaires de correspondance entre les objets présents dans la scène. À l'avenir, l'utilisation d'une structure en arbre pourrait peut-être simplifier les choses, remplaçant l'utilisation des ids. Seulement je ne suis pas sûr que ça soit faisable, l'utilisation d'instances dans 3ds Max permet qu'un objet ait plusieurs parents différents.

Puis vont être appelées dans l'ordre les fonctions de création de caméras et lumières, de textures, de matériaux, de géométrie, puis enfin de modèles. Chacune de ces fonctions a en charge certains objets, et se charge de les ajouter à la scène :

- light_cam_builder s'occupe des caméras et des lumières
- textures_builder s'occupe des références aux textures
- materials_builder gère les matériaux
- shapes_builder exporte les maillages des objets 3D
- models_builder place les maillages dans la scène.

Pour finir, le fichier final XML est créé.

# TODO section

## light_cam_builder

## texture_builder

## materials_builder

## shapes_builder

## models_builder

# Améliorations possibles

## Interface graphique

Pour des raisons d'ergonomie et de simplicité d'accès, il serait bon de mettre en place une interface graphique simple, pour permettre l'utilisation du programme à un plus grand nombre.

Une fois lancée, cette interface vérifierait la version de Python, installerait Pillow si nécessaire, et permettrait, via une boite de dialogue simple, de paramétrer et de lancer la conversion.

## Plus de types d'objets

Pour l'instant, tous les types d'objets ne sont pas pris en compte. Les caméras physiques, les informations de transluminescence, ainsi que beaucoup d'autres détails, ne sont pas encore implémentés. Le fichier FBX contenant des informations limitées, il faudra dans un premier temps récupérer tout ce qui est possible de récupérer. L'utilisation d'un autre format (ASE par exemple) pour compléter les information peut également être envisagé. L'exemple de l'environnement mapping, présent dans le ASE mais pas dans le FBX, est un bon exemple des limitations du format.

## Programme plus générique

À l'heure actuelle, les modèles de type caméra et lumières sont placés par light_cam_builder. Il serait logique que models_builder s'occupe de les placer, tout comme il s'occupe de placer les modèles référençant de la géométrie. 

La partie materials_builder est très linéaire dans son exécution, avec beaucoup de code se ressemblant, il est sans doute possible de rendre générique le fait d'appliquer soit une texture soit une couleur/valeur pour une caractéristique donnée.

## Conversions plus précises

Le programme utilise actuellement des algorithmes arbitraires et approximatifs pour la conversion de la carte de glossiness et de la couleur exprimée en Kelvin. Il faudrait raffiner ces algorithmes pour plus de fidélité à la scène originale.

## Exportation portable

L'exportation prend pour l'instant les références qui sont données par le fichier FBX. Avec l'option --portable, les chemins relatifs sont pris. L'idéal serait la création d'un nouveau dossier comprenant la scène Mitsuba Renderer ainsi que tout ce qui est nécessaire à l'affichage correct. L'ensemble des maillages, l'ensemble des textures, dans des sous-dossiers. Dans ce genre de cas, le transfert de fichiers d'un ordinateur à l'autre ne poserait plus aucun problème. Le programme devrait aussi, lorsqu'il n'arrive pas à trouver un fichier là où il devrait être, permettre à l'utilisateur de spécifier le chemin.