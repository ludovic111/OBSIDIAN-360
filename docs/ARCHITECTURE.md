# Architecture observée

| Bloc | Preuve sur cet exemplaire | État / limite |
|---|---|---|
| CPU Xenon | PVR `00710500`, six processeurs logiques, 3 200 MHz déclarés | Fréquence non mesurée physiquement |
| RAM | 469 568 Kio utilisables ; 480 Mio exposés comme System RAM | Réservations non toutes attribuées |
| Xenos | PCI `1414:5831`, révision `11`, famille Jasper selon base PCI | Révision de carte à confirmer visuellement |
| Affichage | 1280 × 720, framebuffer 32 bits, Xorg modesetting | Mode hérité de XeLL ; pas de 1080p validé |
| SMC | PCI `1414:580d`, réponses version et AV cohérentes | Pas d’analyse complète du firmware |
| Stockage | Deux SATA `5802/5803`, Hitachi 120 Go, USB SanDisk | Linux persistant fonctionne |
| DVD | PLDS DG-16D2S répond à l’identification ; tiroir fonctionnel selon utilisateur | Aucun disque lu ; cause inconnue, mécanique/laser non diagnostiqués |
| USB | Deux OHCI et deux EHCI | Changement de port a rendu le clavier utilisable |
| Manette | Récepteur `045e:0291`, pilote xpad | js0 et événements désormais reçus ; usage visible à confirmer |
| Réseau | PCI `580a`, sis190 adapté Xenon | Watchdog TX déjà observé, cause non corrigée |
| Audio | PCI `580c` et XMA `5801` | Sous-système audio désactivé dans le noyau |
| NAND | PCI `580b`, pilote qui ne fait qu’identifier le contrôleur | MTD absent ; lecture directe a gelé la machine |

## Démarrage actuel

Système Xbox authentifié → Rock Band Blitz → BadUpdate → FreeMyXe/XeLL → noyau USB → racine Linux interne → bureau.

BadUpdate intervient après le démarrage authentifié. Un effacement du système Xbox supprime ce chemin sans désactiver les contrôles du premier chargeur. Aucune nouvelle faille persistante découverte. Les voies RGH documentées nécessitent une intervention matérielle compatible ; ABadAvatar peut diminuer les manipulations tout en conservant la dépendance au système Xbox.

## Affichage

La largeur et la hauteur lues dans les registres GPU (`0x500`, `0x2d0`) recoupent 1280 × 720. La branche du pilote réellement installée impose également un mode constant 1280 × 720 ; le patch Free60 étudié initialement lit ces dimensions dans les registres. Voir [l'identification binaire](BINARY-AUDIT-2026-10-01.md). Le pilote recopie les pixels dans le format de mémoire attendu. Modifier seulement les dimensions du bureau ne programme pas les horloges et timings HDMI/ANA/HANA. Les relevés historiques 1080p disponibles ne sont pas une recette validée pour cette console.

Les preuves détaillées, sources et inconnues figurent dans [le rapport](rapport-initial.txt).
