# Journal des expériences

| ID | Action | Résultat et preuve | Suite |
|---|---|---|---|
| E01 | Exploit Rock Band Blitz et XeLL depuis USB | Démarrage Linux observé puis SSH vérifié | Chemin de récupération à conserver |
| E02 | Installation sur Hitachi 120 Go autorisée par utilisateur | Racine `/dev/sda1` ext4 et swap 2 Gio vérifiés après démarrage réel | Ne pas rejouer le partitionnement |
| E03 | Mise à jour et installation du bureau | Service pacman terminé `Result=success` | SSH a nécessité un redémarrage local |
| E04 | Xorg fbdev | Échec `no screens found` | Remplacé par modesetting ; permissions initiales Xorg rétablies |
| E05 | Xorg modesetting, rendu logiciel | Capture 1280 × 720 vérifiée | Support 1080p manquant |
| E06 | XTest puis clics sur clavier visuel | Terminal a reçu `xbox360`, puis `123` et Entrée | Manette physique encore à confirmer |
| E07 | Demande XRandR 1920 × 1080 sur None-1 | `cannot find mode 1920x1080` | Développer et valider la programmation vidéo |
| E08 | Inventaire PCI/USB/configuration/dmesg | 12 fonctions PCI et preuves copiées sur Mac | État daté, pas télémétrie continue |
| E09 | Requêtes SMC d’état, hwmon, lecture ANA et registres vidéo ciblés | Réponses cohérentes, températures, 1 024 octets ANA, 15 registres GPU | Rapatriement vérifié en E11 |
| E10 | Lecture mmap PROT_READ de BAR1 du contrôleur flash | SSH et ping perdus, utilisateur confirme écran figé ; aucun dump validé | Sonde bloquée. Cause inconnue ; ne pas relancer. Aucun flash/effacement envoyé |
| E11 | Redémarrage utilisateur et reconnexion SSH | Racine ext4 interne, IceWM et lanceur actifs ; fichiers SMC/ANA/GPU récupérés et SHA-256 concordants | Incident E10 récupéré, cause encore inconnue |
| E12 | Lecture du diagnostic de manette après redémarrage | js0 présent, device_open=true, 4 557 événements | Utilisation visible à confirmer |
| E13 | Inventaire vivant via interfaces noyau standards | SSH, racine, bureau, températures et réseau vérifiés ; `deep-audit/runtime.json` | Aucun accès MMIO/NAND brut |
| E14 | Décodage hors ligne GPU et comparaison ANA/libxenon | Paramètres horizontaux HDMI 720p concordants ; 109/121 entrées ANA hors sentinelles identiques | Total vertical/horloge non mesurés ; six différences expliquées par écritures de constantes |
| E15 | Fonction C réelle xenos_blit dans banc ASan sur Mac | Dépassements heap en 720p/1080p reproduits ; allocation arrondie passe quatre tailles | Correctif candidat, noyau complet non compilé, non déployé |
| E16 | Gestionnaire HTTP XeLL réel avec SFCX simulé sur Mac | Dépassement stack 512/528 reproduit ; correction transmet deux pages intactes | Statut/ECC à traiter ; aucune acquisition réelle de NAND |
| E17 | Revue du pilote audio et des en-têtes Linux 6.18 | API historiques absentes, risques DMA/SMC/IRQ identifiés | Portage et compilation requis avant activation |
| E18 | Provenance du noyau et observation pacman | Paquet linux-xenon 6.18.11-1 ; avertissement trousseau public manquant | Binaire non désassemblé ; trousseau à diagnostiquer avant installation |
| E19 | Vérification finale du journal graphique sur la console | Allocation annoncée 0x384000 = 3 686 400 octets pour 720p ; bureau actif après 22 minutes | Corrobore la taille de F01, sans prouver une corruption ni la cause de E10 |
| E20 | Acquisition vmlinux/System.map et comparaison ELF | SHA-256 locaux/distants concordants ; six sections identiques à l'image de démarrage, dont .text | Code sur disque identifié, sans lecture de mémoire vivante |
| E21 | Retrouver la recette exacte puis désassembler neuf fonctions | Source linux-custom identifiée ; mode constant 720p et calcul d'allocation confirmés | Corrige l'attribution antérieure au patch Free60 |
| E22 | Analyse DMA, PCI et routage IRQ | Pages 64 Kio ; GPU remappé par logiciel ; périphériques routés CPU0 | Chemin d'allocation précis non instrumenté sur la console |
| E23 | Callback IPI réel testé avec MMIO simulée | 252/256 masques perdus dans l'original ; 256/256 corrects avec le candidat ; anomalie également présente dans le binaire | Le chemin SMP ordinaire utilise une autre fonction ; impact vivant non établi |
| E24 | Corriger le chemin d'outillage | Incompatibilités PowerPC64 des anciens outils contournées ; environnement multiarchitecture construit et audit complet réussi | Aucun échec ne doit être assimilé à une preuve ; compilation noyau encore à faire |

## Expériences suivantes hors console

| ID | Action | Résultat et preuve | Suite |
|---|---|---|---|
| E25 | Audit du cache SMC, test du C réel et désassemblage installé | Dépassement de tableau confirmé ; quatre cas ASan aux résultats attendus, recherche corrigée sur 256 identifiants ; `smc-audit/` | Aucun message matériel ; concurrence et attentes encore à traiter |
| E26 | Archive source vérifiée, LLVM 16, olddefconfig puis build vmlinux avec trois correctifs Linux | Code 0, ELF64 PowerPC big-endian vérifié, `6.18.11-xenon-obsidian1` ; `kernel-build/` | Avertissement du pilote LED restant ; modules, image de démarrage et essai réel non validés |
| E27 | Diagnostic des interruptions Codex et suivi du build existant | Erreur structurée `cyber_policy` sur cinq tours ; processus local encore vivant puis terminé avec succès | Contrôle de plateforme non modifiable par les scripts ; voir SESSION-RECOVERY |
| E28 | Revue du pilote LED, désassemblage et injection de fautes hors console | 21 cas ASan/UBSan passent pour le candidat ; allocation/nettoyage/init/exit et envoi corrigés ; `led-audit/` | Aucun ordre SMP réel ni état visuel validé |
| E29 | Compiler le pilote LED comme module PowerPC | Original : redéfinitions init/exit ; premier correctif : symbole SMC absent ; après export GPL : succès sans diagnostic | Échecs intermédiaires conservés ; module non chargé |
| E30 | Construire noyau, modules et image XeLL obsidian3 | Codes 0 ; 65 modules et six sections de contenu vérifiés ; `kernel-build-obsidian3/` | Deux avertissements Makefile de recette concurrente ; initramfs, ensemble séparé et démarrage réel non validés |

## Préparation du démarrage et lecteur

| ID | Action | Résultat et preuve | Suite |
|---|---|---|---|
| E31 | Vérifier SSH, configuration de démarrage et clé montée en lecture seule | Noyau installé vivant, racine interne, zéro service en échec ; empreintes noyau/initramfs/récupération conservées | `boot-preflight/runtime.json` et `usb.json` |
| E32 | Nettoyer la recette de l'image et construire obsidian4 | Trois cibles terminées code 0 sans avertissement ; 65 modules et six sections vérifiés | `kernel-build-obsidian4/` |
| E33 | Générer un initramfs depuis les modules candidats dans un répertoire distinct | depmod/mkinitcpio/lsinitcpio codes 0 ; 43 modules extraits identiques et exécutables PPC vérifiés | Copie Mac à empreinte identique ; pas encore de démarrage |
| E34 | Copier les nouveaux modules et une entrée USB optionnelle | 65 modules présents, kernel/initrd vérifiés, menu sauvegardé ; linux_hdd par défaut et fichiers antérieurs intacts | `boot-preflight/staging-result.json` ; procédure archivée, ne pas rejouer |
| E35 | Identifier le lecteur via sysfs/proc/journal et analyser le repli du pilote | DG-16D2S ; page de capacités non exploitable ; utilisateur : tiroir s'ouvre, aucun disque lu | Cause non établie ; aucun disque lu ni commande mécanique envoyée |
| E36 | Premier essai manuel demandé, photo et retour utilisateur | Écran bloqué après /init/udev/détection USB ; aucune sélection obsidian4 confirmée, noyau inconnu, SSH absent | Ne pas attribuer au candidat ; récupération linux_hdd demandée ; `first-boot-observation.json` |
| E37 | Exécuter hors console les fonctions vidéo f1/f2 réelles avec MMIO simulée | 26 entrées, 1 846 écritures tracées, ASan/UBSan sans erreur ; 12/13 registres communs HDMI 720p concordent avec la capture ancienne | Aucune programmation matérielle ni horloge validée ; `video-mode-trace/modes.json` |
| E38 | Utilisateur sélectionne obsidian dans XeLL ; vérification SSH du système démarré | obsidian4 confirmé, racine interne, bureau actif, zéro service en échec, udev settle code 0 ; framebuffer corrigé 0x398000 | `obsidian4-first-boot/` ; un démarrage prouvé, stabilité prolongée et cause de E36 inconnues |
| E39 | Référence CPU/mémoire/boot via interfaces standard et courts tests userspace | Cible graphique ~34,1 s, 118,5 Mio disponibles au relevé, SHA-256 médian 22,553 Mio/s ; outils et preuve `performance-baseline/` | Deux requêtes systemd expirées ; suivi ciblé réussi ; slabinfo absent, maintenant facultatif ; aucune configuration changée |

## Analyse de l’incident E10

La documentation décrit une fenêtre flash en lecture seule, sans ECC. Cela ne garantissait pas que la méthode de lecture large employée fonctionnerait sur cette combinaison matériel/noyau. Le programme a ouvert `resource1` avec O_RDONLY, utilisé PROT_READ, et ne contenait aucune commande d’effacement ou de programmation. Le gel est corrélé à cette lecture ; son mécanisme exact n’a pas été établi.

La sonde est conservée comme texte dans `research/blocked/` afin de pouvoir l’examiner. Elle ne fait pas partie des outils à exécuter. Privilégier une acquisition XeLL ou une interface matérielle documentée avec contrôle des résultats.

## Fiche pour les prochaines expériences

- Question précise et hypothèse.
- État matériel/logiciel et moyen de retour au fonctionnement.
- Action exacte et limites de durée/volume.
- Preuve conservée, hash, résultat observé.
- Incertitudes, effet sur le système, prochaine étape.
