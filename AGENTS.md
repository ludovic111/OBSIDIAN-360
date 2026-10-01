# OBSIDIAN-360 — instructions de travail

- Lire `docs/STATE.md` puis `docs/EXPERIMENTS.md` avant toute interaction matérielle.
- Communiquer en français et distinguer mesure directe, analyse du code, hypothèse et résultat non vérifié.
- Vérifier l’état vivant de la console avant de transformer une ancienne observation en affirmation actuelle.
- La lecture mmap de la fenêtre flash `0000:01:08.0/resource1` a figé la console. Ne pas relancer la sonde archivée ni une variante sans avoir expliqué et résolu la cause technique ; privilégier l’acquisition XeLL documentée ou un lecteur matériel.
- Les scripts d’installation archivés effacent des disques. Ils documentent du travail déjà effectué et ne sont pas des étapes à rejouer.
- Aucun effacement/flashage NAND pour « essayer » : il manque une chaîne de démarrage indépendante validée et une sauvegarde brute restaurable adaptée au matériel.
- Ne pas toucher aux eFuses, à la protection thermique, ni aux réglages d’alimentation dans une collecte d’inventaire.
- Garder clés SSH, CPU/DVD keys, keyvaults, dumps firmware et adresses privées de travail hors Git ; `.local/` et `private/` sont ignorés.
- Lancer Linux par Rock Band Blitz avec Ethernet débranché ; le rebrancher seulement après arrivée sous Linux. Le firmware stock et les patchs temporaires sont encore nécessaires.
- L’accès utilise `en0` sur ce Mac ; les routes Tailscale non liées à l’interface ont donné des résultats trompeurs auparavant.
- Préférer les lectures ciblées et les pilotes existants. Un accès MMIO en lecture seule peut quand même bloquer le matériel.
- Après chaque expérience, mettre à jour STATE et EXPERIMENTS avec les preuves et limitations. Ne jamais annoncer « rétro-ingénierie complète » pour un inventaire ou une synthèse documentaire.
- Publication GitHub explicitement autorisée par le nouvel objectif. Avant chaque commit public/push, auditer contenu et historique ; ne jamais pousser directement la branche de recherche locale contenant des traces privées. Publier uniquement depuis l'export public contrôlé décrit dans docs/PUBLICATION.md.
- Pendant l'absence nocturne de l'utilisateur : pas de redémarrage volontaire ni opération irréversible ; noter les actions physiques dans docs/BLOCKED.md et poursuivre un axe indépendant.
