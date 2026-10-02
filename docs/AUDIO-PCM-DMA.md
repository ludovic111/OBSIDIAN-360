# Tampons PCM gérés par ALSA — E55

Le correctif 0011 s’applique après 0008/0009/0010. Il supprime le second mappage des échantillons audio et confie leur allocation au cœur ALSA. Le noyau `6.18.11-xenon-audio-pcm` et ses 70 modules compilent sans avertissement ; ils ne sont ni installés ni démarrés. Le pilote reste incomplet.

## Analyse du code

Dans la source linux-custom `a293dd19311668900eb1eeb2f6cb01dcac54f330`, `SNDRV_DMA_TYPE_DEV` utilise `dma_alloc_coherent` (`sound/core/memalloc.c`). L’adresse destinée au CPU est fournie dans `runtime->dma_area`. Une adresse DMA n’est pas une adresse CPU à remapper par `ioremap` : le remappage historique est donc supprimé, ainsi que son pointeur auxiliaire et la boucle assembleur privée de maintenance du cache.

`snd_pcm_set_managed_buffer_all` remplace la préallocation seule et ses erreurs sont propagées pour les deux sorties. Le cœur alloue avant `.hw_params` et détache/libère après `.hw_free`, comme documenté dans `Documentation/sound/kernel-api/writing-an-alsa-driver.rst`. Le pilote ne libère plus ces pages dans `.close`. La préallocation peut rester attachée au PCM jusqu’à sa destruction : « managed » ne signifie pas que chaque `.hw_free` restitue nécessairement les pages physiques.

Le contrat de taille est annoncé dès `.open` : 128 à 65 536 octets, par pas de 128. Les erreurs de contraintes sont renvoyées avant programmation des registres. `.hw_params` conserve un contrôle défensif ; dans cette variante, ce contrôle intervient **après** l’allocation gérée par ALSA. `sound/core/pcm_memory.c` confirme que `runtime->dma_bytes` devient la taille demandée, même quand une préallocation plus grande est réutilisée.

`.prepare` vérifie l’adresse CPU, les tailles et l’intégralité de l’intervalle DMA dans le masque historique de 29 bits. La soustraction après vérification de la borne évite un débordement d’addition. Les échantillons sont initialisés via `runtime->dma_area` ; `dma_wmb()` précède la publication des descripteurs et le démarrage. La garantie de cohérence dépend de l’implémentation DMA de la plateforme, pas de ce banc hôte.

`.hw_free` écrit l’arrêt sur le seul canal propriétaire et relit le registre avant que le cœur ALSA puisse libérer le tampon. Les compteurs de géométrie sont invalidés. `.pointer` refuse alors les calculs sur une taille nulle et START est refusé après libération. Cette séquence ne démontre pas que le contrôleur réel a cessé toute transaction DMA ; la sémantique matérielle d’arrêt reste à vérifier.

## Résultats hors console

- Vingt scénarios de ressources passent sous ASan/UBSan, dont échecs de préparation des deux tampons gérés. Les treize scénarios originaux conservent leurs résultats attendus.
- Douze scénarios des callbacks C réels passent : contraintes, pointeur nul, tailles incohérentes, adresses hors plage/débordantes, propriétaire inconnu, deux flux simultanément ouverts et dix préparations successives.
- Le scénario normal vérifie les gardes autour du tampon, les appels de barrière, l’arrêt d’un seul flux avant libération simulée, puis le refus de START et la protection de `.pointer` après libération.
- La régression de géométrie examine 16 369 tailles ; 512 acceptées et 15 857 rejetées. Aucun descripteur hors tampon parmi les tailles acceptées. La fonction privée de cache étant supprimée, le candidat exécute zéro cas de cette ancienne fonction ; ce n’est pas une validation du cache PowerPC.
- Les quatre diffs reconstruisent exactement les trois sources compilées. Noyau et 70 modules ELF64 PowerPC big-endian vérifiés, avec vermagic concordants et aucun diagnostic de compilation.

Les API ALSA, MMIO et verrous sont modélisés. Les assertions séquentielles ne démontrent ni la négociation ALSA réelle, ni l’arrêt matériel, ni l’ordre entre CPU, ni l’absence de course. Le banc libère volontairement sa mémoire immédiatement après `.hw_free` pour détecter les accès ultérieurs ; cela représente une possibilité de libération du cœur, pas chaque chemin réel de préallocation.

L’outil `check-kernel-artifacts.py --kernel-only` permet désormais de vérifier un noyau et ses modules sans image XeLL. Sa voie complète a aussi été réexécutée sur les fichiers obsidian4 : six sections de charge utile identiques, 65 modules valides. Aucune reconstruction ni modification de ce noyau fonctionnel.

## Limites avant activation

Le timer historique reste partagé et n’est pas initialement armé. Son calcul de période, la synchronisation des callbacks lors d’un arrêt et l’absence de `.sync_stop` doivent être traités. Les publications liées à `appl_ptr` restent dans `.pointer`, avec leur arithmétique historique. Les supprimer de ce diff conserve un périmètre vérifiable, mais interdit de considérer le pilote comme prêt.

Restent aussi la divergence Linux/LibXenon sur la longueur des descripteurs, la limite mémoire basse possible de 32 Mio, et l’initialisation analogique/HDMI. Aucun son ni gain de performance mesuré. Aucun initramfs ou image de démarrage de cette variante n’est produit.

## Reproduction

Dans une copie des sources préparées pour obsidian4, appliquer successivement 0008, 0009, 0010 et 0011. Les sources originales doivent être conservées séparément pour les comparaisons.

```sh
python3 research/tests/check-audio-lifecycle.py --original ORIGINAL/sound/pci/snd-xenon.c --candidate CANDIDAT/sound/pci/snd-xenon.c --output lifecycle.json
python3 research/tests/check-audio-buffers.py --original ORIGINAL/sound/pci/snd-xenon.c --candidate CANDIDAT/sound/pci/snd-xenon.c --output buffers.json
python3 research/tests/check-audio-pcm.py --source CANDIDAT/sound/pci/snd-xenon.c --output pcm.json
make -C CANDIDAT O=BUILD ARCH=powerpc LLVM=1 LOCALVERSION=-audio-pcm -j2 vmlinux modules
python3 tools/check-kernel-artifacts.py --kernel-only --build BUILD --output artifacts.json
```

Utiliser la configuration `evidence/2026-10-02/audio-pcm/kernel.config` et l’environnement LLVM 16 décrit en E53. Le build réalisé utilise une copie indépendante de la sortie E54 et trois fichiers candidats montés en lecture seule sur les sources obsidian4. Empreintes de sources/diffs, identité d’image, journal, preuves de tests et métadonnées ELF sont conservés dans `evidence/2026-10-02/audio-pcm/`.

## Contrôle vivant distinct — E56

Après le retour de l’utilisateur, une connexion SSH confirme obsidian4, environ 5 139 secondes de fonctionnement, aucun service systemd en échec et un framebuffer 1280 × 720. Seules les interfaces standard sont lues. Cela ne mesure pas la réactivité visuelle du bureau, la stabilité sous charge ou le nouveau pilote, resté sur le Mac. L’horodatage exact est dans `console-status.json`.
