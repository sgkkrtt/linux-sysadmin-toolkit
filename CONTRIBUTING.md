# Contribuer

Décrivez d’abord le problème et un exemple reproductible, sans publier de chemins sensibles ni de données personnelles. Une nouvelle commande doit avoir une aide, une documentation et des tests pour ses erreurs.

Exécutez `make check` avant de proposer une modification. Les tests doivent rester sans privilèges et ne pas toucher aux services ou aux fichiers du système. Gardez les dépendances limitées et évitez les actions destructrices implicites.
