# Noyau candidat Linux — validation des fichiers

Point de contrôle E30 : **6.18.11-xenon-obsidian3**, compilé sur le Mac dans Docker Linux ARM64 avec Clang/LLVM 16. Cette version n'a pas été installée ni démarrée sur la Xbox. Elle est suivie d'obsidian4 : voir [préparation et essai du dernier candidat](BOOT-PREFLIGHT-2026-10-01.md) et [état courant](STATE.md).

## Provenance et différences

Base `techflashYT/linux-custom@a293dd19311668900eb1eeb2f6cb01dcac54f330`, identifiée depuis la recette du noyau installé. L'archive complète a été vérifiée contre l'empreinte SHA-256 de cette recette. Configuration issue du noyau installé, passée par `olddefconfig` ; la configuration finale est conservée avec chaque build. L'identité de l'image de compilation et les empreintes des correctifs sont dans `kernel-build-obsidian3/provenance.json`.

Cinq correctifs Linux sont appliqués : 0001 allocation du framebuffer, 0003 masque IPI, 0004 cache SMC, 0005 cycle de vie LED et 0006 export de la fonction de disponibilité SMC. Le correctif XeLL 0002 n'appartient pas à cette compilation. Le candidat reste en 720p avec le son désactivé.

Ce n'est pas une reconstruction binaire identique du paquet : il utilise LLVM 16 au lieu de GCC, une autre date de compilation et un suffixe distinct. Les fichiers du noyau installé et du premier candidat sont conservés hors Git.

## Résultats

| Vérification | Résultat | Limite |
|---|---|---|
| Construction de vmlinux | Code 0, sans avertissement dans le journal | Aucun démarrage effectué |
| Modules sélectionnés | 65 fichiers, build code 0 sans avertissement | Aucun chargement réel |
| Format des modules | ELF64 PowerPC big-endian, version conforme à `6.18.11-xenon-obsidian3` | Ne prouve pas l'ABI de toutes les interactions matérielles |
| Pilote LED séparé | Compilation et modpost passent après ajout de l'export SMC | Test de construction, pas de chargement |
| Image `zImage.xenon` | Code 0, ELF32 PowerPC big-endian avec contenu de noyau 64 bits | Compatibilité physique du démarrage non testée |
| Contenu après conversion | `.head.text`, `.text`, `.rodata`, `.init.text`, `.data`, `.notes` identiques à vmlinux | Contrôle de ces six sections, pas exécution |

Le fichier `arch/powerpc/boot/Makefile` définit deux recettes pour `zImage.xenon` : une règle générique avec wrapper, puis une règle spécifique qui retire les symboles et convertit l'en-tête ELF. Make signale le remplacement et utilise la règle spécifique. Cela explique les deux avertissements de fabrication ; aucune erreur de compilateur ne les accompagne. Nettoyer cette concurrence avant de stabiliser la procédure de fabrication. Une copie vers un chemin TFTP absolu du développeur amont figure aussi dans la recette ; ce chemin n'existe pas dans notre conteneur et aucun fichier n'a été envoyé sur le réseau.

## Reproduire les contrôles locaux

Une arborescence source préparée et un répertoire de sortie contenant `.config` sont requis ; les outils ne téléchargent pas de source et ne déploient rien. Construire successivement les cibles, avec **le même suffixe** et sans deux builds concurrents :

```sh
python3 tools/build-kernel.py --source CHEMIN_SOURCE --output CHEMIN_BUILD --jobs 4 --localversion=-obsidian3 --target vmlinux
python3 tools/build-kernel.py --source CHEMIN_SOURCE --output CHEMIN_BUILD --jobs 4 --localversion=-obsidian3 --target modules
python3 tools/build-kernel.py --source CHEMIN_SOURCE --output CHEMIN_BUILD --jobs 4 --localversion=-obsidian3 --target zImage.xenon
python3 tools/check-kernel-artifacts.py --build CHEMIN_BUILD --output CHEMIN_RAPPORT.json
```

Le vérificateur utilise `modules.order`, vérifie chaque module sélectionné et publie son rapport seulement après validation des formats, versions et sections. Les SHA-256 sont dans `kernel-build-obsidian3/artifacts.json`. Les journaux sont datés ; ne pas écraser les preuves historiques lors d'une reprise.

## Avant un essai réel

Il reste à préparer et vérifier les modules et l'initramfs correspondant au candidat dans un ensemble de démarrage distinct, puis conserver une sélection explicite du système existant et de la récupération USB. Le simple fichier `zImage.xenon` validé ici ne suffit pas à démontrer cet ensemble. Pas de modification de la NAND, des eFuses, du firmware stock ou du démarrage par défaut dans ces expériences.
