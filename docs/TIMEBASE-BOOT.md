# Candidat de correction d’horloge : préparation E71

Le noyau `6.18.11-xenon-obsidian-clock` est préparé séparément sur le disque interne et la clé USB. Il reprend obsidian4 avec le correctif optionnel 0016, sans les changements audio expérimentaux. L’option `xenon_tb_hz=49875000` ajuste la conversion des ticks ; elle ne programme pas l’oscillateur ni les tensions. La mesure de référence et les limites sont dans [TIMEBASE-CALIBRATION.md](TIMEBASE-CALIBRATION.md).

## Construction et contrôle

La console répond sous obsidian4 avant préparation ; racine interne ext4, clé ARCH vfat distincte, aucun service en échec listé. Les 65 modules candidats et l’image ont été emballés depuis la sortie E70 après comparaison de chaque empreinte. Archive reçue avec empreinte identique, extraite dans un nouveau répertoire de travail sans écraser les modules actifs.

`depmod -e -E` et `mkinitcpio --nopost` réussissent, sans erreur ni avertissement de compilation de l’image. La configuration reprend les hooks base, udev, modconf, block, filesystems, keyboard et fsck, avec compression zstd niveau 1. La commande d’analyse de l’image a initialement émis un diagnostic d’affichage `tput` lié à TERM absent, sans échec de génération ; les inspections suivantes utilisent TERM=dumb.

L’initramfs fait **16 171 806 octets**, sous la limite de 32 Mio du LibXenon étudié. SHA-256 : `0f2bea5579d397127a75b9daa27aa724a24deb2d2be3984749de64c16e937eef`. L’extraction contient uniquement le répertoire de version attendu et **43 modules**, tous comparés octet pour octet par SHA-256 aux modules E70. Six programmes essentiels sont ELF32 PowerPC big-endian et leurs chemins résolus restent dans l’image extraite. Présence de /init et du hook udev vérifiée.

Image noyau SHA-256 : `85b39fd069950625ad6e6cb8f5c17c71aa2755c7d325d3459cf848b69fa241cb`. Les empreintes et les commandes exactes sont dans `evidence/2026-10-02/timebase-boot/`.

## Disposition préparée

- Modules : `/usr/lib/modules/6.18.11-xenon-obsidian-clock`, nouveau répertoire, 65 empreintes revérifiées.
- Clé : `obsidian-clock/kernel` et `obsidian-clock/initrd`.
- Menu : nouvelle entrée **obsidian_clock**, 168 octets, avec la même racine que l’entrée obsidian4 et l’option de cadence à 49 875 000 Hz.
- Menu précédent sauvegardé dans `Recovery/kboot-before-obsidian-clock.conf`.
- Défaut **linux_hdd conservé** ; entrées obsidian4 et récupération existantes conservées. Huit fichiers de démarrage/récupération préexistants restent aux empreintes relevées avant copie.

Une seconde lecture après démontage/remontage en lecture seule confirme les nouveaux fichiers, les secours et le menu ; la copie Mac de l’initramfs a la même empreinte. SSH reste sous obsidian4, aucun service en échec listé.

Le menu est écrit seulement après vérification des deux fichiers nouveaux et des modules. Le fichier temporaire du menu est synchronisé puis renommé ; la clé est synchronisée et démontée. Cela réduit les possibilités d’une entrée pointant vers une copie incomplète, sans constituer une garantie contre toute panne physique. Les procédures exactes sont archivées comme texte sous `research/archive/`, pour audit et non pour répétition automatique.

## Essai physique requis

1. Éteindre normalement la console et débrancher Ethernet.
2. Relancer Rock Band Blitz, choisir USB si demandé, puis sélectionner explicitement **obsidian_clock** dans XeLL.
3. Rebrancher Ethernet seulement après arrivée au bureau Linux.
4. Vérifier par SSH la version obsidian-clock, l’option de démarrage, le message de calibration, la racine et les services ; refaire les sept échantillons de cadence sur 60 secondes avec le même outil qu’E69.

Si cette entrée bloque, revenir par un démarrage physique à **obsidian4**, qui a déjà atteint le bureau. linux_hdd et la récupération sont aussi conservés, mais leur simple présence ne démontre pas une nouvelle validation de démarrage. Aucun redémarrage n’est envoyé par les procédures de préparation. Aucun firmware/NAND/eFuse modifié.

**Limite actuelle : fichiers préparés, candidat pas encore démarré.** La réduction effective de dérive, le bureau et les entrées utilisateur sous ce noyau restent à vérifier. Les horodatages console des rapports sont laissés tels quels et doivent être interprétés avec les horodatages hôte, compte tenu du défaut mesuré E69.
