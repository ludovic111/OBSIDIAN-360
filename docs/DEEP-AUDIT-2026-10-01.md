# Analyse approfondie — 1 octobre 2026

Cette session combine des observations Linux en direct, une analyse des sources et des tests C exécutés sur le Mac. Elle ne constitue pas une rétro-ingénierie complète du silicium. Deux défauts de bornes mémoire sont reproduits dans le code de référence ; deux correctifs candidats sont conservés, sans modification du noyau ni du chargeur de la Xbox.

## Périmètre des preuves

- Mesure directe : `evidence/2026-10-01/deep-audit/runtime.json` et `kernel-provenance.txt`.
- Analyse reproductible : `video-analysis.json`, `tiling-bounds.json` et `memory-bounds.json` dans le même dossier.
- Sources exactes, commits et SHA-256 : `deep-audit/sources.json`.
- Patch Linux étudié : `patch-6.18-xenon0.30.diff`, SHA-256 `d5d79cd502f859311dd2f2b834b57a489fead1e8e622deb55c6a70f79df604ad`. Il correspond à la référence déjà archivée dans ce dépôt.
- Le paquet installé est `linux-xenon 6.18.11-1`. L'identité de version ne prouve pas à elle seule que chaque instruction du binaire installé correspond aux sources étudiées. Nous n'avons ni reconstruit ce binaire ni vérifié son désassemblage.

## F01 — Allocation du framebuffer trop petite pour le placement en tuiles

**Confirmé dans le code de référence, reproduit sur le Mac.** Le pilote alloue `width * height * cpp` octets, mais `xenos_blit()` place les pixels dans des macro-tuiles de 32 × 32. Les dernières lignes d'une hauteur non multiple de 32 peuvent donc écrire après la fin de l'allocation.

| Taille | Allocation originale | Fin maximale adressée, exclusive | Allocation proposée |
|---|---:|---:|---:|
| 640 × 480 | 1 228 800 | 1 228 800 | 1 228 800 |
| 1280 × 720 | 3 686 400 | 3 766 272 | 3 768 320 |
| 1920 × 1080 | 8 294 400 | 8 354 816 | 8 355 840 |
| 1280 × 768 | 3 932 160 | 3 932 160 | 3 932 160 |

Le test extrait la vraie fonction C `xenos_blit()` et la compile avec AddressSanitizer. Les allocations originales produisent `heap-buffer-overflow` en 720p et 1080p. L'allocation arrondie aux tuiles passe les quatre tailles. Le calcul exhaustif des indices fournit une deuxième vérification indépendante.

**Corroboration en direct** : le journal du démarrage actuel annonce `Using 1280x720 (384000) fb`. La valeur hexadécimale `0x384000` vaut 3 686 400 octets, exactement la taille linéaire étudiée. Cela renforce la pertinence du défaut pour cette installation, sans démontrer les accès mémoire effectifs ni remplacer une vérification du binaire. Preuve : `deep-audit/final-console-check.txt` ; console toujours accessible après 22 minutes, bureau actif et aucun service en échec.

Correctif candidat : `research/patches/0001-xenos-pad-tiled-framebuffer.patch`.

Limites : les tests utilisent des allocations mémoire du Mac, pas les allocations DMA du noyau PowerPC. Les quatre largeurs testées sont multiples de 32. Le cycle de vie DRM, les rectangles de dommage, le cache, les erreurs d'allocation et l'ensemble des formats restent à tester. Ce correctif ne programme aucun timing HDMI et n'active pas le 1080p. Il ne démontre pas la cause du gel E10.

Source : [xenos.c dans le patch Linux figé](https://github.com/Free60Project/linux-kernel-xbox360/blob/498bbe1910f707ceba0535276d75a3e6ad0b7df4/patch-6.18-xenon0.30.diff), fonctions `xenos_enable` et `xenos_blit`.

## F02 — Tampon de lecture NAND HTTP XeLL insuffisant

**Confirmé pour les sources étudiées, reproduit sur le Mac avec lecture matérielle simulée.** Dans `response_flash_do_data()`, le tampon réserve `sfc.page_sz` octets. L'appel `sfcx_read_page(..., 1)` y écrit une page physique de `sfc.page_sz_phys` octets. L'initialisation libxenon fixe respectivement 512 et 528 octets : il manque 16 octets pour les métadonnées/ECC.

Le test compile le fichier HTTP XeLL complet en remplaçant seulement les dépendances matérielles/réseau par des interfaces simulées. La simulation respecte la taille écrite par `sfcx_read_page()` en lecture brute. AddressSanitizer reproduit un `dynamic-stack-buffer-overflow`. Avec le tampon de 528 octets, deux pages sont transmises correctement : 1 056 octets vérifiés.

Correctif candidat : `research/patches/0002-xell-allocate-physical-page.patch`.

Autres points constatés : le gestionnaire HTTP ignore le statut retourné par `sfcx_read_page()` ; l'attente `STATUS_BUSY` de libxenon n'est pas bornée. Deux téléchargements identiques ne suffiraient donc pas à garantir une acquisition restaurable : géométrie, ECC, blocs défectueux et statut de lecture doivent être contrôlés séparément.

Limites : aucune requête `/FLASH` n'a été envoyée à la console pendant cette session. La version de XeLL effectivement embarquée dans notre chaîne de démarrage n'a pas été identifiée par son code binaire. Cette anomalie appartient au chemin HTTP XeLL ; elle n'explique pas la lecture mmap Linux ayant gelé la machine.

Sources : [gestionnaire HTTP](https://github.com/Free60Project/xell-reloaded/blob/a36ed6b7dae940e47e472a20fd14b0616ddc8cef/source/lv2/httpd/httpd_flash.c), [lecture et géométrie SFCX](https://github.com/Free60Project/libxenon/blob/a333adef440f28b436a667be0a4f014afce6349d/libxenon/drivers/xenon_nand/xenon_sfcx.c).

## F03 — Corrélation du mode HDMI 720p

**Mesures historiques décodées hors ligne et comparaison de code.** Les captures GPU donnent : largeur 1 280, hauteur 720, pitch 1 280 pixels ; total horizontal 1 650 ; décalage horizontal 259. Ces valeurs correspondent à la table `HDMI 720p` de libxenon.

Sur les 121 entrées ANA de cette table qui ne sont pas des sentinelles `ffffffff` ou `deadbeef`, 109 égalent la capture. Douze diffèrent. Six différences (`0x20` à `0x25`) correspondent exactement aux constantes écrites séparément par `xenos_init_ana_new()`. Les autres différences restent à interpréter ; les zéros communs ne sont pas une preuve forte d'identité matérielle.

Un piège de lecture est clarifié : libxenon écrit volontairement zéro dans le registre nommé `D1CRTC_V_TOTAL` à `0x6020`. Il place `total_height - 1` à `0x6010`, malgré le nom `D1CRTC_H_SYNC_B`. Notre capture ne contient pas `0x6010` : le total vertical n'est donc pas mesuré. Il serait incorrect de calculer une fréquence à partir de `0x6020`, ou de traiter 60 Hz annoncé par DRM comme une mesure d'horloge. La capture à `0x6024` ne permet pas non plus une interprétation générique de timing Radeon.

Le patch Free60 étudié construit un seul `fixed_mode` depuis les dimensions déjà présentes dans les registres. **Correction après identification du paquet : la branche réellement installée impose un mode constant 1280 × 720**, comme détaillé dans [l'analyse binaire](BINARY-AUDIT-2026-10-01.md). Les tables actuelles de libxenon exposent 13 modes, aucun 1920 × 1080. Il faut comprendre et valider horloges ANA/HANA, timings GPU, placement mémoire et démarrage du mode ; une simple modeline XRandR est insuffisante.

Enfin, `ana_read_reg()` dans le pilote Linux retourne les octets de la réponse SMC sans valider son statut. Les lectures ANA doivent rester des observations assorties de cette limite ; ce n'est pas une lecture garantie de tous les registres physiques.

Sources : [programmation vidéo libxenon](https://github.com/Free60Project/libxenon/blob/a333adef440f28b436a667be0a4f014afce6349d/libxenon/drivers/xenos/xenos.c), [tables](https://github.com/Free60Project/libxenon/blob/a333adef440f28b436a667be0a4f014afce6349d/libxenon/drivers/xenos/xenos_videomodesdata.h).

## F04 — Audio : pilote présent dans les sources, portage incomplet

**Code de référence et configuration mesurée.** Le contrôleur PCI `1414:580c` existe, mais `CONFIG_SOUND` est désactivé et aucun pilote n'y est attaché. Le patch contient `snd-xenon.c`, qui décrit deux sorties PCM, analogique et numérique, en stéréo S16_LE à 48 kHz. Le fonctionnement HDMI n'a pas été démontré.

L'activer immédiatement serait prématuré. Le code utilise encore `pci_alloc_consistent`, `pci_free_consistent`, `from_timer` et `del_timer_sync`, absents des en-têtes Linux v6.18 inspectés. Les interfaces modernes correspondantes sont les API DMA cohérentes, `timer_container_of` et les fonctions `timer_delete*`/`timer_shutdown*`, à sélectionner selon le cycle de vie réellement nécessaire.

D'autres problèmes demandent une revue avant portage : accès direct au SMC sans utiliser la sérialisation du pilote central ; attente matérielle sans délai maximum ; retour d'allocation DMA non vérifié ; adresse DMA masquée en place avant sa libération ; gestionnaire IRQ qui retourne toujours `IRQ_HANDLED`, tandis que l'évolution PCM est suivie par un timer. Avec `CONFIG_HZ=300`, une demande de timer à 200 microsecondes ne garantit pas une cadence réelle de 200 microsecondes.

Aucune compilation PowerPC ni restitution audio effectuée. Installer seulement un mixeur ou ALSA en espace utilisateur ne résoudrait pas ces éléments.

Sources : `sound/pci/snd-xenon.c` dans le patch Linux figé ; [API timer Linux v6.18](https://github.com/torvalds/linux/blob/v6.18/include/linux/timer.h) et [API DMA](https://github.com/torvalds/linux/blob/v6.18/include/linux/dma-mapping.h).

## F05 — Réseau, températures et interruptions

**Mesure directe ponctuelle.** `enp1s7` indique 100 Mbit/s duplex intégral. Compteurs au relevé : zéro erreur RX/TX, zéro collision, 84 paquets RX abandonnés. Les abandons ne prouvent pas une panne physique. Le journal interrogé ne contient pas de nouveau watchdog, timeout, Oops ou BUG à cet instant. Cela ne démontre pas la résolution du watchdog historique ni la stabilité sous charge.

Les interruptions des périphériques observés arrivent sur CPU0 ; les IPI et timers utilisent aussi les autres threads. Températures relevées : CPU 55,121 °C, GPU 49,195 °C, eDRAM 52,925 °C, carte 27,898 °C, selon l'ordre du pilote hwmon déjà étudié. Aucune consigne thermique modifiée.

Le patch réseau contient un MAC de secours fixe et limite correctement la négociation Gigabit au type SiS191. Ces faits de code ne diagnostiquent pas la cause du timeout de transmission.

## Carte du travail restant

| Sous-système | Ce qui est établi | Ce qui manque |
|---|---|---|
| CPU / RAM / interruptions | Inventaire, topologie Linux, route des IRQ et configuration | Mesures de caches, performances, cohérence DMA ; aucune analyse du silicium |
| GPU / HDMI | Mode 720p corrélé, défaut d'allocation reproduit hors machine | Noyau candidat compilé, validation DMA, tables et horloges 1080p, accélération 3D |
| Audio / XMA | Contrôleurs PCI et pilote audio historique analysés | Portage testé, restitution physique, décodeur XMA |
| SATA / USB / manette | Disque monté, pilotes liés, événements de manette | Validation prolongée et protocoles propriétaires non étudiés |
| SMC / ANA / thermique | Commandes d'état, captures et code des pilotes | Sens exact des registres restants, robustesse des échanges |
| NAND / boot | Stub Linux, protocole SFCX étudié, défaut XeLL reproduit | Cause du gel, géométrie réelle, acquisition contrôlée, ECC, bootloaders propres à la console |
| Ethernet | Liaison active et compteurs ; code du pilote identifié | Cause du watchdog et validation sous charge maîtrisée |

Le démarrage indépendant du système Xbox demeure non réalisé. Aucun nouvel exploit persistant n'est établi par ces analyses, et aucune mémoire de démarrage n'a été effacée ou reprogrammée.
