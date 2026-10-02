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
