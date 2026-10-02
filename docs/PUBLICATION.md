# Publication contrôlée

## Publication vérifiée

Mise à jour du 2 octobre : commit public `2d31efbd2230c28dfd23ad199ffab231c7a12b12`, enfant direct de f9da49e, 203 fichiers. Inspecteur XEX2, tests et outil d'audit de l'historique inclus ; vérification API du commit et de l'arbre réussie. L'audit avant push a couvert les deux commits et 213 objets texte atteignables. Voir `evidence/2026-10-02/public-audit/publication.json`.

Le dépôt public [ludovic111/OBSIDIAN-360](https://github.com/ludovic111/OBSIDIAN-360) est créé. Premier commit : `f9da49e7cc39a3bf06983e97b9fffe73a8e63606`, sans parent, 187 fichiers. L'API GitHub confirme visibilité publique, branche main, SHA du commit et égalité de l'arbre distant avec l'export audité. Preuve : `evidence/2026-10-01/publication/verification.json`.

Deux relevés ont été dérivés pour masquer l'adresse MAC. Dix-sept chemins ont été exclus de la sélection initiale, dont le manifeste SHA original (remplacé par celui des dérivés), les acquisitions binaires, les archives et les extraits tiers retenus localement. Les attributions publiques amont restent conservées ; aucune identité Git privée de l'opérateur n'est dans le nouvel historique.

Le checkout de publication local est `.local/public-export-reviewed-20261001`, avec son propre Git et son remote origin. Le dépôt de recherche principal n'a pas de remote : ne pas en déduire que les modifications locales suivantes sont automatiquement publiées. Repréparer et auditer un export pour chaque mise à jour, sans mélanger les deux historiques.

L'utilisateur autorise une publication GitHub publique dans l'objectif v2. Le dépôt de recherche local et son historique restent conservés : ils contiennent des traces et métadonnées personnelles qui ne doivent pas être poussées telles quelles.

L'export initial est préparé dans un répertoire ignoré distinct avec `tools/export-public.py`. Il prend uniquement les fichiers texte suivis, exclut les acquisitions binaires, les archives d'installation, la sonde bloquante, les anciennes transcriptions de session et certains extraits tiers dont la licence reste à contrôler. Une politique locale fournit les remplacements des noms, chemins et coordonnées privées. Elle n'est jamais exportée. Le manifeste public donne les fichiers exclus, les empreintes avant/après et les transformations signalées, sans publier les valeurs retirées.

Les sommes des preuves publiques sont recalculées pour les dérivés publiés ; elles ne remplacent pas les empreintes des originaux locaux. Un document qui cite une preuve exclue signale une expérience locale, pas un fichier téléchargeable depuis GitHub. L'export conserve ces références historiques pour ne pas falsifier le périmètre du travail.

Avant le premier commit public : inspecter la sélection, scanner les secrets et informations personnelles, vérifier qu'aucun binaire propriétaire/dump n'est inclus, puis créer un historique neuf avec une identité de projet. Avant chaque push suivant : refaire l'audit des fichiers et de tous les objets atteignables ajoutés. Ne jamais pousser la branche locale `research/bootstrap`, ni utiliser `--mirror`, ni envoyer les anciens tags.

Le scanner intégré détecte plusieurs motifs évidents et la politique locale ; il ne remplace pas la revue humaine/agent des fichiers choisis. Les fichiers exclus restent conservés localement pour poursuivre la recherche. Aucune publication d'image NAND, jeu, clé ou firmware n'est nécessaire pour expliquer les résultats.

Pour chaque mise à jour, `tools/audit-public.py --repo CHEMIN_EXPORT_GIT --policy CHEMIN_POLITIQUE_LOCALE` contrôle la sélection suivie/non ignorée, les empreintes du manifeste et des preuves, puis les blobs, commits et tags atteignables de cet historique public. L'exécuter avant le commit public et après le commit avant le push. Un nouveau répertoire d'export préparé est synchronisé seulement après contrôle du checkout public et de son parent distant. Le programme d'audit ne committe ni ne pousse.

Mise à jour E43–E46 : `ec431c9c7e114e11074628d0fb95358d1128a752`, 221 fichiers, troisième commit public. Audit avant commit puis avant push réussi (240 objets texte), vérification API de l’arbre et du parent réussie. Preuve `evidence/2026-10-02/public-audit/optical-publication.json`.

Publication E47 et piste PAL vérifiée à 2026-10-02T07:57:41.408927+00:00 : commit public `a67d28f83a160fde6048efc74a9824c808745f74`, 230 fichiers, arbre GitHub identique ; preuve `evidence/2026-10-02/public-audit/resize-publication.json`.

Publication E48 vérifiée à 2026-10-02T08:03:48.586991+00:00 : commit public `b4b49e2b2fdcc42f522fbc6cd4b74b1b96202632`, 234 fichiers et arbre distant conforme ; preuve `evidence/2026-10-02/public-audit/video-publication.json`. Résultat du contrôle sous tableau de bord stock encore attendu.

Publication E49–E52 vérifiée à 2026-10-02T08:25:04.519035+00:00 : commit public `fd75dd4f20e7d0c0d0fc1475b1423d013d7cfa00`, 248 fichiers, parent et arbre GitHub conformes après audits. Preuve `evidence/2026-10-02/public-audit/audio-publication.json`. Audio non activé ; aucun arrêt depuis le retour Linux.

Publication E53/E54 vérifiée à 2026-10-02T08:57:54.026744+00:00 : commit public `5dd3293b9936669ba7a8e25935de8dd6b918fafc`, 273 fichiers, parent et arbre GitHub conformes après audits. Preuve `evidence/2026-10-02/public-audit/smc-publication.json`. Deux builds audio complets validés, aucun installé.

Publication E55/E56 vérifiée à 2026-10-02T09:45:58.581719+00:00 : commit public `74ba6693755aaef77e96d016bbcbc6e7cf473713`, 287 fichiers, parent et arbre GitHub conformes après audits. Preuve : `evidence/2026-10-02/public-audit/pcm-publication.json`. Candidat audio-pcm non installé.

Publication E57/E58 vérifiée à 2026-10-02T10:19:25.216637+00:00 : commit public `987fea14abdeb6059b4b8d4a6b1215345cefabbe`, 312 fichiers, parent et arbre GitHub conformes après audits. Preuve : `evidence/2026-10-02/public-audit/poll-publication.json`. Noyau audio-poll compilé, non installé ; soumission encore à corriger.

Publication E59 vérifiée à 2026-10-02T10:36:04.104109+00:00 : commit public `3a98dcf5b0977a33251748255f186c25cfcf2da0`, 324 fichiers, parent et arbre GitHub conformes après audits. Preuve : `evidence/2026-10-02/public-audit/queue-publication.json`. File PCM testée et liée pour PowerPC, non intégrée au pilote et non chargée.
