# Lecteur optique — diagnostic initial

## Observation du 1 octobre 2026

À 21:29:44 UTC, les interfaces sysfs et le journal identifient `/dev/sr0` comme **PLDS DG-16D2S**, révision SCSI `0251`, identification ATAPI `02510C`. Le périphérique est dans l'état noyau `running`. Il est attaché au port ATA1 ; le disque Hitachi interne est ATA2. L'utilisateur précise ensuite : **le tiroir s'ouvre, mais aucun disque n'est lu**.

L'identification confirme une communication avec l'électronique du lecteur. Elle ne valide ni le déplacement de la tête, ni la rotation, ni la mise au point du laser, ni la lecture d'un secteur. Aucune commande d'éjection, de réinitialisation, d'écriture ou de lecture de disque n'a été envoyée pendant cette collecte.

## Pourquoi Linux affiche une capacité DVD nulle

`/proc/sys/dev/cdrom/info` affiche une vitesse de 1 et `Can read DVD: 0`. Le journal du démarrage contient `scsi-1 drive`.

Dans la source exacte `drivers/scsi/sr.c`, fonction `get_capabilities`, ce message est émis lorsque la requête de page de capacités `0x2a` échoue ou donne des longueurs invalides. Ce chemin impose la vitesse de repli 1 et masque plusieurs capacités, dont DVD. **Il ne mesure pas la vitesse réelle et ne prouve pas une incapacité physique à lire des DVD.** Les données conservées ne disent pas laquelle de ces conditions a échoué.

Référence de code : `techflashYT/linux-custom@a293dd19311668900eb1eeb2f6cb01dcac54f330`, `drivers/scsi/sr.c`, lignes 838–852. Preuve vivante : `evidence/2026-10-01/boot-preflight/optical-inventory.json`.

## Prochaines vérifications

Après stabilisation du nouvel essai de démarrage, relever les erreurs précises du lecteur avec les commandes standards du pilote, puis essayer un support connu fonctionnel avec l'utilisateur. Comparer la détection du support, la rotation observée et les erreurs de lecture. Sans ces éléments, laser, mécanique, média, firmware et transport restent des hypothèses.

Une réparation mécanique ou optique éventuelle nécessite une intervention physique. Ne pas modifier au hasard les réglages du laser ni flasher le lecteur pour tester une hypothèse. La lecture des secteurs et l'exécution d'un jeu sont deux validations distinctes ; aucun fonctionnement de jeu sur disque n'est démontré à ce stade.
