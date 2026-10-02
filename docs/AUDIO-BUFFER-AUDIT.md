# Pilote audio : compilation et géométrie des tampons — E51

Analyse du 2 octobre 2026 sur `sound/pci/snd-xenon.c`, source linux-custom `a293dd19311668900eb1eeb2f6cb01dcac54f330`. SHA-256 du pilote : `4289271b03404f6079b590f696e44625d07c59017f099295833390d38f89a0ac`. Aucun accès à la carte son ; aucun nouveau module installé. Le noyau fonctionnel obsidian4 conserve le son désactivé.

## Compilation originale

Un dossier de sortie distinct reprend la configuration obsidian4 en activant SOUND, SND et SND_XENON comme modules et SND_PCI. La source et l’ancien build ne sont pas modifiés. Image LLVM 16 connue, réseau Docker désactivé, deux processeurs et 2 Gio maximum.

`olddefconfig` réussit ; la cible `sound/pci/snd-xenon.o` échoue : huit erreurs et un avertissement. Les API absentes sont `from_timer`, `pci_alloc_consistent`, `pci_free_consistent`, `snd_printk` et `del_timer_sync`. L’avertissement concerne le prototype manquant du transport SMC privé au pilote. Ces résultats confirment E17 par une compilation effective ; aucun objet audio utilisable obtenu. Log complet, configuration et méthode dans `evidence/2026-10-02/audio-buffers/`.

## Boucle de cache

La fonction soustrait 128 à un entier signé tant qu’il est non nul. Pour une taille positive non divisible par 128, elle dépasse zéro sans l’atteindre et continue à avancer l’adresse ; un débordement signé finit par rendre le comportement C indéfini. Cela ne prouve pas un gel réel : ce pilote est désactivé sur notre console.

Le banc conserve la boucle C réelle, remplace uniquement les deux instructions PowerPC par des hooks et interrompt l’exécution au premier parcours au-delà du nombre de lignes attendu. Cinq tailles parmi huit déclenchent ce garde-fou : 64, 68, 132, 192 et 65 532 octets. Les cas 128, 256 et 65 536 se terminent normalement. Il s’agit d’une preuve logique bornée, pas de l’exécution d’un cache PowerPC ni d’une mesure de cohérence DMA.

La préallocation ALSA de 64 Kio ne suffit pas à éviter le problème : `sound/core/pcm_memory.c`, fonction `snd_pcm_lib_malloc_pages`, affecte la taille demandée à `runtime->dma_bytes`, même quand elle réutilise une allocation plus grande.

## Descripteurs

Le pilote crée 32 segments de longueur arrondie vers le haut, puis retranche tout l’excédent au dernier. Pour 68 octets, il choisit 3 octets par segment, un excédent de 28 et une dernière longueur encodée par `3 - 1 - 28 = -26` ; le mot devient `0xffffffe6`. Les premiers segments dépassent déjà le tampon avant la fin du tableau.

Le banc exécute les vrais `hw_params` et `prepare`, avec allocation, verrouillage et MMIO simulés. Il parcourt les 16 369 tailles multiples de quatre de 64 à 65 536 octets : 98 géométries sortent de la plage du tampon selon l’encodage longueur moins un employé par le code. Par ailleurs, 12 273 géométries fractionnent les trames stéréo de quatre octets entre des descripteurs. **Cette deuxième propriété seule n’est pas une panne matérielle démontrée** : la capacité du contrôleur à traverser une limite de descripteur au milieu d’une trame reste non vérifiée. L’union des deux catégories vaut 12 301 tailles.

## Correction partielle 0008

La boucle s’arrête maintenant quand la taille devient non positive. `hw_params` refuse les tailles hors de 128–65 536 ou non multiples de 128 ; `prepare` répète ce contrôle avant toute opération matérielle et exige la concordance entre taille DMA et taille ALSA. Chaque taille acceptée donne alors 32 segments égaux contenant des trames entières.

Les mêmes tests acceptent 512 tailles, rejettent les 15 857 autres avant allocation/mappage et ne produisent aucun segment hors tampon. Le test indépendant de désaccord DMA/ALSA passe. Huit tests de boucle passent sans dépassement du nombre de lignes attendu. ASan/UBSan ne rapportent aucune erreur dans ce banc ; les accès matériels sont simulés.

Cette restriction est un premier correctif défensif. Il reste à annoncer la contrainte dans la négociation ALSA, à tester le portage complet et à confirmer le format des descripteurs sur le matériel. Le test ne prouve pas que toutes les tailles énumérées peuvent être négociées dans un système ALSA réel, ni qu’une application choisira une taille acceptée.

## Obstacles avant activation

Analyse du code, sans expérimentation matérielle :

- Le timer est initialisé mais aucun armement initial n’apparaît ; seul son callback contient `mod_timer`. Les notifications de périodes et leur calcul doivent être revus.
- Le transport SMC privé contourne le verrou du cœur existant et attend sans borne. Utiliser une interface partagée exige aussi de traiter ses propres attentes sans borne.
- Allocation DMA non vérifiée sous verrou, handle DMA masqué puis réutilisé à la libération, conversion d’adresse DMA par `ioremap` : contrat mémoire à reprendre.
- Nettoyage possible avant `timer_setup`, échec de création suivi d’une libération de pointeur nul, double libération après échec d’enregistrement ALSA : gestion des ressources à tester par injection de fautes.
- IRQ toujours déclarée traitée et gestion activation/désactivation vide ; arrêt DMA et synchronisation des callbacks non validés.

Ne pas charger le pilote après une simple correction des erreurs de compilation. Aucun support HDMI, lecture audio, latence ou stabilité n’est validé par E51.

## Reproduction hors console

Appliquer le diff 0008 à une copie de la source originale. Exécuter :

```sh
python3 research/tests/check-audio-buffers.py --original ORIGINAL/snd-xenon.c --candidate CANDIDAT/snd-xenon.c
```

Le banc exige Clang et ses runtimes ASan/UBSan ; il crée des fichiers temporaires et ne contacte aucun matériel. Pour le build initial, dans l’image LLVM 16 documentée, monter la source en lecture seule sur `/src` et un nouveau dossier de sortie sur `/build`, copier la configuration, puis :

```sh
/src/scripts/config --file /build/.config -m SOUND -m SND -e SND_PCI -m SND_XENON
make -C /src O=/build ARCH=powerpc LLVM=1 LOCALVERSION=-audio-audit olddefconfig
make -C /src O=/build ARCH=powerpc LLVM=1 LOCALVERSION=-audio-audit -j2 sound/pci/snd-xenon.o
```

Cette compilation originale doit échouer avec les diagnostics conservés. Elle ne constitue pas une procédure d’installation.
