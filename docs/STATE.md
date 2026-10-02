# État courant — 2 octobre 2026

## Longueurs audio corrigées et protocole à vérifier — E62

Le correctif 0014 adopte les longueurs en octets exacts, appuyées par un correctif LibXenon de 2010 et le pilote SiS ALSA. Les 16 384 descripteurs testés sur 512 tailles ont des longueurs alignées ; quinze scénarios de l'adaptateur et vingt de ressources repassent. Noyau audio-bytes + 70 modules vérifiés, construction finale sans avertissement sur un volume Linux après deux incidents d'horodatage Mac/Linux.

La correspondance de registres SiS est une hypothèse étayée par le code, pas une mesure Xbox. La référence distingue fin d'accès mémoire et fin de sortie sonore ; statut mémorisé/acquittement et FIFO restent à résoudre avant activation. Voir `docs/AUDIO-REGISTER-HYPOTHESIS.md`. Dernier état vivant inchangé : E61.


## Adaptateur audio candidat — E60 ; contrôle vivant E61

Le correctif 0013 relie la file aux engagements ALSA, au drain et aux resets ; `.pointer` ne touche plus aux registres. Quinze scénarios de callbacks, vingt de ressources et la régression complète de la file passent hors console. La fin du dernier descripteur reste non décodée : le test de stagnation produit un XRUN, aucun succès audio revendiqué. Voir `docs/AUDIO-ALSA-ADAPTER.md` ; aucun chargement.

Noyau `6.18.11-xenon-audio-submit` et 70 modules compilés sans avertissement à 10:52:58 UTC ; formats ELF PowerPC et vermagic vérifiés. Aucune installation ni image de démarrage produite.

E61 : SSH vérifié à 2026-10-02T10:49:58.112905+00:00 sous obsidian4, uptime 9 327,35 s, aucune unité en échec listée, framebuffer 1280 × 720. Réactivité visuelle non testée ; aucune configuration matérielle changée.


## File audio logicielle — E59

Un nouveau composant C original distingue blocs prêts, données partielles et silence de fin de flux. Vérifié sur 512 tailles, 54 008 opérations et 24 544 033 frames synthétiques ; ASan/UBSan et analyse statique sans diagnostic après correction d’un réglage d’outillage. Compilation et liaison PowerPC contre le noyau réussies. Il reste séparé de snd-xenon : adaptateur ALSA et fin réelle des blocs DMA non validés, aucun son activé. Voir `research/audio/README.md`.

E58 : 96 cas reproduisent une file modifiée par des demandes de position identiques ; débordement de conversion signé également reproduit avec une valeur synthétique native 64 bits. Aucun défaut vivant revendiqué. Le contrôleur audio de l’émulateur Xenon examiné est un stub et ne valide pas le protocole. Soumission et fin de flux à résoudre avant activation ; voir `docs/AUDIO-SUBMISSION-AUDIT.md`.

## Suivi audio compilé et soumission à corriger — E57/E58

Le correctif 0012 arme un timer par flux, compte la progression réelle entre observations et attend les callbacks avant libération. Quinze scénarios de suivi, vingt de ressources et quinze PCM passent hors console. La variante finale active les timers haute résolution ; noyau et 70 modules compilent sans avertissement, ELF et versions vérifiés. Aucun chargement. Voir `docs/AUDIO-STREAM-POLLING.md`. Dernier état vivant : E56.

## Tampons audio et retour utilisateur — E55/E56

E55 : le candidat 0011 utilise les tampons cohérents gérés par ALSA, sans remappage ioremap ni boucle de cache privée. Vingt scénarios de ressources et douze de callbacks passent ; noyau audio-pcm et 70 modules compilés sans avertissement. Aucun installé : timer, concurrence et protocole matériel restent à résoudre. Voir `docs/AUDIO-PCM-DMA.md`.

E56 : SSH revérifié à 2026-10-02T09:40:09.815799+00:00 : obsidian4, uptime 5 139,44 s, aucun service en échec, framebuffer 1280 × 720. Réactivité visuelle non testée. L’utilisateur est de retour ; aucune manipulation physique requise pour poursuivre ces tests hors console.

## Envoi SMC borné et builds audio — non installés

E54 : nouvelle voie d’envoi audio avec refus immédiat des verrous occupés et budget de polling ; dix-neuf scénarios SMC et dix-huit scénarios de ressources audio passent hors matériel. Les noyaux audio-lifecycle (0008/0009) et audio-post (0008/0009/0010) compilent avec 70 modules chacun, sans avertissement. Export SMC et vermagic vérifiés. Aucun son ni démarrage de ces variantes ; le dernier état vivant reste E52. Les anciens chemins SMC conservent leurs attentes sans borne. Voir `docs/SMC-BOUNDED-POST.md`.

## Portage audio en cours, hors console

E53 : correctif 0009 après 0008 ; objet PowerPC compilé sans avertissement, douze défaillances attendues reproduites dans treize scénarios originaux, seize scénarios du candidat passent avec contrôle des ressources et ASan/UBSan. La comparaison LibXenon révèle une divergence d’encodage des longueurs et une limite mémoire basse possible ; elles doivent être résolues avant activation. Compilation noyau/modules suivie séparément. Dernier état vivant : E52. Voir `docs/AUDIO-LIFECYCLE-AUDIT.md`.

## Dernier contrôle vivant et audit audio

E52 : retour sous obsidian4 confirmé le 2 octobre à 08:17:42 UTC, uptime 201,58 s, zéro unité en échec, XRandR répond en 720p. OpaqueMove/Resize restent à 1. Le lanceur appartient à la session locale active et ses deux autorisations d’arrêt passent. **Correction E49 :** le « challenge » mesuré via runuser dans SSH ne caractérisait pas le vrai lanceur ; bouton à essayer au retour de l’utilisateur, aucune nouvelle règle installée. À ce relevé E52, utilisateur absent temporairement ; il est revenu depuis (E56). Aucun arrêt/redémarrage volontaire pendant son absence.

E51 : compilation audio originale échouée (huit erreurs, un avertissement). Fonctions C réelles testées hors console : dépassements de géométrie et boucle de cache reproduits ; correctif partiel 0008 validé sur 16 369 tailles synthétiques. Audio toujours désactivé, portage complet et matériel non validés. Voir `docs/AUDIO-BUFFER-AUDIT.md`.

## Dernier retour utilisateur : DVD absent sous le système d’origine

E50 : après le contrôle demandé dans le tableau de bord Xbox, l’utilisateur rapporte que rien n’est détecté. Ce retour rend une cause exclusivement Linux moins probable ; aucun composant fautif identifié, état du DVD sur un autre lecteur toujours inconnu. Retour vers obsidian4 demandé, état Linux actuel non revérifié.

E49 : arrêt depuis le bureau refusé ; CanPowerOff renvoie « challenge », aucun inhibiteur. Demande d’arrêt normal administrateur acceptée. Contournement ponctuel effectué, permissions du bouton graphique non corrigées ; extinction physique non observée directement.

## Régression graphique reproduite hors console

E47 : deux affichages Xvfb isolés, IceWM 4.0.0 recompilé, lanceur réel du dépôt. Le redimensionnement en mode contour bloque le client XTest et un observateur indépendant ; en mode direct, la taille diminue de 1240 × 640 à 1180 × 600 et les deux clients répondent. Cause reproduite au niveau X11, pas une validation PowerPC/GPU ni un essai physique de manette. Voir `docs/DESKTOP-TESTING.md`.

## Contrôles vivants du 2 octobre

E48 : DVD vidéo Big Order inséré par l’utilisateur ; deux interrogations espacées renvoient aussi `02/3a/00` (support absent). Le refus dépasse le seul jeu Xbox ; région réelle et composant fautif non identifiés. Utilisateur : rotation brève puis arrêt, comme le jeu. Lisibilité sur un autre lecteur non confirmée ; contrôle dans le tableau de bord d’origine demandé.


E45 : Just Cause 2 inséré ; statut « pas de disque », erreur de lecture et réponse SCSI `02/3a/00` (« medium not present »). Contraste CD/DVD constaté, origine matérielle précise inconnue.

E46 : l’utilisateur corrige son premier retour : le bureau était figé depuis un redimensionnement la veille. La présence des processus dans E43 ne démontrait donc pas sa réactivité. Relance du lanceur seule et SIGHUP IceWM insuffisants ; arrêt forcé IceWM suivi de sa relance automatique rétablit XRandR, sans reboot Linux. Réglages `OpaqueMove=1` et `OpaqueResize=1` installés, ancien fichier sauvegardé ; lanceur relancé et état manette rafraîchi. Essai manuel de redimensionnement demandé. Voir `docs/DESKTOP-RESIZE-RECOVERY.md`.

E43 : obsidian4 répond après plus de neuf heures de fonctionnement, IceWM actif et zéro service en échec. Ce relevé ne constitue pas un test de charge ni une validation du lanceur : son fichier d’état manette ne change pas pendant une fenêtre de douze secondes. Aucun gain d’écriture au repos n’est donc mesuré ; diagnostic à poursuivre avant optimisation.

E44 : après insertion d’un CD musical par l’utilisateur, le lecteur renvoie un statut prêt et une table de **20 pistes audio**. Quatre lectures de 2 352 octets réussissent, sur trois positions éloignées, avec empreinte identique lors de la relecture de la première. Le lecteur sait lire ces secteurs CD ; DVD et jeux restent non vérifiés. Aucune donnée audio conservée, seulement métadonnées et empreintes. Preuves : `evidence/2026-10-02/optical-cd/`. Utilisateur réveillé ; comparaison DVD demandée.

## Outil d'analyse ajouté le 2 octobre (date locale)

E41 : inspecteur XEX2 Rust en lecture seule, testé sur l'hôte avec dix tests structurels, 10 000 mutations déterministes et neuf cas CLI. Champs sensibles omis, lectures bornées, aucun jeu authentique analysé. Ce travail n'a pas interrogé la console et ne rafraîchit donc pas son dernier état vivant. Voir `docs/XEX2-INSPECTION.md`.

Publication E41/E42 vérifiée le 2 octobre à 07:14:53 UTC : commit public `2d31efb`, 203 fichiers, arbre GitHub identique à l'export audité. Le parseur a également passé ses dix tests après compilation dans le checkout public. Preuve : `evidence/2026-10-02/public-audit/publication.json`.

## Dernier point : obsidian4 démarré et vérifié en SSH

Objectif étendu : démarrage direct sous Linux, bureau, optimisations mesurées et évaluation de Rust, lecteur et jeux sur disque ; voir `docs/OBJECTIVE.md` pour les preuves encore requises.

Objectif courant mis à jour : analyse des jeux légitimes, modernisation, autonomie nocturne et publication GitHub autorisée après audit. Actions physiques différées dans `docs/BLOCKED.md`. Première référence mesurée sous obsidian4 : systemd atteint sa cible graphique à ~34,1 s après l'origine noyau, 118,5 Mio disponibles au relevé et SHA-256 médian 22,553 Mio/s. Aucun gain avant/après revendiqué ; voir `docs/PERFORMANCE-BASELINE-2026-10-01.md`.

Publication initiale vérifiée : `https://github.com/ludovic111/OBSIDIAN-360`, commit public `f9da49e`, 187 fichiers issus d'un export audité, historique public indépendant. La branche de recherche locale reste privée et sans remote. Procédure et preuve dans `docs/PUBLICATION.md`.

Le candidat **6.18.11-xenon-obsidian4** est construit sans avertissement, avec 65 modules et un initramfs vérifié. Les nouveaux fichiers sont présents sur la console et sur la clé ; une entrée optionnelle `obsidian4` est ajoutée. **Le défaut reste `linux_hdd` et les fichiers de récupération sont préservés.**

Après avoir trouvé le menu XeLL, l'utilisateur indique avoir choisi obsidian et retrouvé le bureau. **Mesure directe du 1 octobre à 21:45:47 UTC : `6.18.11-xenon-obsidian4`, racine `/dev/sda1` ext4, Xorg/IceWM actifs, zéro service en échec.** udev actif et `udevadm settle --timeout=5` réussit. Le journal confirme l'allocation graphique corrigée `0x398000` (3 768 320 octets) en 1280 × 720. Ethernet à 100 Mbit/s duplex intégral, zéro erreur RX/TX au relevé (14 paquets RX abandonnés). Preuves : `obsidian4-first-boot/runtime.json` et `validation.json`.

La photo IMG_1372 précédente reste un incident à noyau non identifié ; le démarrage réussi ne démontre ni sa cause ni sa résolution définitive. Le 1080p, les essais prolongés, les commandes physiques à la manette et les redémarrages répétés restent à vérifier. Aucun changement du choix par défaut n'a été fait pendant cette validation. Voir `docs/BOOT-PREFLIGHT-2026-10-01.md`.

Analyse vidéo hors console : les fonctions f1/f2 réelles de libxenon ont été exécutées avec écritures simulées sur les 26 entrées des deux familles de tables, sous ASan/UBSan. Douze des treize registres communs du mode HDMI 720p concordent avec l'ancien relevé ; la différence concerne l'adresse du framebuffer. Cette corrélation ne fournit pas les horloges 1080p. Voir `docs/VIDEO-MODE-TRACE-2026-10-01.md`.

Lecteur : PLDS DG-16D2S identifié ; l'utilisateur confirme que le tiroir s'ouvre mais qu'aucun disque n'est lu. Le pilote a utilisé un repli après échec de détection des capacités ; cela n'identifie pas la panne optique. Voir `docs/OPTICAL-DRIVE.md`.

Les sections suivantes conservent les étapes antérieures ; leurs états « non installé » précèdent le staging obsidian4.

## Récupération vérifiée

SSH est rétabli après le redémarrage physique effectué par l’utilisateur. La racine `/dev/sda1` est montée en ext4 et IceWM ainsi que le lanceur se sont relancés automatiquement. Aucun service systemd actuellement en échec. Preuve : `evidence/2026-10-01/recovery-log.txt`.

L’incident NAND reste non expliqué : la sonde de lecture a figé la machine. Aucune écriture flash envoyée, aucun dump NAND validé. Ne pas rejouer cette sonde.

## Installation déjà vérifiée avant le gel

- Racine ext4 : UUID `e9584d6f-d7ed-40ba-80a2-6834f8d91f31` ; swap 2 Gio.
- Noyau `6.18.11-xenon`, applications PowerPC 32 bits ; hostname `xbox-linux`.
- IceWM 4.0.0, Xorg 21.1.24, Python 3.14.6, Tk 8.6.16.
- Xorg `modesetting`, rendu logiciel, 1280 × 720 ; premier essai `fbdev` abandonné.
- Compte graphique `xbox`, autologin tty1 → startx → IceWM → lanceur Python.
- Manette : `/dev/input/js0` présent après redémarrage, accès ouvert par le lanceur, 4 557 événements reçus au relevé. La réussite des interactions visibles doit encore être confirmée par utilisateur.
- Pas de son : `CONFIG_SOUND` désactivé dans le noyau installé.
- Les paquets étaient entièrement installés avant le gel ; aucune transaction pacman en cours à cet instant.

## Acquisitions rapatriées

`smc-status.json`, `platform-read.log`, `ana-720p.bin`, `ana-720p.json` et `gpu-display-registers.json` ont survécu au redémarrage. Ils sont copiés dans `evidence/2026-10-01/` et leurs SHA-256 ont été comparés à ceux calculés sur la console. Le dump ANA contient exactement 1 024 octets.

## Observation résiduelle

Le journal du nouveau démarrage signale le module facultatif `pkcs8_key_parser` introuvable, demandé par `/usr/lib/modules-load.d/pkcs8.conf`. Aucun service n’est en échec au contrôle final. Aucune modification de noyau n’a été effectuée pour ce point ; à examiner séparément si une fonction cryptographique en dépend.

## Analyse approfondie suivante

Console revérifiée vivante en SSH : noyau `6.18.11-xenon`, racine interne, bureau actif, affichage 1280 × 720. Relevé dans `evidence/2026-10-01/deep-audit/`.

Deux défauts mémoire des sources de référence sont reproduits par AddressSanitizer sur le Mac : framebuffer Xenos sous-dimensionné pour les tuiles en 720p/1080p ; tampon HTTP XeLL de 512 octets pour une lecture NAND brute de 528 octets. Deux correctifs candidats et dix cas de test vérifiés, **aucun correctif déployé sur la Xbox**. Correspondance exacte des binaires installés avec ces sources encore à établir ; aucune cause démontrée du gel E10. Lire `docs/DEEP-AUDIT-2026-10-01.md`.

Le journal vivant confirme néanmoins la même taille d'allocation graphique linéaire : `0x384000` octets en 1280 × 720. Contrôle final : bureau actif, SSH accessible, aucun service en échec, uptime 22 minutes. Preuve : `deep-audit/final-console-check.txt`.

Le pilote audio historique exige un portage des API et une revue DMA/SMC avant activation. Le nouveau relevé réseau indique 100 Mbit/s duplex intégral et aucune erreur RX/TX ; il ne valide pas la stabilité prolongée.

Une interrogation du paquet installé a également signalé un trousseau public pacman absent ; `/etc/pacman.d/gnupg/pubring.gpg` n'existe pas au contrôle. Diagnostic incomplet, aucune modification de la politique de signatures. À résoudre avant une prochaine installation de paquets. Preuve : `deep-audit/package-access.txt`.

## Identification binaire et outillage rétabli

La recette exacte du paquet pointe vers `techflashYT/linux-custom@a293dd19311668900eb1eeb2f6cb01dcac54f330`. Le vmlinux récupéré et l'image de démarrage ont six sections identiques, dont tout `.text` ; leurs empreintes sont vérifiées. Ne plus attribuer sans comparaison le comportement du patch Free60 à ce binaire. Le mode graphique de la branche installée est **constant 1280 × 720**.

Neuf fonctions du noyau ont été désassemblées avec succès dans l'environnement Docker multiarchitecture. Les multiplications de la taille graphique sont confirmées dans le binaire. Un troisième défaut concerne `xenon_ipi_send_mask`, qui perd le masque des destinataires ; le chemin SMP ordinaire utilise une autre fonction correcte. Test du callback réel hors console : 256 combinaisons avant et après correction candidate. Aucun correctif déployé ; aucune cause du gel E10 démontrée. Lire `docs/BINARY-AUDIT-2026-10-01.md`.

`tools/audit-session.py` vérifie les prérequis et conserve les résultats de chaque étape, sans refaire les acquisitions.

## Cache SMC et première compilation candidate

La recherche du cache SMC dépasse son tableau pour les identifiants absents : reproduction ASan hors console et boucle confirmée dans le binaire installé. Le correctif borné passe les 256 identifiants possibles. Aucun message inconnu envoyé au matériel. Analyse du transport, des attentes et de la concurrence dans `docs/SMC-AUDIT-2026-10-01.md`.

Le noyau candidat `6.18.11-xenon-obsidian1` a terminé sa compilation `vmlinux` le 1 octobre à 21:00:03 UTC, code 0. Format ELF64 PowerPC big-endian vérifié ; correctifs Linux 0001, 0003 et 0004 inclus. SHA-256 : `34da8563558009ef6473e56b6f44fccea31a9c080d7d6382af8b5ec5e0dd16df`. Preuves, configuration et journal dans `evidence/2026-10-01/kernel-build/`.

Le build comporte un avertissement de variable non initialisée dans `xenon_led_init`, à corriger avant essai. Modules et conditionnement de démarrage non validés ; aucun déploiement ni démarrage du candidat. Cette compilation LLVM 16 n'est pas une reconstruction bit à bit du paquet GCC installé. L'affichage candidat reste configuré en 720p, le son désactivé.

Les interruptions de session répétées sont identifiées par `cyber_policy` dans les événements Codex ; le build local a continué malgré elles. Diagnostic et procédure de reprise dans `docs/SESSION-RECOVERY.md`. La rétro-ingénierie reste incomplète.

## Pilote LED et candidat obsidian3

Le retour non initialisé a été corrigé avec le cycle init/exit, les ressources LED et l'envoi SMC sans réponse. Les 21 tests hors console passent. Le test de compilation en module a révélé une fonction SMC non exportée ; son export GPL rétablit le lien. Les échecs initiaux et le succès sont conservés dans `led-audit/`.

Le candidat **6.18.11-xenon-obsidian3** est construit : noyau, 65 modules et image `zImage.xenon`. Formats PowerPC, versions des modules et six sections entre noyau et image contrôlés. Les compilations noyau/modules ne signalent aucun avertissement ; la fabrication de l'image signale deux règles concurrentes dans le Makefile amont, à nettoyer. Lire `docs/LED-AUDIT-2026-10-01.md` et `docs/KERNEL-CANDIDATE-2026-10-01.md`.

Aucun candidat installé ou démarré ; l'initramfs et l'ensemble de démarrage séparé restent à préparer. Toujours aucun 1080p ni démarrage indépendant validé. Aucune nouvelle mesure matérielle dans E28–E30.

## Accès et sauvegardes conservés

Configuration d’accès dans `.local/ssh_config`, ignorée. La clé privée reste à son emplacement original hors dépôt. Accès root par clé uniquement.

Les sauvegardes historiques sont des régions du disque interne, pas une sauvegarde de la NAND. Aucune image de flash restaurable confirmée. N’effacer aucune sauvegarde ni la récupération Linux live de la clé USB.

Publication E43–E46 vérifiée à 2026-10-02T07:41:15.538940+00:00 : commit public `ec431c9c7e114e11074628d0fb95358d1128a752`, 221 fichiers, arbre distant identique ; preuve `public-audit/optical-publication.json`. Validation manuelle du redimensionnement encore attendue.

Publication E47 et piste PAL vérifiée à 2026-10-02T07:57:41.408927+00:00 : commit public `a67d28f83a160fde6048efc74a9824c808745f74`, 230 fichiers, arbre GitHub identique ; preuve `evidence/2026-10-02/public-audit/resize-publication.json`.

Publication E48 vérifiée à 2026-10-02T08:03:48.586991+00:00 : commit public `b4b49e2b2fdcc42f522fbc6cd4b74b1b96202632`, 234 fichiers et arbre distant conforme ; preuve `evidence/2026-10-02/public-audit/video-publication.json`. Résultat du contrôle sous tableau de bord stock encore attendu.

Publication E49–E52 vérifiée à 2026-10-02T08:25:04.519035+00:00 : commit public `fd75dd4f20e7d0c0d0fc1475b1423d013d7cfa00`, 248 fichiers, parent et arbre GitHub conformes après audits. Preuve `evidence/2026-10-02/public-audit/audio-publication.json`. Audio non activé ; aucun arrêt depuis le retour Linux.

Publication E53/E54 vérifiée à 2026-10-02T08:57:54.026744+00:00 : commit public `5dd3293b9936669ba7a8e25935de8dd6b918fafc`, 273 fichiers, parent et arbre GitHub conformes après audits. Preuve `evidence/2026-10-02/public-audit/smc-publication.json`. Deux builds audio complets validés, aucun installé.

Publication E55/E56 vérifiée à 2026-10-02T09:45:58.581719+00:00 : commit public `74ba6693755aaef77e96d016bbcbc6e7cf473713`, 287 fichiers, parent et arbre GitHub conformes après audits. Preuve : `evidence/2026-10-02/public-audit/pcm-publication.json`. Candidat audio-pcm non installé.

Publication E57/E58 vérifiée à 2026-10-02T10:19:25.216637+00:00 : commit public `987fea14abdeb6059b4b8d4a6b1215345cefabbe`, 312 fichiers, parent et arbre GitHub conformes après audits. Preuve : `evidence/2026-10-02/public-audit/poll-publication.json`. Noyau audio-poll compilé, non installé ; soumission encore à corriger.

Publication E59 vérifiée à 2026-10-02T10:36:04.104109+00:00 : commit public `3a98dcf5b0977a33251748255f186c25cfcf2da0`, 324 fichiers, parent et arbre GitHub conformes après audits. Preuve : `evidence/2026-10-02/public-audit/queue-publication.json`. File PCM testée et liée pour PowerPC, non intégrée au pilote et non chargée.

Publication E60/E61 vérifiée à 2026-10-02T10:58:31.472464+00:00 : commit public `f8989261de3589ec3b3c3276b9e4ef66646795f3`, 342 fichiers, parent et arbre GitHub conformes après audits. Preuve : `evidence/2026-10-02/public-audit/adapter-publication.json`. Noyau audio-submit compilé, non installé ; fin du dernier descripteur toujours non décodée.
