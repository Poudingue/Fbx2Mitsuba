# Manuel d'utilisation

## Intro

Ce programme transforme une scène 3ds Max en une scène Mitsuba Renderer. En suivant correctement les étapes décrites dans ce manuel, vous devriez obtenir un fichier xml ouvrable avec le logiciel Mitsuba Renderer correspondant à la scène d'origine.

Tout n'est pas convertissable à l'heure actuelle. Les matériaux peuvent être mal rendus, des lumières et des caméras risquent d'être mal placées ou absentes, ainsi que plein d'autres défauts de transfert. Une partie de ces problèmes pourront être réglés dans des versions futures du logiciel, mais pour l'instant, afin de vous assurer un meilleur transfert, il est recommandé de s'assurrer que votre scène 3D remplit plusieurs critères.

## Prérequis de la scène 3D

- Les lumières doivent être de type photométrique, soit projecteur, soit omnidirectionnel. Les lumières omnidirectionnelles peuvent avoir une forme sphérique.
- Les caméras doivent être de type target, les caméras de type physical ne sont pas transférées.

- Les lumières et caméras ne doivent pas être dépendantes de la hiérarchie, ou leur emplacement dans l'espace risque d'être incorrect.
- Les matériaux doivent être de type physical. L'anisotropie et la transluminance ne sont pas supportées pour l'instant.
- L'usage des textures procédurales 3ds Max est à éviter, seule l'utilisation de bitmaps est supportée.

## Étapes

- Assurez-vous d'avoir python 3 installé sur votre ordinateur. Si ce n'est pas le cas où que vous ne savez pas, vous pouvez le télécharger sur le site officiel https://www.python.org/
- Conformez au maximum votre scène aux prérequis cités plus haut.
- Exportez la scène 3D au format FBX. Dans la fenêtre d'export, sous «options avancées» puis «Format du fichier FBX», sélectionnez le type «ASCII». Évitez de modifier d'autres options pour des raisons de compatibilité.
- Vous pouvez normalement lancer la conversion de scène en glissant simplement le fichier FBX exporté sur launcher.bat.

## Résultat

Si tout s'est déroulé correctement, la console devrait s'être refermée automatiquement, et un dossier export devrait être apparu à l'emplacement du fichier FBX. Ce dossier contient la scène Mitsuba Renderer, ainsi qu'un dossier contenant les textures utilisées, et un dossier contenant les modèles 3D. Si vous souhaitez déplacer la scène, veillez à prendre le dossier dans son intégralité.