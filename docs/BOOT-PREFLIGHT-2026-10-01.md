# Préparation et essai du candidat obsidian4

## État de la console avant préparation

SSH vérifié le 1 octobre à 21:21:44 UTC : noyau `6.18.11-xenon`, racine `/dev/sda1` ext4, aucun service en échec. La clé ARCH a été montée en lecture seule pour relever les empreintes, puis démontée. Son noyau fonctionnel, l'initramfs du système installé et la récupération live étaient présents.

L'initramfs de `/boot` et celui du répertoire USB `linux-hdd` ont des empreintes différentes ; la clé conserve l'image antérieure qui a servi au démarrage fonctionnel. Ils n'ont pas été synchronisés ni remplacés pendant cette préparation.

## Construction et vérifications

Le correctif 0007 exclut `zImage.xenon` de la recette générique concurrente et retire la copie vers un chemin TFTP local du développeur amont. Le candidat **6.18.11-xenon-obsidian4** se construit sans avertissement pour les trois cibles vmlinux, modules et zImage.xenon. Les 65 modules sélectionnés sont vérifiés ; les six sections contrôlées restent identiques entre noyau et image. Preuves dans `kernel-build-obsidian4/`.

Les modules ont été transférés dans `/var/tmp/obsidian4-preflight-20261001/root`, après contrôle SHA-256 de l'archive. `depmod -e -E` n'a signalé aucune erreur de symbole/version. `mkinitcpio 40` a généré l'image avec un répertoire de modules distinct, le suffixe exact et `--nopost`, sans preset ni écriture dans `/boot`.

L'initramfs fait 16 169 156 octets, SHA-256 `87c91934ead6d828fcaaf0bc5b6bfe78fc011c8a895b53441cdfb404f208e7b5`. Ses 43 modules ont été extraits et comparés individuellement aux modules candidats. Les exécutables essentiels contrôlés sont ELF32 PowerPC big-endian ; les chemins vérifiés restent à l'intérieur de l'image extraite. La copie rapatriée sur le Mac a la même empreinte.

SATA Xenon, SCSI, disque bloc, ext4, USB OHCI/EHCI, réseau sis190 et décompression zstd sont intégrés à la configuration du noyau. Cela ne remplace pas un essai de démarrage réel.

Le libxenon étudié fixe une limite d'initrd à 32 Mio (`a333adef440f28b436a667be0a4f014afce6349d`, `libxenon/drivers/elf/elf.c`). Le candidat reste en dessous. Le parser kboot étudié limite chaque entrée à 255 octets ; l'entrée préparée reste en dessous. Ces vérifications de sources ne prouvent pas l'identité binaire complète du XeLL exécuté.

## Fichiers effectivement préparés sur la console

À 21:29:51 UTC, les contrôles après copie confirment :

- Modules dans `/usr/lib/modules/6.18.11-xenon-obsidian4`, sans remplacement du répertoire du noyau fonctionnel.
- Sur la clé : `obsidian4/kernel` et `obsidian4/initrd`, empreintes conformes au candidat.
- Ancien menu sauvegardé dans `Recovery/kboot-before-obsidian4.conf`.
- Entrée `obsidian4` ajoutée ; **`default=linux_hdd` conservé**.
- Noyau, initramfs et récupération préexistants de la clé toujours aux mêmes empreintes.
- Clé démontée après synchronisation. Aucun redémarrage envoyé par script.

Le menu effectivement écrit est décrit par `boot-preflight/menu-plan.json` et confirmé par `staging-result.json`. Le premier fichier porte `installed: false` car il décrit la préparation avant copie ; le résultat daté de staging est l'état ultérieur faisant foi. La procédure exécutée est archivée dans `research/archive/stage-obsidian4.py.txt` pour audit, **pas pour être rejouée**.

## Essai utilisateur et retour au système fonctionnel

L'utilisateur a indiqué qu'il lançait l'essai : démarrer sans Ethernet, lancer Rock Band Blitz, choisir USB si demandé, puis sélectionner `obsidian4` dans XeLL, et rebrancher Ethernet une fois Linux affiché. Le premier contrôle SSH après cette réponse expire ; cela est compatible avec la phase sans réseau et ne prouve ni un gel ni un succès.

La validation attendue est `uname -r` égal à `6.18.11-xenon-obsidian4`, racine interne, bureau actif, entrée clavier/manette et journaux sans nouvelle erreur critique. Le retour au noyau précédent passe par l'entrée `linux_hdd`, toujours par défaut. La récupération live reste disponible. Aucun démarrage autonome depuis la mise sous tension n'est encore validé.

### Résultat intermédiaire fourni par l'utilisateur

La photo IMG_1372 montre `Run /init as init process`, le démarrage de systemd-udevd 259-2-arch, `Triggering uevents...`, puis la détection de SanDisk et de sdb1. La dernière ligne visible est horodatée 4,016710 secondes après démarrage. Aucun message de panique noyau n'est visible. L'utilisateur confirme ensuite que l'écran reste bloqué et ne se souvient pas d'avoir choisi une entrée.

Le menu ayant conservé linux_hdd par défaut, il est impossible de savoir à partir de cette photo si le candidat a été lancé. L'analyse locale de l'initramfs candidat montre que le hook udev déclenche les événements puis appelle `udevadm settle`, avant la résolution et le montage de la racine. Cela situe une piste de diagnostic ; la photo ne distingue pas une attente udev d'un blocage noyau et ne démontre pas une erreur de disque.

Récupération demandée : extinction physique, redémarrage sans Ethernet, sélection explicite de linux_hdd si le menu apparaît, Ethernet après le bureau. Aucune nouvelle modification à distance n'est envoyée pendant cette récupération. Preuve : `boot-preflight/first-boot-observation.json`, photo conservée hors Git.

## Démarrage candidat confirmé — E38

L'utilisateur a finalement repéré le menu XeLL et choisi obsidian. Il confirme l'arrivée au bureau. SSH identifie ensuite `6.18.11-xenon-obsidian4` ; la collecte datée de 21:45:47 UTC indique 132 secondes d'uptime, racine interne ext4 et zéro service en échec. Xorg et IceWM sont actifs, XRandR indique 1280 × 720, udev est actif et sa file se vide dans le délai de cinq secondes. Aucun watchdog réseau ni panique dans les avertissements collectés de ce démarrage.

Le journal `Using 1280x720 (398000) fb` confirme que le chemin d'allocation corrigé est exécuté : 1280 × 736 × 4 = 3 768 320 octets, contre 3 686 400 historiquement. Cela valide l'activation du changement sur la machine ; cela ne démontre pas à lui seul l'absence de toute corruption graphique. Les avertissements précoces ioremap/rodata subsistent ; pas de prétention à un journal sans avertissement.

Preuves : `evidence/2026-10-01/obsidian4-first-boot/{runtime,validation}.json`. La collecte ne lit aucun BAR ni NAND. Aucun redémarrage ni modification de configuration envoyé. Le défaut du menu n'a pas été changé. La cause du gel précédent reste inconnue ; le retour de linux_hdd n'a pas été testé dans cette séquence. L'usage visible de la manette, les redémarrages répétés et la stabilité sous charge restent à établir.
