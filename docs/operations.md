# Exploitation et restauration

## Avant la sauvegarde

Choisissez un dossier de données stable et une destination privée. Vérifiez l’espace disponible et les droits. Pour une base de données, utilisez d’abord son export natif. Effectuez une simulation, relisez les deux chemins, puis utilisez `--apply`.

Conservez une copie hors de la machine : une archive sur le même disque ne protège pas d’une panne de ce disque. Les données restent en clair ; ne placez pas de secrets dans un emplacement partagé.

## Vérifier et restaurer

Pour une archive produite par cet outil et dont vous connaissez l’origine :

```bash
cd "$HOME/backup-lab"
sha256sum -c backup-REMPLACER.tar.gz.sha256
tar -tzf backup-REMPLACER.tar.gz
mkdir -m 700 restore-review
tar -xzf backup-REMPLACER.tar.gz --no-same-owner --no-same-permissions -C restore-review
```

Remplacez le nom par celui de votre archive. Examinez les fichiers dans `restore-review` avant de les recopier. N’extrayez pas une archive inconnue avec `sudo`. Comparez un fichier représentatif à l’original et ouvrez-le avec l’application habituelle. Répétez cet exercice régulièrement.

## Contrôle périodique du disque

Les fichiers systemd fournis utilisent un utilisateur `toolkit` à créer par l’administrateur et une copie du projet dans `/opt/linux-sysadmin-toolkit`. Ce sont des exemples, pas un installateur.

Adaptez `User`, `WorkingDirectory`, le chemin Python et le seuil. Vérifiez les unités avec `systemd-analyze verify`, puis copiez-les dans `/etc/systemd/system/`. Après relecture, rechargez systemd et activez le timer : `sudo systemctl daemon-reload` puis `sudo systemctl enable --now toolkit-disk.timer`.

Consultez `journalctl -u toolkit-disk.service` et `systemctl list-timers`. Un seuil dépassé fait échouer le service ; aucun courriel ni alerte externe n’est envoyé. Pour annuler : `sudo systemctl disable --now toolkit-disk.timer`, retirez les deux unités et rechargez systemd.
