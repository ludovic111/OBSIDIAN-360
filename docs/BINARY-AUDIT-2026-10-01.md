# Noyau installé, DMA et interruptions

## Chaîne de preuve

Le paquet installé est `linux-xenon 6.18.11-1`. La recette ArchPOWER correspondante est identifiée au commit `b166195754bd59ec1cbb4392dee6ae0f1ded87e4` : elle utilise le dépôt **techflashYT/linux-custom**, commit `a293dd19311668900eb1eeb2f6cb01dcac54f330`. Ce n'est pas exactement le patch Free60 étudié initialement.

Les fichiers de la console ont été copiés une fois, avec comparaison des empreintes locales et distantes :

| Fichier | SHA-256 |
|---|---|
| vmlinux avec symboles | `a51fb462247102de87b49f3047bb7b96dc8c8c40a5a488cc98ad8f2a919d95aa` |
| System.map | `6e67b74e4e568c03c18874ccb222905ab13b003d16cac3eb7b85c196363e0f90` |
| Image de démarrage vmlinuz | `a499ab2816bd5a94843442b0a8b89d18af4c1f98f4f264a83b0da5940c8bed66` |

L'image de démarrage porte un en-tête ELF32 PowerPC, tandis que `vmlinux` porte un ELF64 big endian ABI v2. Cela ne signifie pas que le noyau s'exécute en 32 bits : les sections `.head.text`, `.text`, `.rodata`, `.init.text`, `.data` et `.notes` sont identiques octet par octet entre ces deux fichiers. L'image de démarrage locale a le même SHA-256 que `/boot/vmlinuz-linux-xenon` sur la console. Les adresses des fonctions examinées dans System.map correspondent également au relevé `/proc/kallsyms`.

Preuves : `evidence/2026-10-01/binary-audit/remote-provenance.txt`, `elf-comparison.json`, `source-provenance.json`, `session-check.json` et les fichiers `.asm`. Le binaire complet reste dans `.local/binaries/`, hors Git.

Source de la recette : [PKGBUILD figé](https://github.com/kth5/archpower/blob/b166195754bd59ec1cbb4392dee6ae0f1ded87e4/kernels/powerpc/linux-xenon/PKGBUILD).

## Correction de l'analyse vidéo précédente

Le patch Free60 lit les dimensions dans les registres GPU. **La branche réellement utilisée par le paquet impose au contraire un mode constant 1280 × 720.** Son `xenos_load()` initialise une structure de mode fixe avec ces dimensions, sans les lire dans les registres.

Le désassemblage de `xenos_pci_probe()` contient les constantes correspondantes. À `0xc0000000007465c0` et `0xc0000000007465c8`, les arguments de dimensions sont chargés respectivement avec 720 et 1280. La lecture de registres effectuée lors de l'inventaire demeure valide comme observation matérielle, mais ne décrivait pas comment ce binaire construit son mode.

Conséquence : même un chargeur qui laisserait le GPU en 1080p ne suffit pas avec ce pilote précis. Il faut aussi adapter le mode exposé par le noyau et valider la programmation du GPU/ANA/HANA. Aucun de ces changements n'a encore été déployé.

Source : [xenos.c réellement référencé par le paquet](https://github.com/techflashYT/linux-custom/blob/a293dd19311668900eb1eeb2f6cb01dcac54f330/drivers/gpu/drm/tiny/xenos.c).

## Allocation graphique : confirmation dans le binaire

Dans `xenos_enable`, les instructions à `0xc000000000746328` et `...632c` multiplient largeur × hauteur × octets par pixel ; le résultat est transmis à `dma_alloc_attrs` à `...6338`. Aucun arrondi aux tuiles n'apparaît entre ces multiplications et l'appel. La fonction de recopie en tuiles est incluse dans `xenos_update`.

Cette preuve rapproche le défaut reproduit sous AddressSanitizer du binaire de la console. Elle ne prouve toujours pas une corruption effectivement survenue ni la cause du gel E10.

La taille des pages est mesurée à **65 536 octets**, en accord avec `CONFIG_PPC_64K_PAGES=y`. `dma_direct_alloc` arrondit la demande à cette granularité, ce que montre également son désassemblage. Pour le chemin du pool DMA, le code utilise ensuite un `gen_pool` de granularité `PAGE_SHIFT`. Le callback graphique demande l'allocation avec des flags GFP nuls ; le chemin exact reste conditionné notamment par la cohérence DMA du périphérique.

| Taille | Demande du pilote | Arrondi à 64 Kio | Fin maximale calculée du blit | Dépassement de cet arrondi |
|---|---:|---:|---:|---:|
| 1280 × 720 | 3 686 400 | 3 735 552 | 3 766 272 | 30 720 |
| 1920 × 1080 | 8 294 400 | 8 323 072 | 8 354 816 | 31 744 |

Ce tableau est un calcul conditionnel pour une allocation arrondie à la page ; ce n'est pas une mesure d'une allocation vivante. Une allocation par pages d'ordre supérieur peut réserver davantage. L'arrondi interne ne doit pas être utilisé pour justifier des écritures au-delà de la taille demandée par le pilote. Le correctif candidat arrondit explicitement les dimensions aux macro-tuiles.

Sources : [DMA direct](https://github.com/techflashYT/linux-custom/blob/a293dd19311668900eb1eeb2f6cb01dcac54f330/kernel/dma/direct.c), [pool DMA](https://github.com/techflashYT/linux-custom/blob/a293dd19311668900eb1eeb2f6cb01dcac54f330/kernel/dma/pool.c).

## Troisième défaut : masque de destinations IPI annulé

Le callback `xenon_ipi_send_mask()` calcule la partie destinataires avec `(mask << 16) & 0x3f`. Les six bits de poids faible sont nécessairement nuls après ce décalage. Le binaire confirme que le paramètre `dest` n'est pas lu : seule la priorité est écrite dans le registre d'envoi.

Le correctif candidat inverse l'ordre des opérations : `(mask & 0x3f) << 16`, conformément à l'encodage utilisé par l'autre fonction `xenon_cause_IPI()`.

Le banc compile le callback C réel, avec une écriture MMIO simulée. Pour les 64 masques possibles et quatre priorités, l'original perd les destinations dans les **252 cas à masque non nul** ; la version corrigée satisfait les 256 cas. Le test ne valide pas une émission électrique d'interruption.

**Limite essentielle :** le chemin SMP ordinaire `smp_xenon_message_pass()` appelle `xenon_cause_IPI()`, dont le code conserve la destination. Nous n'avons pas établi qu'un appel au callback fautif a eu lieu pendant cette session. Ce défaut ne permet donc pas d'annoncer une panne générale du SMP, une explication du watchdog réseau ou une cause du gel NAND.

Correctif : `research/patches/0003-xenon-preserve-ipi-target-mask.patch`, non déployé. Test : `research/tests/check-ipi-mask.py`, résultat `binary-audit/ipi-mask-test.json`.

Sources : [interrupt.c](https://github.com/techflashYT/linux-custom/blob/a293dd19311668900eb1eeb2f6cb01dcac54f330/arch/powerpc/platforms/xenon/interrupt.c) et [smp.c](https://github.com/techflashYT/linux-custom/blob/a293dd19311668900eb1eeb2f6cb01dcac54f330/arch/powerpc/platforms/xenon/smp.c).

## Deux choix logiciels à ne pas confondre avec le câblage

Le GPU apparaît sous `01:0f.0` dans Linux parce que `xenon_pci_ecam_map_bus()` transforme cet emplacement en bus 0, slot 2 pour l'accès ECAM. Le pilote force également le premier bus Linux à 1 pour contourner la gestion incomplète du pont. L'inventaire PCI Linux est donc une vue remappée, pas un relevé brut de la topologie physique.

Les IRQ périphériques arrivent sur CPU0 parce que `iic_unmask()` appelle `connect_pci_irq(..., 0)`. L'absence de répartition entre les six threads constatée dans `/proc/interrupts` est cohérente avec cette décision du pilote. Aucune affinité ni aucun registre d'interruption n'a été modifié.

Source : [PCI Xenon](https://github.com/techflashYT/linux-custom/blob/a293dd19311668900eb1eeb2f6cb01dcac54f330/arch/powerpc/platforms/xenon/pci.c).

## Réparation du chemin d'analyse

Les essais initiaux utilisaient des outils dont la présence ne garantissait pas le support de la cible : LLVM fourni par Xcode n'inclut pas PowerPC ; l'objdump de la console a refusé l'ELF64. Le Docker de ce Mac utilise le moteur historique sans buildx, et les paquets GCC croisés big endian demandés initialement n'étaient pas disponibles pour son hôte ARM64.

Le chemin validé utilise maintenant un conteneur Debian ARM64 avec `binutils-multiarch`, LLVM, Clang et LLD. `tools/audit-session.py` contrôle l'empreinte du binaire, son architecture ELF, le moteur Docker, l'image et les formats réellement pris en charge avant de désassembler. Il n'effectue aucun téléchargement et ne redémarre aucune acquisition. Les sorties sont publiées par remplacement atomique seulement après succès ; les états et erreurs sont conservés dans un rapport structuré.

Une exécution complète a produit neuf désassemblages avec succès. Les dix tests mémoire précédents restent distincts du test IPI. Aucune image de noyau modifiée n'est encore compilée ni installée ; disposer de Clang ne prouve pas qu'il compilera cette branche sans adaptation.

Commandes depuis le dépôt :

```sh
docker build -t obsidian360-toolchain:bookworm - < research/Dockerfile.toolchain
python3 tools/audit-session.py --disassemble --output evidence/2026-10-01/binary-audit/session-check.json
```

La première commande n'est nécessaire qu'à la préparation de l'environnement. L'image obtenue et les versions des paquets sont enregistrées dans `toolchain-image.txt` et `toolchain-packages.txt`. Le Dockerfile utilise une balise Debian ; le fichier de provenance identifie l'image effectivement construite, mais il ne promet pas une reconstruction bit à bit dans le futur.
