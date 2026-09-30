# Démonstration en quelques minutes

1. Lancez `python3 -m sysadmin_toolkit inventory`. Expliquez la différence entre nombre de CPU et charge moyenne, puis observez la mémoire disponible.
2. Lancez `python3 -m sysadmin_toolkit disk --threshold 85`. Identifiez l’espace libre et le code de sortie avec `echo $?`.
3. Créez un dossier temporaire et un fichier texte sans données personnelles. Simulez sa sauvegarde vers un autre dossier, puis constatez que rien n’a été créé.
4. Recommencez avec `--apply`, vérifiez le SHA-256 et restaurez dans un dossier vide avec la procédure d’exploitation.
5. Lancez `make check`. Montrez le test qui refuse une destination à l’intérieur de la source.

Pour votre présentation, gardez vos propres résultats et expliquez une limite rencontrée. Les tests automatisés sont des validations locales, pas la preuve d’un déploiement en production.
