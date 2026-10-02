# Journal chronologique

Horodatages en UTC. Les expériences antérieures E01–E38 sont décrites dans EXPERIMENTS avec leurs preuves datées ; ne pas inventer d'horodatage de manipulation lorsqu'il n'a pas été enregistré.

## 2026-10-01 — 21:45:47 — E38

- Objectif : identifier le noyau réellement démarré après sélection utilisateur.
- Action : SSH, état du bureau, udev, journal graphique et interfaces standard.
- Observation : obsidian4, racine interne, Xorg/IceWM actifs, allocation 0x398000, zéro service en échec.
- Résultat : premier démarrage candidat confirmé.
- Interprétation : activation effective du correctif graphique ; pas de preuve de stabilité prolongée ni de cause du gel antérieur.
- Suite : établir une référence de performances sans changer la configuration.

## 2026-10-01 — 21:50:15 — E39

- Objectif : mesurer boot, mémoire, topologie et deux charges userspace courtes.
- Action : collect-baseline.py avec trois échantillons puis collect-boot-detail.py.
- Observation : cible graphique à 34,1 s, 118,5 Mio disponibles au premier relevé, SHA-256 médian 22,553 Mio/s ; deux analyses systemd expirées.
- Résultat : référence conservée et suivi ciblé réussi ; /proc/slabinfo absent, erreur initiale conservée puis interface rendue facultative.
- Interprétation : référence d'un démarrage ; la copie Python ne mesure pas la RAM brute, la cible graphique ne mesure pas le bureau visible.
- Suite : décomposer le démarrage et la mémoire ; comparer toute optimisation future à une méthode équivalente.

## 2026-10-01 — révision d'objectif pendant E39

- Objectif : intégrer le texte de référence actualisé sans perdre l'historique.
- Action : conserver les deux versions détaillées, leurs empreintes et une carte des inconnues.
- Observation : ajout de l'analyse des jeux, de la modernisation, de l'autonomie nocturne et d'une autorisation GitHub publique conditionnée à l'audit.
- Résultat : OBJECTIVE, RESEARCH-MAP et BLOCKED mis à jour.
- Interprétation : la publication n'autorise pas l'envoi des données confidentielles ni de l'ancien historique privé.
- Suite : export public contrôlé, licence et instructions reproductibles. Aucun reboot demandé à l'utilisateur absent.

## 2026-10-01 — 22:01 UTC — E40

- Objectif : publier le projet autorisé sans exporter l'historique privé.
- Action : export textuel à sélection explicite, contrôle des empreintes, recherche de secrets/identifiants, compilation syntaxique des scripts Python, nouveau Git avec identité de projet, audit des objets atteignables puis création/push GitHub.
- Observation : première revue trouve l'adresse MAC dans deux relevés ; ajout d'une règle bloquante et masquage dans les dérivés. Originaux locaux intacts. Attributions amont distinguées des données personnelles de l'opérateur.
- Résultat : 187 fichiers publics, 17 chemins exclus de la sélection initiale ; premier commit f9da49e sans parent. L'API GitHub confirme visibilité publique et arbre identique à l'export contrôlé.
- Interprétation : publication de connaissances/outils et de preuves sélectionnées, pas distribution de firmware ou de jeux. Le scanner de motifs n'est pas une preuve universelle d'absence de secrets.
- Suite : maintenir les deux historiques séparés, actualiser les exports après audit, poursuivre les mesures et l'analyse de formats avec échantillons synthétiques en attendant des supports légitimes accessibles.

## 2026-10-02T07:07:37.271107+00:00 — E41

- Objectif : préparer une inspection reproductible des exécutables de jeux sans acquérir ni distribuer de binaire propriétaire.
- Action : lecture des sources Xenia figées et Free60, implémentation Rust originale, tests structurels et CLI avec échantillons synthétiques.
- Observation : différence de traitement des clés à taille zéro dans les références ; dix tests Rust et neuf cas CLI passent, ainsi que 10 000 mutations déterministes.
- Résultat : JSON structurel, bornes vérifiées, champs opaques non lus dans le test instrumenté ; fichiers d'entrée inchangés.
- Interprétation : outil de métadonnées validé sur l'hôte ; pas d'authentification, de désassemblage de jeu ou de validation sur fichier commercial.
- Suite : validation de compatibilité sur entrée légitime, formats des imports et PE, puis profilage ; export et audit public avant publication. Aucune interaction avec la console pendant E41.

## 2026-10-02T07:10:20.726239+00:00 — E42

- Objectif : rendre reproductible l'audit exigé avant chaque publication.
- Action : contrôle du manifeste, de la sélection, des sommes de preuve et des objets Git atteignables ; cinq cas dans un dépôt jetable.
- Observation : le contrôle trouve aussi le marqueur factice retiré du fichier courant mais toujours présent dans un ancien commit.
- Résultat : cinq cas aux résultats attendus ; historique public existant audité sans anomalie détectée.
- Interprétation : contrôle de motifs et provenance, avec limites explicites ; ne démontre pas l'absence de tout secret arbitraire.
- Suite : exporter les sources Rust et leurs preuves, auditer avant commit puis avant push, vérifier le SHA distant.

Publication E41/E42 vérifiée à 2026-10-02T07:14:53.060765+00:00 : commit public `2d31efbd2230c28dfd23ad199ffab231c7a12b12`, 203 fichiers, arbre GitHub identique à l'export audité. Dix tests Rust passent aussi après compilation dans le checkout public. Historique local privé non poussé.

## 2026-10-02 — matin — E43/E44

- Objectif : vérifier le fonctionnement prolongé, puis profiter du retour de l’utilisateur pour diagnostiquer le lecteur.
- Action : interfaces Linux standards ; observation douze secondes du lanceur ; CD musical inséré par l’utilisateur, lecture TOC et quatre secteurs audio.
- Observation : obsidian4 actif après neuf heures, aucun service en échec ; aucune écriture observée du lanceur pendant la fenêtre. Le CD présente 20 pistes ; trois positions audio lisibles, relecture de la première identique.
- Résultat : première preuve de lecture effective du lecteur, limitée au CD et aux secteurs échantillonnés. Métadonnées et empreintes conservées, pas le contenu audio.
- Interprétation : la piste initiale de réécritures inutiles du lanceur vient du code, mais n’est pas confirmée sur le processus vivant ; ne pas revendiquer un gain. La panne DVD n’est ni identifiée ni réparée.
- Suite : comparaison avec DVD demandée ; diagnostic du lanceur et mesures avant tout changement. Pas de redémarrage ni commande firmware.

## 2026-10-02 — 07:30–07:37 UTC Mac — E45/E46

- Objectif : comparer CD/DVD et rétablir le bureau figé.
- Action : disque Just Cause 2 inséré par l’utilisateur ; lecture et statut SCSI standards. Diagnostic graphique et relances ciblées, sans redémarrage Linux.
- Observation : le lecteur renvoie « medium not present » pour le jeu. L’utilisateur corrige son premier retour : redimensionnement la veille suivi d’un gel. L’arrêt forcé du gestionnaire, contrairement à celui du lanceur et au SIGHUP, rétablit les requêtes X11.
- Résultat : OpaqueMove/Resize activés avec sauvegarde des préférences ; manette rouverte par le lanceur. Cinq tests synthétiques de sense passent.
- Interprétation : mécanisme XGrabServer cohérent avec le code et les symptômes ; pas encore reproduction contrôlée ni confirmation manuelle du correctif. Différence CD/DVD réelle, pièce fautive encore inconnue.
- Suite : utilisateur invité à redimensionner de nouveau ; besoin d’un DVD vidéo connu fonctionnel pour distinguer panne DVD et disque particulier.

Publication E43–E46 vérifiée à 2026-10-02T07:41:15.538940+00:00 : commit public `ec431c9c7e114e11074628d0fb95358d1128a752`, 221 fichiers, arbre distant identique ; preuve `public-audit/optical-publication.json`. Validation manuelle du redimensionnement encore attendue.

## 2026-10-02 — 07:42–07:49 UTC — E47

- Objectif : dépasser l’hypothèse de blocage au redimensionnement en reproduisant le mécanisme indépendamment du matériel Xbox.
- Action : service Docker initialement arrêté, redémarré après vérification de son état ; source IceWM 4.0.0 figée et contrôlée, compilation aarch64, deux serveurs Xvfb privés sans réseau ni socket graphique hôte.
- Observation : l’ancien mode empêche la fin d’une requête XTest et la réponse d’un autre client. Le nouveau mode redimensionne réellement et les deux clients répondent. Le premier test, qui manquait le bord du thème, n’avait rien redimensionné et est conservé comme échec.
- Résultat : test automatisé discriminant réussi ; aucune interaction Xbox pendant cette expérience.
- Interprétation : preuve du mécanisme X11 et de la correction de configuration dans cet environnement. Pas une preuve de toutes les fonctions de la manette, du pilote graphique ou de la stabilité prolongée sur Xbox.
- Suite : confirmation manuelle sur Xbox ; garder les avertissements de compilation de l’applet réseau amont comme piste distincte, sans les attribuer au gel.

## 2026-10-02 — piste utilisateur PAL/NTSC

- Observation rapportée : Just Cause 2 et les autres boîtes de jeux portent PAL.
- Action : vérifier la documentation Microsoft archivée sur les régions et la signification T10 du code 3a/00 ; demander si ces jeux fonctionnaient auparavant sur cette console.
- Interprétation : région non vérifiée, marquage des boîtes insuffisant ; erreur mesurée de support absent différente d’un refus explicite de région. Aucune commande matérielle ni modification de région exécutée.

Retour utilisateur : achat simultané de la console et des jeux en magasin d’occasion ; fonctionnement antérieur de cet ensemble inconnu. Compatibilité régionale toujours non confirmée ; disponibilité d’un DVD vidéo demandée.

Publication E47 et piste PAL vérifiée à 2026-10-02T07:57:41.408927+00:00 : commit public `a67d28f83a160fde6048efc74a9824c808745f74`, 230 fichiers, arbre GitHub identique ; preuve `evidence/2026-10-02/public-audit/resize-publication.json`.

## 2026-10-02 — 07:58 UTC Mac — E48

- Objectif : distinguer une restriction propre au jeu Xbox d’un refus plus général de DVD.
- Action : l’utilisateur insère Big Order ; deux TEST UNIT READY standards, intervalle observé 59.2 s, aucun changement de firmware/région.
- Observation : 02/3a/00 à chaque fois ; l’observation n’est donc pas limitée à l’instant de l’insertion. Aucun secteur vidéo lu.
- Résultat : deuxième DVD non reconnu, de catégorie différente du jeu.
- Interprétation : piste de reconnaissance DVD renforcée ; panne laser non prouvée, état du disque et bruits encore à confirmer.
- Suite : retour sur rotation/clics demandé ; comparaison sous système d’origine avant toute ouverture du lecteur.

Retour utilisateur E48 : le DVD tourne brièvement puis s’arrête, comme Just Cause 2. Contrôle sous le tableau de bord Xbox d’origine demandé, avec arrêt propre depuis Linux et sans relancer le jeu de démarrage. Le résultat reste en attente.

Publication E48 vérifiée à 2026-10-02T08:03:48.586991+00:00 : commit public `b4b49e2b2fdcc42f522fbc6cd4b74b1b96202632`, 234 fichiers et arbre distant conforme ; preuve `evidence/2026-10-02/public-audit/video-publication.json`. Résultat du contrôle sous tableau de bord stock encore attendu.


## 2026-10-02 — E49/E50 — arrêt et comparaison sous le système d’origine

- Objectif : comparer le comportement de Big Order hors Linux.
- Observation utilisateur : le bouton d’arrêt du bureau affiche « failed request ». Mesure administrative préalable : CanPowerOff = challenge, aucun inhibiteur.
- Action : arrêt normal demandé par un timer administrateur, accepté à 08:05:45 UTC ; aucune extinction forcée ni modification de permission. Extinction physique non observée directement.
- Résultat rapporté ensuite : aucun DVD détecté lors du contrôle stock demandé. Libellé exact non fourni ; pas de capture ni de confirmation de lisibilité du média ailleurs.
- Interprétation : une cause exclusivement Linux est moins probable ; panne matérielle précise non démontrée. Le défaut du bouton Éteindre reste à corriger après vérification du contexte de session normal.
- Suite : retour Linux par Rock Band Blitz, choix obsidian4 et Ethernet uniquement après arrivée au bureau. Pas de nouvelle connexion lancée pendant la manipulation utilisateur.


## 2026-10-02 — E51/E52 — audio hors matériel et retour Linux

- Objectif : avancer sur le son pendant la manipulation DVD, puis vérifier le retour de la console.
- Action hors console : nouvelle sortie de build, audio original en module ; reproduction des calculs par extraction du C réel, hooks pour cache/MMIO et ASan/UBSan.
- Observation : API disparues confirmées par compilation ; 98 tailles produisent un tableau sortant du tampon selon l’encodage du pilote, cinq cas de boucle de cache dépassent le nombre de lignes attendu. Le fractionnement de trames constitue une propriété distincte, pas une panne matérielle prouvée.
- Résultat : correctif 0008 partiel, 512 tailles acceptées sans géométrie hors tampon sur 16 369 examinées ; portage complet et son toujours non validés.
- Mesure matérielle : à 08:17:42 UTC obsidian4 répond après 201,58 s, zéro unité en échec, XRandR répond en 720p. Préférences contre le gel conservées.
- Correction du diagnostic d’arrêt : CanPowerOff depuis runuser dans SSH renvoie encore challenge, mais pkcheck sur le vrai PID 429 du lanceur local autorise power-off et power-off-multiple-sessions. La règle étroite existait déjà. Le contexte du lanceur relancé depuis SSH est une explication cohérente de l’ancien refus, pas une reproduction complète.
- Suite : utilisateur parti temporairement, travail autonome demandé ; aucun redémarrage volontaire ni test effectif du bouton. Poursuivre le portage audio hors matériel et valider l’arrêt lors d’un créneau physique.

Publication E49–E52 vérifiée à 2026-10-02T08:25:04.519035+00:00 : commit public `fd75dd4f20e7d0c0d0fc1475b1423d013d7cfa00`, 248 fichiers, parent et arbre GitHub conformes après audits. Preuve `evidence/2026-10-02/public-audit/audio-publication.json`. Audio non activé ; aucun arrêt depuis le retour Linux.


## 2026-10-02 — E53 — cycle de vie audio et divergence de protocole

- Objectif : corriger les ressources du pilote avant activation.
- Action : propriétaire unique ALSA, nettoyage des acquisitions partielles, arrêt avant destruction des PCM, API DMA/timer modernes, transport SMC partagé. Banc de fonctions C extraites sous ASan/UBSan, hors matériel.
- Observation : douze échecs attendus dans treize scénarios de l’original ; seize scénarios du candidat passent. Le premier essai du banc ne compilait pas, corrigé et conservé comme échec d’outillage. Régression des tampons inchangée.
- Résultat : objet PPC compilé sans avertissement ; compilation noyau/modules lancée séparément avec source figée. Aucun fichier installé sur Xbox.
- Analyse du code : LibXenon mentionne les premiers 32 Mio et encode les longueurs différemment ; HDMI y exige une initialisation absente du pilote Linux. Masque 29 bits et encodage historique non validés sur le matériel. ALSA fournit déjà de la mémoire DMA cohérente, à utiliser directement pour les PCM.
- Suite : achever et vérifier la compilation complète ; poursuivre contrat DMA, callbacks/timer et protocole. Aucun redémarrage pendant l’absence utilisateur.


## 2026-10-02 — E54 — envoi SMC borné et liaison audio

- Objectif : éviter les attentes sans borne sur la nouvelle voie audio et confirmer la liaison des modules.
- Action : nouvelle API processus avec deux trylocks, budget atomique de polling, message aligné et absence d’écriture en cas d’échec ; protection probe/remove spécifique à cette voie. Les anciens expéditeurs ne sont pas migrés.
- Observation : dix-neuf scénarios du C réel et des macros iopoll réelles passent ; régression audio étendue à dix-huit scénarios. Premier échec d’outillage sur paramètre inutilisé conservé.
- Résultat : première compilation complète audio-lifecycle terminée code 0 ; copie indépendante puis compilation audio-post code 0. Soixante-dix modules chacune, aucun avertissement, formats PowerPC et vermagic vérifiés, nouvel export GPL présent.
- Limites : budget logique, pas borne de transaction MMIO ; tests séquentiels sans validation SMP. Le mutex ne protège pas les anciennes voies. Aucun envoi réel, noyau/image ni module installé.
- Suite : publication après audit ; contrat DMA PCM, timer/notifications et protocole avant activation.

Publication E53/E54 vérifiée à 2026-10-02T08:57:54.026744+00:00 : commit public `5dd3293b9936669ba7a8e25935de8dd6b918fafc`, 273 fichiers, parent et arbre GitHub conformes après audits. Preuve `evidence/2026-10-02/public-audit/smc-publication.json`. Deux builds audio complets validés, aucun installé.


## 2026-10-02T09:43:49.512960+00:00 — E55/E56 — mémoire PCM et contrôle vivant

- Objectif : retirer le remappage CPU erroné des tampons DMA et clarifier leur propriétaire.
- Action : correctif 0011 après 0008–0010, contraintes ALSA, tampons gérés, barrières, arrêt du canal avant libération et validation des bornes. Aucun chargement.
- Observation : 20 scénarios ressources et 12 callbacks passent sous ASan/UBSan ; 16 369 tailles examinées, 512 acceptées sans dépassement. Suppression de la fonction privée de cache, pas test matériel de cohérence.
- Résultat : noyau audio-pcm et 70 modules compilés sans avertissement, ELF/vermagic et reconstruction des patches vérifiés. Outil de contrôle étendu au mode sans image XeLL ; voie complète obsidian4 encore valide.
- Mesure directe distincte : à 2026-10-02T09:40:09.815799+00:00, SSH répond sous obsidian4, uptime 5 139,44 s, zéro unité en échec, framebuffer 720p. Réactivité visuelle non vérifiée.
- Retour utilisateur : de nouveau disponible ; aucune action physique nécessaire pour ce travail.
- Limites : aucun son, aucune validation DMA réelle ; ancien timer non armé, synchronisation des callbacks et protocole à résoudre. Prochaine étape : notifications de progression et durée de vie des flux, hors matériel.

Publication E55/E56 vérifiée à 2026-10-02T09:45:58.581719+00:00 : commit public `74ba6693755aaef77e96d016bbcbc6e7cf473713`, 287 fichiers, parent et arbre GitHub conformes après audits. Preuve : `evidence/2026-10-02/public-audit/pcm-publication.json`. Candidat audio-pcm non installé.


## 2026-10-02T10:04:39.273970+00:00 — E57 — suivi audio par sortie

- Objectif : lancer et synchroniser correctement le suivi de lecture.
- Observation : START n’arme pas le timer ; deux appels directs du vieux callback avec position identique produisent deux fausses notifications. Reproduction hors matériel, pas un relevé vivant.
- Action : hrtimer par sortie, progression modulo et reste de période, XRUN si observation trop tardive, notification hors verrou du pilote, sync_stop/hw_free attendent le callback.
- Résultat hôte : 15 scénarios timer, 20 ressources, 15 PCM passent sous ASan/UBSan ; cas pthread avec notification retenue pendant la fermeture. Géométrie : 512 tailles acceptées sur 16 369, sans dépassement parmi elles.
- Échecs conservés : deux comparaisons signées au premier banc ; option --output incorrecte pour le banc de géométrie. Corrigés, recettes mises à jour.
- Configuration : ancien noyau sans HIGH_RES_TIMERS, incompatible avec la cadence nominale pour les plus petits tampons. Activation dans la copie candidate et refus de open si haute résolution inactive. Deux builds intermédiaires réussis ; build final démarré à 2026-10-02T09:59:37Z, encore vivant au relevé.
- Limites : modèle temporel et un entrelacement déterministe ; aucune validation SMP/latence/DMA. Ni installation ni nouvelle interaction Xbox. Prochain axe : publication des échantillons via ack puis protocole matériel.


## 2026-10-02T10:16:13.670215+00:00 — fin E57 et audit E58

- Résultat E57 : build haute résolution terminé code 0 ; 70 modules, ELF/vermagic et empreintes vérifiés, aucun avertissement. Le processus existant a été suivi jusqu’à sa fin, sans relance. Aucun déploiement.
- Objectif E58 : comprendre la publication audio avant migration vers ack.
- Observation hôte : trois requêtes identiques alternent la file sur 96 cas. Les helpers ALSA réels reproduisent un dépassement signé pour une valeur synthétique native 64 bits ; atteignabilité par les applications 32 bits actuelles non démontrée. Publication d’un bloc partiellement engagé interprétée sous l’hypothèse dernier-descripteur-valide.
- Analyse : ack doit préserver rollback, retour de boundary, tampon complet, écritures partielles, drain et reset. Déplacer simplement les écritures ne suffirait pas.
- Référence examinée : xenon-emu/xenon au commit 0284bbe6c8125935d97bf54ab3132089c6c65c8b ; classe audio sans consommation de descripteurs, donc pas de validation du protocole.
- Suite : documenter et publier après audit ; concevoir soumission/fins de flux, sans activer les noyaux audio encore incomplets. Dernier relevé matériel inchangé : E56.
