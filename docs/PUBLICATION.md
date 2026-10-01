# Publication contrôlée

L'utilisateur autorise une publication GitHub publique dans l'objectif v2. Le dépôt de recherche local et son historique restent conservés : ils contiennent des traces et métadonnées personnelles qui ne doivent pas être poussées telles quelles.

L'export initial est préparé dans un répertoire ignoré distinct avec `tools/export-public.py`. Il prend uniquement les fichiers texte suivis, exclut les acquisitions binaires, les archives d'installation, la sonde bloquante, les anciennes transcriptions de session et certains extraits tiers dont la licence reste à contrôler. Une politique locale fournit les remplacements des noms, chemins et coordonnées privées. Elle n'est jamais exportée. Le manifeste public donne les fichiers exclus, les empreintes avant/après et les transformations signalées, sans publier les valeurs retirées.

Les sommes des preuves publiques sont recalculées pour les dérivés publiés ; elles ne remplacent pas les empreintes des originaux locaux. Un document qui cite une preuve exclue signale une expérience locale, pas un fichier téléchargeable depuis GitHub. L'export conserve ces références historiques pour ne pas falsifier le périmètre du travail.

Avant le premier commit public : inspecter la sélection, scanner les secrets et informations personnelles, vérifier qu'aucun binaire propriétaire/dump n'est inclus, puis créer un historique neuf avec une identité de projet. Avant chaque push suivant : refaire l'audit des fichiers et de tous les objets atteignables ajoutés. Ne jamais pousser la branche locale `research/bootstrap`, ni utiliser `--mirror`, ni envoyer les anciens tags.

Le scanner intégré détecte plusieurs motifs évidents et la politique locale ; il ne remplace pas la revue humaine/agent des fichiers choisis. Les fichiers exclus restent conservés localement pour poursuivre la recherche. Aucune publication d'image NAND, jeu, clé ou firmware n'est nécessaire pour expliquer les résultats.
