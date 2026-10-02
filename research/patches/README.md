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

## Audio : candidats compilés, non activés

`0008-xenon-audio-buffer-geometry.patch` cible le même snd-xenon.c (GPL-2.0-or-later). Il borne les tailles à des multiples de 128 octets et empêche la boucle de cache de continuer pour une taille négative. Tests du C extrait sur hôte : 16 369 tailles, 512 acceptées par le candidat, aucune géométrie hors tampon parmi elles. Ce diff ne constitue pas un pilote utilisable : portage des API, cycle de vie, transport SMC, DMA et notifications ALSA restent à résoudre. Voir `docs/AUDIO-BUFFER-AUDIT.md`.

`0009-xenon-audio-resource-lifecycle.patch` s’applique après 0008 : propriétaire ALSA unique, chemins d’erreur, API DMA/timer, transport SMC partagé, retrait du faux gestionnaire IRQ. Objet PowerPC compilé et seize scénarios de ressources validés dans le modèle ; toujours non activable. Voir `docs/AUDIO-LIFECYCLE-AUDIT.md`.

`0010-xenon-bounded-smc-post.patch` ajoute une API d’envoi sans attente de verrou, à budget de polling, et l’utilise dans l’audio. Dix-neuf scénarios SMC et dix-huit de ressources passent. Les variantes 0008/0009 puis 0008/0009/0010 compilent noyau + 70 modules sans avertissement. Aucun chargement ; anciens chemins SMC encore non bornés. Voir `docs/SMC-BOUNDED-POST.md`.

`0011-xenon-audio-coherent-pcm.patch` passe aux tampons gérés ALSA et à leur adresse CPU existante, supprime le remappage/cache privés et ajoute contraintes et contrôles défensifs. Vingt scénarios ressources, douze callbacks et régression géométrique passent ; noyau et 70 modules compilés. Timer et protocole restent incomplets, aucun chargement. Voir `docs/AUDIO-PCM-DMA.md`.

`0012-xenon-audio-stream-polling.patch` ajoute le suivi par sortie et la synchronisation avant libération ; 15 scénarios de suivi, 20 ressources et 15 PCM passent hors matériel. Configuration haute résolution activée, noyau final et 70 modules vérifiés sans avertissement, non activé. Voir `docs/AUDIO-STREAM-POLLING.md`.
