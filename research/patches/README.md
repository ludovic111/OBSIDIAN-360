# Correctifs et statut de validation

Les correctifs 0001–0007 sont des résultats d'analyse. Les six correctifs Linux (tous sauf 0002) ont été compilés ensemble dans le candidat obsidian4, avec ses modules et son image de démarrage. Ses fichiers sont préparés sur la console et sur la clé pour un essai optionnel ; son démarrage a ensuite été confirmé en E38 et son retour après essai du système stock en E52. XeLL n'a pas été reconstruit. Le système fonctionnel reste l'entrée par défaut.

- `0001-xenos-pad-tiled-framebuffer.patch` : taille d'allocation arrondie aux macro-tuiles 32 × 32. Base : `xenos.c` ajouté par le patch Linux 6.18-xenon0.30, commit `498bbe1910f707ceba0535276d75a3e6ad0b7df4` du dépôt Free60Project/linux-kernel-xbox360.
- `0002-xell-allocate-physical-page.patch` : tampon dimensionné pour les 528 octets de la page NAND brute. Base : Free60Project/xell-reloaded, commit `a36ed6b7dae940e47e472a20fd14b0616ddc8cef`.
- `0003-xenon-preserve-ipi-target-mask.patch` : corrige l'ordre masque/décalage dans le callback IPI. Base : techflashYT/linux-custom, commit `a293dd19311668900eb1eeb2f6cb01dcac54f330`. 256 combinaisons testées par variante avec MMIO simulée ; le chemin SMP ordinaire appelle une autre fonction.
- `0004-xenon-bound-smc-reply-cache.patch` : borne la recherche dans le cache SMC à ses treize entrées. Même base linux-custom ; quatre cas ASan vérifient l'original et le candidat, sans messages envoyés au matériel.
- `0005-xenon-led-lifecycle.patch` : init/exit unique, ressources gérées, erreurs d'allocation vérifiées, envoi sans réponse et sous verrou. Même base linux-custom ; 21 cas ASan/UBSan hors console.
- `0006-xenon-export-smc-ready.patch` : export GPL de la disponibilité du cœur SMC, nécessaire au pilote LED en module. S'applique après 0004 ; le cœur est construit par PPC_XENON, indépendamment de l'interface caractère XENON_SMC.
- `0007-xenon-isolate-boot-image-recipe.patch` : exclut l'image Xenon de la recette générique concurrente et supprime une copie vers un chemin local propre au développeur amont. Le build obsidian4 ne produit plus ces avertissements.

Les dix cas du premier banc AddressSanitizer passent : les trois erreurs attendues sont reproduites dans les sources originales ; les variantes corrigées et les contrôles sans dépassement terminent normalement. Les interfaces matérielles sont simulées. Le pilote graphique a ensuite été compilé dans le vmlinux candidat complet avec LLVM 16 ; XeLL n'est pas compilé comme chargeur PowerPC complet. Les preuves du dernier candidat sont dans `evidence/2026-10-01/kernel-build-obsidian4/`. Les avertissements LED et de recettes concurrentes sont résolus.

Avant promotion en système par défaut : valider le démarrage, le bureau, les périphériques et le retour au système précédent. L'initramfs et l'ensemble optionnel sont préparés, voir `docs/BOOT-PREFLIGHT-2026-10-01.md`. Le candidat LLVM ne reproduit pas bit à bit le build GCC installé. Le défaut HTTP ne valide ni les statuts SFCX, ni les ECC, ni les blocs défectueux.

Ne pas appliquer ces diffs aux archives de preuves. Aucun flash NAND requis pour le test graphique envisagé.

## Audio : candidat partiel, non compilé et non activé

`0008-xenon-audio-buffer-geometry.patch` cible le même snd-xenon.c (GPL-2.0-or-later). Il borne les tailles à des multiples de 128 octets et empêche la boucle de cache de continuer pour une taille négative. Tests du C extrait sur hôte : 16 369 tailles, 512 acceptées par le candidat, aucune géométrie hors tampon parmi elles. Ce diff ne constitue pas un pilote utilisable : portage des API, cycle de vie, transport SMC, DMA et notifications ALSA restent à résoudre. Voir `docs/AUDIO-BUFFER-AUDIT.md`.
