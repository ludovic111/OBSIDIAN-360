# Interruptions de session et reprise

Diagnostic du 1 octobre 2026, basé sur les événements structurés du transcript local, consulté en lecture seule. Les journaux complets restent hors Git.

Les fins de tours à 20:33:16, 20:34:10, 20:35:20, 20:55:01 et 20:55:34 UTC comportent `last_agent_message: null` et `error.codex_error_info: cyber_policy`. Leur message signale un risque cybersécurité possible. Ce contrôle de plateforme explique ces interruptions précises ; les précédentes incompatibilités des outils de compilation sont des incidents distincts. Les avoir corrigées ne répare pas ce contrôle et ne garantit pas l'absence de nouvelles interruptions.

Le contrôle ne peut pas être désactivé depuis le dépôt. Ne pas reformuler ou segmenter des opérations pour le contourner. Les travaux permis de documentation, vérification et correction de pilotes restent évalués selon leur contenu réel. Le diagnostic ne démontre pas quelle opération particulière a déclenché chaque signalement.

Lors de la reprise, `get_goal` indiquait `active`. Le processus de compilation déjà lancé et son conteneur étaient encore vivants : aucune deuxième compilation n'a été lancée. Le processus a ensuite terminé normalement à 21:00:03 UTC avec un code 0. Le noyau produit et son format ELF PowerPC64 big-endian ont été vérifiés.

Pour reprendre une compilation :

1. Lire `.local/kernel-build/build-state.json` pour retrouver le journal et le conteneur.
2. Vérifier le processus ou le conteneur réellement vivant. Le fichier d'état seul n'est pas une preuve.
3. Reprendre l'observation du même processus s'il tourne. Une expiration de l'observation ne signifie pas qu'il a échoué.
4. Après fin confirmée, lire le code de retour et le journal ; vérifier l'artefact avant de déclarer un succès.

`tools/build-kernel.py` conserve chaque tentative et refuse de démarrer si un conteneur de compilation existe déjà. Ce mécanisme protège la reprise du build ; il ne modifie pas Codex et ne relance pas automatiquement des tours interrompus.

Référence consultée pour localiser les journaux : [documentation officielle de dépannage](https://learn.chatgpt.com/docs/reference/troubleshooting), section « Feedback and logs ». Aucun signalement ni journal envoyé à un tiers.
