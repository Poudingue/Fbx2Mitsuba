# Format FBX

Le format FBX est un format contenant la majeure partie des informations d'une scène 3D.
À l'heure actuelle, converter.py peut prendre -d ou --debug en argument pour exporter sous forme d'un fichier XML le contenu du fichier FBX pour une meilleure lisibilité de la part d'un humain.

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
(Pour le détail sur le processus de chaque fonction, s'appuyer sur les commentaires.)

- light_cam_builder s'occupe des caméras et des lumières
- textures_builder s'occupe des références aux textures
- materials_builder gère les matériaux
- shapes_builder exporte les maillages des objets 3D
- models_builder place les maillages dans la scène.

Pour finir, le fichier final XML est créé.

# Fonctionnalités manquantes

## Physical cameras

Les caméras de type «Physical» ne sont à l'heure actuelle pas placées dans la scène. Il semble qu'elles sont référencées par les models de type «Null», mais les extraire me semble peu trivial. Les implémenter pourrait être une bonne chose, car les caméras de type physical permettent des choses intéressantes tel que l'usage de la profondeur de champ, cependant je n'ai trouvé dans le FBX aucun signe de paramètres permettant de récupérer ces réglages, et donc je doute de la faisabilité de la chose.

## Transformations composées

Mitsuba Renderer ne supportant pas les shapegroup imbriquées, les hiérarchies d'objet présentes dans 3ds Max ne peuvent pas être reconstituées. Pour récupérer les transformations correctes, j'ai donc dû faire la fonction «recursive_build_hierarchy», dans models_builder.py, qui remonte la chaîne de la hiérarchie des modèles et qui applique peu à peu toutes les transformations nécessaires. Ainsi, la géométrie est correctement placée dans la scène, avec les bonnes mises à l'échelle et rotations. 

Cependant, à l'heure actuelle, elles ne sont appliquées que sur les formes géométriques. Les caméras et les lumières dépendant d'une hiérarchie risquent d'être mal placées au sein de la scène. Avec des fonctions plus générique, les transformations composées pourraient être appliquées à tous les models, quel que soit le type d'objet qu'ils référencent.

## Propriétés des matériaux

Le type de matériaux que j'ai priorisé et sur lequel j'ai tout axé est le type «Physical Material».  Pour qu'une scène soit correctement transférée, c'est le type de matériaux que je recommande. Cependant quelques propriétés manquent, parmis lesquelles :

- L'usage de textures pour la transmittance spéculaire
- L'atténuation de la transmittance spéculaire dépendant du volume (à l'heure actuelle seule la transmittance spéculaire n'en dépendant pas fonctionne)
- Une gestion correcte de l'anisotropie. Celle de 3ds Max et de Mitsuba Renderer diffère trop pour pouvoir faire un transfert correct entre les deux, mais un transfert partiel serait mieux que rien.
- La Transluminescence, ou Subsurface Scattering.

## Éclairages

L'environnement map n'est pas exporté dans le FBX.

Les objets émissifs ne sont pas non plus pris en compte. Dans le cas d'objets texturés pour leur émissivité, Mitsuba ne semble pas proposer de solution, mais par contre supporte le fait qu'un objet dans son ensemble puisse émettre de la lumière. La principale difficulté pour l'implémenter vient du fait que du côté de 3ds Max, c'est une propriété d'un matériau, et que pour Mitsuba Renderer, c'est une propriété d'une géométrie.

L'éclairage ambiant est dans les propriétés générales de la scène, ça devrait être assez rapide à implémenter.

Les projecteurs de 3ds Max supportent l'ajout d'une texture, et ça tombe bien, ceux de Mitsuba aussi ! Devrait également être assez rapide à implémenter.

# Améliorations possibles

## Interface graphique

Pour des raisons d'ergonomie et de simplicité d'accès, il serait bon de mettre en place une interface graphique simple, pour permettre l'utilisation du programme à un plus grand nombre.

Une fois lancée, cette interface vérifierait la version de Python, installerait Pillow si nécessaire, et permettrait, via une boite de dialogue simple, de paramétrer et de lancer la conversion.

Pour le moment, launcher.bat s'occupe d'installer Pillow si nécessaire, mais ne vérifie pas la version de Python. converter.py vérifie la version de python et quitte si ce n'est pas la 3.

## Plus de types d'objets

Pour l'instant, tous les types d'objets ne sont pas pris en compte. Les détails sont dans la section «Fonctionnalités manquantes». Le fichier FBX contenant des informations limitées, il faudra dans un premier temps récupérer tout ce qui est possible de récupérer. L'utilisation d'un autre format (ASE par exemple) pour compléter les information peut également être envisagé. L'exemple de l'environnement mapping, présent dans le ASE mais pas dans le FBX, est un bon exemple des limitations du format.

## Programme plus générique, code plus court.

À l'heure actuelle, les modèles de type caméra et lumières sont placés par light_cam_builder. Il serait logique que models_builder s'occupe de les placer, tout comme il s'occupe de placer les modèles référençant de la géométrie.

La partie materials_builder est très linéaire dans son exécution, avec beaucoup de code se ressemblant, il est sans doute possible de la rendre plus générique.

## Conversions plus précises

Le programme utilise actuellement des algorithmes arbitraires et approximatifs pour la conversion de la carte de glossiness et de la couleur exprimée en Kelvin. Il faudrait raffiner ces algorithmes pour plus de fidélité à la scène originale. Même chose pour le simple paramètre non texturé de roughness.
