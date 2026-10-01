# Carte de recherche de l'exemplaire

Cette carte organise l'objectif courant ; elle ne remplace pas les preuves datées dans STATE et EXPERIMENTS. « Source » signifie code examiné, « mesure » signifie observation de cet exemplaire. Une identification logicielle ne remplace pas les marquages physiques des puces.

| Bloc | Acquis et nature de preuve | Inconnues / prochaine preuve utile |
|---|---|---|
| Révision et puces | Signature PCI GPU compatible famille Jasper ; inventaire de 12 fonctions | Photographies et marquages carte mère, RAM, flash, Southbridge ; révision exacte |
| CPU et interruptions | Six threads visibles ; code et binaire du callback IPI analysés, correctif inclus dans obsidian4 | Topologie exposée, affinités IRQ, mesures de charge ; portée réelle du callback corrigé |
| RAM / DMA | Pages noyau 64 Kio ; audit des chemins DMA et allocations graphiques | Cartographie des réservations, contraintes cohérence/cache, mesures de débit séparées du langage |
| GPU / HDMI | Bureau 720p et allocation corrigée mesurés ; f1/f2 libxenon tracés hors matériel | Horloges et ANA/HANA 1080p, modes complets, accélération 2D/3D et format des commandes |
| Boot / sécurité | Chaîne stock → jeu → patchs temporaires → XeLL → noyau → HDD observée | Versions précises du chargeur de cet exemplaire, démarrage indépendant, récupération avant toute substitution |
| ROM / hyperviseur / dashboard | Dépendances de la chaîne courante identifiées fonctionnellement | Analyse des composants exacts ; aucune connaissance exhaustive des interfaces ou du silicium |
| NAND | Sonde BAR1 gelante archivée, défaut de tampon HTTP source identifié hors matériel | Acquisition restaurable adaptée au type de flash ; ECC, blocs défectueux, concordance des lectures ; aucune répétition du mmap |
| SMC / thermique / alimentation | Températures via hwmon, requêtes d'état historiques, défaut de cache corrigé | Contrats de concurrence et délais ; mesure de consommation nécessite un instrument ; protections intactes |
| Ethernet | Liaison 100 Mbit/s full duplex et SSH observés ; GRO désactivé | Débit et stabilité prolongée ; mécanisme du watchdog historique non établi |
| SATA / stockage | Racine ext4 interne et swap fonctionnels | Débit réel contrôlé, distinction cache/disque, détails du contrôleur et structure des sauvegardes historiques |
| DVD | PLDS DG-16D2S 0251 ; tiroir fonctionne selon utilisateur, pas de lecture | Réponse SCSI de capacités, erreurs de lecture sur support connu bon, optique/moteur ; firmware exact non acquis |
| USB / commandes | Clavier et manette identifiés ; événements observés historiquement | Validation physique sous obsidian4, répétition clavier, cohérence HID et latence |
| Audio | Source historique examinée ; noyau avec son désactivé | Portage API, revue DMA/IRQ, compilation et test sonore réel |
| Linux / bureau | obsidian4, Xorg/IceWM et udev vérifiés | Référence CPU/mémoire/démarrage, signatures pacman, coût du lanceur et choix des composants |
| Rust / remplacements | Liberté de réimplémentation explicitement demandée | Sélection d'un composant, cible PowerPC et ABI vérifiées, bénéfice comparé ; pas de réécriture sans justification |

Pour chaque expérience : conserver code exact, versions, commandes, erreurs, empreintes, résultat et limites. Un dump confidentiel reste dans les espaces ignorés ; publier uniquement les métadonnées et analyses partageables. Le lecteur suivant doit pouvoir distinguer observation de la console, simulation locale et hypothèse, et retrouver un chemin de récupération réellement validé.
