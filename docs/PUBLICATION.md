# Publication contrôlée

## Publication vérifiée

Le dépôt public [ludovic111/OBSIDIAN-360](https://github.com/ludovic111/OBSIDIAN-360) est créé. Premier commit : `f9da49e7cc39a3bf06983e97b9fffe73a8e63606`, sans parent, 187 fichiers. L'API GitHub confirme visibilité publique, branche main, SHA du commit et égalité de l'arbre distant avec l'export audité. Preuve : `evidence/2026-10-01/publication/verification.json`.

Deux relevés ont été dérivés pour masquer l'adresse MAC. Dix-sept chemins ont été exclus de la sélection initiale, dont le manifeste SHA original (remplacé par celui des dérivés), les acquisitions binaires, les archives et les extraits tiers retenus localement. Les attributions publiques amont restent conservées ; aucune identité Git privée de l'opérateur n'est dans le nouvel historique.

Le checkout de publication local est `.local/public-export-reviewed-20261001`, avec son propre Git et son remote origin. Le dépôt de recherche principal n'a pas de remote : ne pas en déduire que les modifications locales suivantes sont automatiquement publiées. Repréparer et auditer un export pour chaque mise à jour, sans mélanger les deux historiques.

L'utilisateur autorise une publication GitHub publique dans l'objectif v2. Le dépôt de recherche local et son historique restent conservés : ils contiennent des traces et métadonnées personnelles qui ne doivent pas être poussées telles quelles.

L'export initial est préparé dans un répertoire ignoré distinct avec `tools/export-public.py`. Il prend uniquement les fichiers texte suivis, exclut les acquisitions binaires, les archives d'installation, la sonde bloquante, les anciennes transcriptions de session et certains extraits tiers dont la licence reste à contrôler. Une politique locale fournit les remplacements des noms, chemins et coordonnées privées. Elle n'est jamais exportée. Le manifeste public donne les fichiers exclus, les empreintes avant/après et les transformations signalées, sans publier les valeurs retirées.

Les sommes des preuves publiques sont recalculées pour les dérivés publiés ; elles ne remplacent pas les empreintes des originaux locaux. Un document qui cite une preuve exclue signale une expérience locale, pas un fichier téléchargeable depuis GitHub. L'export conserve ces références historiques pour ne pas falsifier le périmètre du travail.

Avant le premier commit public : inspecter la sélection, scanner les secrets et informations personnelles, vérifier qu'aucun binaire propriétaire/dump n'est inclus, puis créer un historique neuf avec une identité de projet. Avant chaque push suivant : refaire l'audit des fichiers et de tous les objets atteignables ajoutés. Ne jamais pousser la branche locale `research/bootstrap`, ni utiliser `--mirror`, ni envoyer les anciens tags.

Le scanner intégré détecte plusieurs motifs évidents et la politique locale ; il ne remplace pas la revue humaine/agent des fichiers choisis. Les fichiers exclus restent conservés localement pour poursuivre la recherche. Aucune publication d'image NAND, jeu, clé ou firmware n'est nécessaire pour expliquer les résultats.

Pour chaque mise à jour, `tools/audit-public.py --repo CHEMIN_EXPORT_GIT --policy CHEMIN_POLITIQUE_LOCALE` contrôle la sélection suivie/non ignorée, les empreintes du manifeste et des preuves, puis les blobs, commits et tags atteignables de cet historique public. L'exécuter avant le commit public et après le commit avant le push. Un nouveau répertoire d'export préparé est synchronisé seulement après contrôle du checkout public et de son parent distant. Le programme d'audit ne committe ni ne pousse.
