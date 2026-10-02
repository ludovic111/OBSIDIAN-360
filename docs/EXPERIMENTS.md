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
| E40 | Préparer un export public, auditer fichiers et objets Git, créer GitHub et contrôler son arbre | 187 fichiers ; MAC masquée dans deux relevés ; 17 chemins exclus ; commit f9da49e sans parent et arbre distant conforme | Historique local non poussé ; publication/verification.json ; refaire audit pour chaque mise à jour |
| E41 | Confronter le format XEX2 aux sources primaires et écrire un parseur Rust borné | Dix tests, 10 000 mutations et neuf cas CLI passent ; aucune lecture des zones opaques instrumentées ; evidence/2026-10-02/xex-inspect | Aucun vrai jeu testé ; pas de décryption, authentification ou exécution ; console non sollicitée |
| E42 | Automatiser le contrôle des fichiers publics et de l'historique Git | Cinq cas synthétiques passent, y compris marqueur retiré du fichier courant mais conservé dans un ancien commit | Audit à exécuter avant commit et push ; scanner de motifs non exhaustif ; export game-analysis désormais inclus |
| E43 | Contrôle vivant après neuf heures et observation du lanceur pendant douze secondes | obsidian4, IceWM, zéro unité en échec ; compteurs E/S et fichier manette inchangés | Fonctionnement prolongé, pas test de charge ; aucune économie d’écriture mesurée ; état du lanceur à diagnostiquer |
| E44 | CD musical inséré par utilisateur ; ioctl CDROM standard et échantillons audio | 20 pistes ; trois secteurs éloignés lus et premier relu avec SHA-256 identique ; optical-cd/ | CD partiellement lisible démontré ; DVD/jeux, lecture intégrale et sortie audio non vérifiés |
| E45 | Just Cause 2 inséré ; lecture standard puis TEST UNIT READY borné | Statut 1, EIO ; CHECK CONDITION, sense 02/3a/00 ; optical-game/ | Aucun support reconnu ; CD lisible mais DVD/jeu non lu ; pas de diagnostic définitif du laser |
| E46 | Diagnostiquer le gel signalé lors du redimensionnement et récupérer les processus graphiques | Relance IceWM forcée rétablit XRandR ; OpaqueMove/Resize à 1, lanceur relancé sans reboot ; desktop-recovery/ | Cause cohérente avec XGrabServer dans le code ; nouvel essai manette demandé, pas encore validé |

| E47 | Recompiler IceWM 4.0.0 et comparer deux redimensionnements XTest sur Xvfb isolé | Ancien mode : deux clients bloqués ; mode direct : 1240×640 → 1180×600 avec réponses ; desktop-resize-regression/ | Premier essai sans vrai redimensionnement rejeté ; mécanisme reproduit hors console, validation physique encore attendue |

| E48 | Remplacer le jeu par le DVD vidéo Big Order et contrôler deux fois la disponibilité | Même sense 02/3a/00 aux deux relevés espacés ; optical-video/ | Deux DVD non reconnus contre CD lisible ; origine exacte et état indépendant des médias non confirmés |

| E49 | Diagnostiquer le refus du bouton Éteindre et demander un arrêt normal administrateur | CanPowerOff challenge, aucun inhibiteur ; timer systemctl poweroff accepté ; poweroff/request.json | Extinction physique non observée directement, bouton graphique non corrigé |
| E50 | Comparer Big Order sous le tableau de bord Xbox à la demande de l’agent | Utilisateur rapporte aucune détection ; stock-dvd/observation.json | Cause exclusivement Linux moins probable ; libellé exact et état indépendant du DVD inconnus |

| E51 | Compiler l’audio original et tester les vrais calculs C avec interfaces simulées | Build échoué : 8 erreurs, 1 avertissement ; 98 géométries hors tampon, 5 boucles dépassant le span ; correctif partiel 0008 passe ; audio-buffers/ | Aucun son activé ; cycle de vie, API, DMA/SMC et négociation ALSA encore à traiter |
| E52 | Vérifier le retour Linux et les permissions du processus graphique réel | obsidian4 vivant, XRandR répond, réglages conservés ; pkcheck autorise les deux arrêts pour le PID du lanceur ; return-linux/ | Correction de portée du challenge mesuré via SSH ; bouton non déclenché, utilisateur absent |

| E53 | Porter les ressources audio et injecter des échecs dans les fonctions C réelles | Objet PPC compilé ; 12 défauts attendus reproduits, 16 scénarios candidat passent ; audio-lifecycle/ | Compilation complète suivie séparément ; protocole, DMA PCM, timer et concurrence non validés ; aucun chargement |

| E54 | Ajouter et tester un envoi SMC borné, puis lier les variantes audio complètes | 19 scénarios SMC, 18 ressources audio ; audio-lifecycle et audio-post avec 70 modules, zéro avertissement ; smc-post/ | Pas de chargement ; vieux chemins SMC non bornés, protocole audio et DMA PCM à poursuivre |

| E55 | Migrer les PCM vers la mémoire DMA gérée ALSA et tester les callbacks réels | 20 scénarios de ressources, 12 de callbacks, régression de 16 369 tailles ; noyau audio-pcm + 70 modules sans avertissement ; audio-pcm/ | Aucun chargement ; timer/concurrence/protocole non validés |
| E56 | Reconnexion SSH après le retour de l’utilisateur, interfaces standard en lecture seule | obsidian4, uptime 5 139,44 s, aucun service en échec, framebuffer 1280×720 ; audio-pcm/console-status.json | Pas un test visuel, de charge ou audio |

| E57 | Reproduire le timer audio non armé et ses fausses notifications, puis ajouter suivi par sortie et sync_stop | 15 scénarios de suivi dont fermeture concurrente contrôlée, 20 ressources et 15 PCM passent ; audio-poll/ | Noyau final haute résolution + 70 modules vérifiés, sans avertissement ; protocole et matériel non validés, aucun chargement |

| E58 | Exécuter la routine pointer et les conversions ALSA réelles ; examiner le contrat ack et un émulateur | 96 cas de file alternante sans nouvelles données, débordement signé attendu, publication partielle conditionnelle ; audio-submission/ | Remplacement à concevoir avec drain/reset ; émulateur audio insuffisant pour valider le protocole |

| E59 | Écrire une file PCM originale avec engagements partiels, drain silencieux et compteur borné | 512 tailles, 54 008 opérations, 24 544 033 frames comparées ; compilation et module de liaison PPC ; audio-queue/ | Aucun adaptateur ALSA ni accès matériel ; protocole/achèvement DMA encore ouverts |

| E60 | Intégrer file, ack, drain/reset et suivi au pilote candidat ; tester les callbacks et le rollback ALSA réels | 15 scénarios dont 512 géométries et fermeture concurrente contrôlée, 20 ressources, régression de file ; noyau + 70 modules sans avertissement ; audio-adapter/ | Fin du dernier bloc non décodée, stagnation = XRUN ; aucun chargement |
| E61 | Reconnexion SSH par interfaces standard en lecture seule | obsidian4, uptime 9 327,35 s, aucun service en échec listé, framebuffer 720p ; audio-adapter/console-status.json | Réactivité visuelle et audio non vérifiés |

| E62 | Examiner l'historique audio, comparer les registres SiS et corriger les longueurs | 16 384 descripteurs par variante, 15 callbacks et 20 ressources ; noyau audio-bytes + 70 modules, volume Linux sans avertissement ; audio-protocol/ | Correspondance matérielle non mesurée ; fin DMA distincte de sortie audio, statuts/FIFO ouverts |

| E63 | Séparer contrôle et acquittement sous modèle SiS ; compiler le module | 4 096 transitions par variante : 3 584 pertes simulées avant, zéro après ; 15 callbacks, 20 ressources, 16 384 descripteurs ; audio-control/ | Hypothèse matérielle non validée ; module seul recompilé contre audio-bytes, aucun chargement |
| E64 | Configuration PCI audio puis trois lectures ciblées de quatre registres | Commande PCI 0x0006, aucun pilote ; contrôles 0x1d08001c et index 0x00008000 / 0x00009616 inchangés ; SSH maintenu ; audio-control/observer-* | Douze lectures, zéro écriture ; calcul de mapping corrigé avant exécution, 31 744 cas ; interprétation SiS, arrêt DMA et sortie sonore non prouvés |

| E65 | Une écriture STOP analogique conditionnée après tests et vérification ELF32 | 0x1d08001c → 0x0008001d puis 0x0000001d, index zéro, numérique inchangé ; SSH répond ; audio-stop/ | Dix lectures au total, une écriture ; indicateur DCH étayé, pas de preuve de fin des transactions/FIFO ; analogique laissé STOP |
| E66 | Exécuter trois fonctions ALSA réelles avec erreurs de callbacks | 144 cas ASan/UBSan, 24 détachements dont 12 libérations dynamiques malgré une erreur ; audio-stop/free-contract.json | Contrat logiciel, pas bogue ALSA ; un retour erreur seul ne préserve pas le tampon et ne suffit pas pour un arrêt matériel échoué |

| E67 | Acquitter séparément trois bits analogiques après tests de 512 refus | 0x1d → 0x19 → 0x11 → 0x01 ; numérique inchangé, SSH répond ; audio-ack/ack-bit*.json | Trois écritures, 24 lectures ; W1C observé au repos, signification des événements sous flux non prouvée |
| E68 | Écrire reset depuis le statut arrêté analogique | 0x02000000 écrit, lecture 0x00000001 ; index zéro, numérique inchangé ; audio-ack/reset-stopped.json | Une écriture, huit lectures ; auto-effacement compatible, effets internes non démontrés car état observé inchangé |
| E69 | Comparer sept horodatages console/Mac en SSH persistant et lire le device tree | Environ −0,25 % sur 60 s ; 50 MHz déclarés, 49,8734–49,8759 MHz compatibles avec la mesure relative ; clock-calibration/ | Mac non étalonné, aucune reconfiguration ; horodatages console décalés et durée historique à interpréter |
| E70 | Ajouter une conversion timebase optionnelle et construire un noyau distinct | obsidian-clock + image + 65 modules sans avertissement, ELF/sections/vermagic vérifiés ; timebase-build/ | Aucune installation/initramfs ni validation après boot ; correction limitée à cette piste mesurée |
| E71 | Préparer initramfs, modules et entrée USB distincte pour obsidian-clock | Image 16 171 806 octets, 43 modules extraits conformes, 65 installés ; entrée obsidian_clock, défaut linux_hdd et secours préservés ; relecture après remontage réussie ; timebase-boot/ | Aucun reboot ni validation de cadence ; essai physique demandé, horodatages console non corrigés |

## Analyse de l’incident E10

La documentation décrit une fenêtre flash en lecture seule, sans ECC. Cela ne garantissait pas que la méthode de lecture large employée fonctionnerait sur cette combinaison matériel/noyau. Le programme a ouvert `resource1` avec O_RDONLY, utilisé PROT_READ, et ne contenait aucune commande d’effacement ou de programmation. Le gel est corrélé à cette lecture ; son mécanisme exact n’a pas été établi.

La sonde est conservée comme texte dans `research/blocked/` afin de pouvoir l’examiner. Elle ne fait pas partie des outils à exécuter. Privilégier une acquisition XeLL ou une interface matérielle documentée avec contrôle des résultats.

## Fiche pour les prochaines expériences

- Question précise et hypothèse.
- État matériel/logiciel et moyen de retour au fonctionnement.
- Action exacte et limites de durée/volume.
- Preuve conservée, hash, résultat observé.
- Incertitudes, effet sur le système, prochaine étape.
