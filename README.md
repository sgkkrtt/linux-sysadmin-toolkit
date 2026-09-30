# Linux Sysadmin Toolkit

Un petit atelier d’administration Linux : comprendre l’état d’une machine, repérer un disque qui se remplit et sauvegarder un dossier sans modifier le système par surprise.

Le projet utilise Python et sa bibliothèque standard. Pas de compte cloud, pas d’agent à installer, pas de service distant. Les commandes renvoient du JSON pour pouvoir être utilisées dans un script ou conservées dans un rapport.

## Démarrer

Linux, Python 3.11 ou supérieur. Les diagnostics et les tests ne nécessitent pas `sudo`.

```bash
git clone https://github.com/sgkkrtt/linux-sysadmin-toolkit.git
cd linux-sysadmin-toolkit
python3 -m sysadmin_toolkit inventory
python3 -m sysadmin_toolkit disk --path / --threshold 85
make check
```

L’installation est facultative : `python3 -m venv .venv`, puis `.venv/bin/pip install .` rend la commande `.venv/bin/linux-toolkit` disponible.

## Ce que les commandes font

| Commande | Usage | Écrit sur disque ? |
| --- | --- | --- |
| `inventory` | Hôte, noyau, architecture, CPU, charge et mémoire | Non |
| `disk` | Espace disponible et alerte à partir d’un seuil | Non |
| `backup` | Prépare une sauvegarde d’un dossier | Seulement avec `--apply` |

### Sauvegarder un dossier

```bash
mkdir -p "$HOME/backup-lab"
python3 -m sysadmin_toolkit backup --source ./docs --destination "$HOME/backup-lab"
# Après avoir relu les chemins :
python3 -m sysadmin_toolkit backup --source ./docs --destination "$HOME/backup-lab" --apply
```

L’archive reçoit un nom unique, des permissions privées et un fichier SHA-256. Aucun fichier existant n’est remplacé. Les liens symboliques et fichiers spéciaux sont exclus. La destination doit déjà exister et se trouver hors de la source. La racine `/` est refusée.

Codes de sortie : **0** succès, **1** seuil disque atteint, **2** erreur d’utilisation ou d’exécution. Le JSON est écrit sur stdout, les erreurs sur stderr.

## Structure

- `sysadmin_toolkit/` : commandes et logique métier ;
- `tests/` : tests isolés dans des dossiers temporaires ;
- `examples/systemd/` : contrôle disque périodique ;
- `docs/` : choix techniques, procédure de restauration et scénario de démonstration ;
- `.github/workflows/` : validation automatique sous Python 3.11 et 3.12.

## Pour présenter le projet

Commencez par [la démonstration](docs/demo.md), puis expliquez pourquoi la sauvegarde simule son travail par défaut. Les [choix techniques](docs/design.md) détaillent les compromis. La [procédure d’exploitation](docs/operations.md) décrit la vérification et la restauration.

Cette première version reste volontairement limitée : pas de chiffrement, de rotation automatique, de sauvegarde incrémentale ou de restauration automatisée. Elle n’est pas une sauvegarde complète d’un serveur. Les applications doivent être arrêtées ou sauvegardées avec leurs propres outils pour garantir des données cohérentes.
