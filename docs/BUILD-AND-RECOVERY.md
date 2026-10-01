# Construire et comprendre l'installation

Ce projet documente un exemplaire et une installation existante ; il ne fournit pas encore un installateur universel. Un clone permet de lire les analyses et construire les composants locaux. Il n'inclut pas les jeux, payloads binaires, firmware, secrets ou dumps nécessaires à reproduire toute la chaîne d'origine.

## Noyau obsidian4

Prérequis : Python 3, Docker avec conteneurs Linux, espace de compilation et source Linux exacte. Le build vérifié utilise l'image décrite par `research/Dockerfile.kernel-build`, LLVM 16, source `techflashYT/linux-custom@a293dd19311668900eb1eeb2f6cb01dcac54f330`. L'archive de référence a pour SHA-256 `b3e0b3a92523f334e594e07b57da58e459b4d21630ec1366aba48297da9282f0`. Ne pas substituer une branche actuelle.

Sur une copie neuve de cette source, appliquer dans l'ordre les correctifs Linux 0001, 0003, 0004, 0005, 0006 et 0007 de `research/patches/` (`patch -p1 --dry-run`, puis application dans l'arborescence cible). 0002 concerne XeLL et ne doit pas être appliqué au noyau. Conserver source et sortie séparées. Copier `evidence/2026-10-01/kernel-build-obsidian4/candidate.config` vers `.config` du répertoire de sortie ; cette configuration provient de l'exemplaire étudié, ce n'est pas une garantie pour une autre révision.

```sh
docker build -t obsidian360-kernel:llvm16 -f research/Dockerfile.kernel-build .
python3 tools/build-kernel.py --source CHEMIN_SOURCE --output CHEMIN_BUILD --jobs 4 --localversion=-obsidian4 --target vmlinux
python3 tools/build-kernel.py --source CHEMIN_SOURCE --output CHEMIN_BUILD --jobs 4 --localversion=-obsidian4 --target modules
python3 tools/build-kernel.py --source CHEMIN_SOURCE --output CHEMIN_BUILD --jobs 4 --localversion=-obsidian4 --target zImage.xenon
python3 tools/check-kernel-artifacts.py --build CHEMIN_BUILD --output CHEMIN_RAPPORT.json
```

Les chemins en capitales sont à remplacer. Ne pas lancer deux builds concurrents : le wrapper conserve chaque journal et refuse de masquer un conteneur déjà présent. L'image est résolue en identifiant local au lancement, mais reconstruire aujourd'hui le Dockerfile ne garantit pas les mêmes paquets ni un binaire identique. Les journaux, versions, configuration et SHA du build vérifié sont dans `kernel-build-obsidian4/`. Cette procédure décrit les éléments déjà utilisés ; un test de reproduction depuis un clone entièrement neuf reste à effectuer.

Les tests hors console et leurs sources nécessaires sont décrits dans `research/tests/README.md`. Aucun de ces builds ne flashe ni ne redémarre la console.

## Installation existante et récupération

Le système vérifié utilise ArchPOWER sur partition ext4 interne avec swap, noyau PPC64 et applications PPC32. Xorg modesetting sans accélération démarre via autologin tty1/startx, avec IceWM et le lanceur de `desktop/`. Les fichiers de bureau ne suffisent pas à provisionner une autre console sans préparer les paquets, comptes, permissions et stockage.

Le candidat est séparé : modules dans `/usr/lib/modules/6.18.11-xenon-obsidian4`, noyau et initramfs dans un répertoire USB `obsidian4/`. Les modules doivent correspondre exactement au noyau. La génération décrite dans BOOT-PREFLIGHT utilise mkinitcpio avec un répertoire de staging et `--nopost`, puis vérifie les fichiers extraits ; elle n'écrase pas `/boot` ni l'initramfs précédent.

Chaîne réelle : démarrage stock, Rock Band Blitz, XeLL, choix du noyau USB, racine Linux interne. Débrancher Ethernet avant ce lancement, le reconnecter après Linux. Le menu conserve `linux_hdd` par défaut et une entrée obsidian4 distincte. En cas de candidat non fonctionnel, sélectionner le noyau précédent et conserver le système live de récupération. Un retour à linux_hdd après le dernier essai obsidian4 n'a pas encore été revérifié ; ne pas le présenter comme un test récent.

Aucune procédure logicielle ne restaure aujourd'hui une NAND endommagée sur cet exemplaire : sauvegarde brute adaptée et méthode matérielle indépendante non validées. Ne pas remplacer la NAND pour tester le démarrage direct. Les anciens scripts de partitionnement et la sonde flash ayant figé la console restent des archives locales, jamais des étapes d'installation à rejouer.
