# Objectif demandé et critères de preuve

## Objectif courant

La dernière version fournie par l'utilisateur remplace les précédentes : [OBJECTIVE-USER-2026-10-01-v2.md](OBJECTIVE-USER-2026-10-01-v2.md), SHA-256 `3c5431252bc8c736c755523e760e855c451043434ca6172a29959f13ca45c9d5`. La première version détaillée est conservée dans [OBJECTIVE-USER-2026-10-01.md](OBJECTIVE-USER-2026-10-01.md). L'objectif exige une recherche aussi approfondie que réalistement accessible, des outils reproductibles, une modernisation justifiée et la préservation de la récupération. Il ajoute l'étude du cycle complet des jeux légitimes, le travail autonome pendant l'absence de l'utilisateur, un journal chronologique et la publication publique sur GitHub après contrôle des données et de l'historique.

Les quatorze axes du texte source font foi, notamment les formats exécutables, assets, API et instructions PowerPC des jeux, les remplacements logiciels et les mesures avant/après. Aucun binaire/asset propriétaire ni secret ne sera publié. L'autorisation explicite de publication remplace la restriction antérieure sur les publications implicites ; elle ne permet pas de pousser l'historique local sans examen. Les tâches exigeant une action physique vont dans [BLOCKED.md](BLOCKED.md) ; poursuivre entre-temps les axes indépendants.

L'organisation actuelle est conservée pour ne pas casser les références aux preuves. Ajouter un répertoire lorsqu'il contient un travail réel, plutôt que créer toutes les catégories proposées à vide. L'état de chaque axe reste fondé sur les preuves ci-dessous ; les inconnues architecturales sont détaillées dans [RESEARCH-MAP.md](RESEARCH-MAP.md).

## Historique de la demande

Objectif étendu par l'utilisateur le 1 octobre 2026 : comprendre et documenter la console, obtenir un démarrage direct sous Linux avec bureau, optimiser l'utilisation du matériel en évaluant notamment Rust, diagnostiquer et si possible réparer la lecture des disques, puis permettre l'utilisation de jeux Xbox 360 sur disque. L'utilisateur autorise des modifications logicielles importantes ; les sauvegardes, le chemin fonctionnel et les limites matérielles doivent rester explicites.

L'utilisateur étend ensuite explicitement cette autorisation à une réécriture éventuelle de tout le firmware, dans le langage choisi. Cette latitude permet d'étudier des remplacements complets ; leur correction, leurs performances, leur compatibilité et leur récupération restent à démontrer. Le choix d'un langage ou le volume réécrit ne constitue pas une preuve de résultat.

## Résultats à établir

| Demande | Preuve nécessaire | État au dernier point documenté |
|---|---|---|
| Démarrage direct Linux | Mise sous tension à froid atteignant Linux et son bureau sans lancement manuel d'un jeu, puis plusieurs redémarrages concordants | Non établi ; chaîne actuelle dépend du système Xbox, de Rock Band Blitz et de XeLL |
| Bureau utilisable | Affichage, saisie, pointeur/manette et démarrage de session vérifiés réellement | Bureau obsidian4 confirmé par utilisateur et SSH ; commandes physiques à revalider, 1080p absent |
| Optimisation du matériel | Mesures comparables avant/après, charge contrôlée, stabilité et ressources suivies | Pas de campagne de performances complète ; correctifs de fiabilité préparés |
| Évaluer Rust | Choisir un composant mesurable et compatible PowerPC, comparer correction, mémoire et performances | Aucun portage Rust commencé ; une réécriture n'est pas en soi une optimisation |
| Réparer le lecteur | Identifier la panne, réaliser la réparation appropriée, lire plusieurs supports connus fonctionnels | DG-16D2S identifié ; utilisateur : tiroir fonctionnel, aucun disque lu ; mécanique/optique non diagnostiquée |
| Jouer aux disques Xbox 360 | Lecture du support puis lancement et fonctionnement réel d'un jeu avec commandes/audio/vidéo | Non vérifié ; préserver le système d'origine pendant la recherche d'une solution Linux |
| Compréhension et documentation complètes | Pour chaque bloc : interfaces, code identifié, mesures, limites, hypothèses, reproductions et références | Inventaire et audits partiels ; de nombreux blocs et protocoles restent inconnus |
| Remplacement éventuel du firmware | Format et dépendances identifiés, reconstruction vérifiée, démarrage/récupération validés sur l'exemplaire et fonctions testées | Pas de firmware de remplacement construit ni de sauvegarde NAND restaurable validée |

La demande « à l'atome près » exprime une ambition d'exhaustivité. L'accès logiciel n'observe pas la structure atomique, le détail de chaque transistor ou les caractéristiques électriques internes. Ces points restent hors des résultats démontrés et demanderaient des moyens de laboratoire distincts. Ne pas présenter une compilation, un inventaire ou une documentation publique comme une connaissance complète du matériel.

## Méthode de travail

Conserver les faits datés, les sources exactes, les empreintes et les échecs instructifs. Les modifications candidatures sont versionnées séparément du système fonctionnel. Le bureau, le démarrage, la lecture de disque et l'exécution des jeux sont des fonctions à valider chacune. Une correction de pilote n'autorise pas à conclure sur les autres.

Pour les performances : commencer par une référence CPU/mémoire, consommation mémoire du bureau, coût de copie du framebuffer, débits de stockage/réseau et stabilité. Privilégier les gains mesurés et la compatibilité de la cible ; ne pas modifier alimentation, protections thermiques ou eFuses pour obtenir un score.

Pour la chaîne de démarrage : conserver le firmware stock tant qu'il fournit le seul chemin validé. Il manque toujours une sauvegarde NAND restaurable et une chaîne autonome testée ; aucune écriture spéculative de flash n'est une étape de validation.
