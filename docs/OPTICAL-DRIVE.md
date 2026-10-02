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

## 2 octobre 2026 — CD audio lisible (E44)

L’utilisateur a inséré un CD musical. Sa lisibilité préalable sur un autre appareil n’a pas été confirmée. Sous `6.18.11-xenon-obsidian4`, `CDROM_DRIVE_STATUS` renvoie 4 (`CDS_DISC_OK`), et `CDROMREADTOCHDR` annonce les pistes 1 à 20. Les entrées TOC indiquent uniquement des pistes audio, avec lead-out au LBA 263934.

L’outil original `tools/inspect-audio-cd.py` utilise le pilote CDROM standard en lecture seule : table des pistes, puis un secteur de 2 352 octets à chacun des LBA 150, 123793 et 249235. Tous réussissent avec données non nulles. La relecture du LBA 150 a exactement la même empreinte. Durées monotones mesurées de 0,091 à 0,207 s par appel, sans benchmark de débit. Les horloges murales du Mac et de la console diffèrent ; les deux horodatages sont conservés sans les confondre.

**Mesure directe : le chemin de lecture CD fonctionne pour ces échantillons.** Cela réfute une incapacité absolue à lire tout support au moment du test. Cela ne valide ni tout le CD, ni le chemin DVD, ni l’authentification/exécution Xbox, ni la sortie audio du système. Aucun réglage, flashage, redémarrage ou réparation matérielle effectué. Le noyau conserve sa configuration audio désactivée.

**Hypothèses restantes :** problème propre au support initial, à la lecture DVD, au firmware ou au chemin Xbox. Le succès CD ne distingue pas ces hypothèses. Une comparaison avec DVD vidéo connu fonctionnel est demandée ; à défaut, un jeu original permettra une observation plus limitée.

Reproduction : sur Linux avec un CD audio inséré, `timeout -k 2 45 python3 tools/inspect-audio-cd.py`. L’outil refuse une cible autre que `/dev/sr0` de type optique, borne les lectures à quatre secteurs, ne stocke ni ne publie leur contenu. Un timeout de processus ne garantit pas l’interruption instantanée d’une opération bloquée dans le noyau. Références ABI : `include/uapi/linux/cdrom.h`, `drivers/scsi/sr_ioctl.c`, `drivers/cdrom/cdrom.c` du commit noyau indiqué dans `optical-cd/method.json`.

## 2 octobre 2026 — Just Cause 2 non reconnu (E45)

Après remplacement du CD par le jeu Xbox 360 Just Cause 2, le statut CDROM devient 1 (`CDS_NO_DISC`). Une lecture standard au LBA 0 échoue avec EIO ; aucune donnée de jeu récupérée. La commande standard `TEST UNIT READY`, sans transfert de données, donne statut SCSI 2, host_status 0, driver_status 8 et sense fixe `02/3a/00` : NOT READY / MEDIUM NOT PRESENT. Le code noyau confirme ce libellé dans `drivers/scsi/sense_codes.h:461`.

L’ancienne taille sysfs correspond encore au CD audio : **ne pas l’interpréter comme la capacité du jeu**. Le noyau effectue de la lecture anticipée lors du pread ; la requête de 2 048 octets ne signifie pas exactement un secteur demandé au lecteur.

Conclusion mesurée : CD partiellement lisible, jeu DVD non reconnu pendant cet essai. Hypothèses encore ouvertes : état de ce disque, détection/mise au point DVD, autres éléments optiques/mécaniques ou firmware. Ni panne laser certaine, ni problème d’authentification démontré. Aucun firmware changé. Prochain test discriminant : DVD vidéo connu fonctionnel, puis autre DVD si possible. Outil reproductible : `timeout -k 2 15 python3 tools/optical-ready.py` ; cinq tests de décodage hors matériel dans `research/tests/check-optical-sense.py`.
