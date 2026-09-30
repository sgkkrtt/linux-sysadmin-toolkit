# Choix techniques

## Une base courte, facile à relire

Python permet de produire du JSON, de tester les erreurs et de créer des archives sans assembler des commandes shell. Le programme ne lance aucune commande externe et ne modifie ni comptes, ni pare-feu, ni services.

Les trois commandes répondent à des tâches quotidiennes : inventaire, capacité disque et copie de secours. Ajouter un outil doit répondre à un besoin concret et apporter ses tests avant de grossir le catalogue.

## Garde-fous

La sauvegarde nécessite `--apply`. Une simulation ne crée aucun fichier. Un fichier temporaire unique évite les écrasements ; ses permissions sont 0600. Les liens et fichiers spéciaux ne sont pas sauvegardés. Aucun mécanisme de suppression ou de rétention n’est inclus.

La source doit être stable et sous votre contrôle : il ne s’agit pas d’un instantané et les vérifications de chemins ne protègent pas contre toutes les substitutions concurrentes. Ne lancez pas l’outil en root sur un dossier qu’un autre utilisateur peut modifier. Les archives ne conservent pas les ACL, attributs étendus ou contextes SELinux. SHA-256 détecte une modification, mais ne prouve pas l’authenticité.

## Validation

Les tests couvrent la simulation, le contenu de l’archive, le checksum, les permissions, les chemins interdits, les liens symboliques et les codes d’erreur. Le contrôle disque est testé avec des valeurs simulées : il n’est pas nécessaire de remplir réellement un disque.

La CI exécute la même suite sur deux versions de Python. Elle ne prouve pas à elle seule la compatibilité avec chaque distribution Linux. Les exemples systemd doivent être adaptés et vérifiés sur la machine cible.
