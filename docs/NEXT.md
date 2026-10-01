# Prochaines étapes

Priorités issues de l'analyse approfondie :

- obsidian4 est désormais confirmé en SSH avec bureau actif et framebuffer corrigé. Priorité : stabilité sous charge mesurée et validation des commandes physiques ; répéter ensuite les démarrages avec sélection explicite. Conserver linux_hdd et la récupération ; la cause de l'écran bloqué précédent reste inconnue.
- Lecteur : identifier la cause du refus de page de capacités et des disques non lus, puis confronter les erreurs à un support connu fonctionnel et aux observations physiques. Pas de diagnostic de laser à partir de `Can read DVD: 0`.
- Établir une référence de performances avant optimisation ; évaluer Rust pour un composant précis au regard de la cible PowerPC. Le périmètre étendu et les critères sont dans `docs/OBJECTIVE.md`.
- Poursuivre la revue SMC : sérialisation des transactions, propagation des interruptions/délais et contrat du gestionnaire IRQ. Ne pas déclencher de commandes inconnues sur le matériel pour reproduire le défaut de cache.
- Évaluer la correction du masque IPI dans cette branche, avec compilation puis test ciblé du chemin concerné ; ne pas attribuer au callback dormant les symptômes du chemin SMP ordinaire.
- Pour une acquisition par XeLL, identifier le binaire réellement utilisé et vérifier/corriger le tampon de page physique HTTP ainsi que les erreurs SFCX. Ne pas assimiler une réponse HTTP complète à une sauvegarde NAND validée.
- Résoudre l'observation de trousseau pacman manquant avant toute nouvelle installation de paquets ; conserver les signatures activées.
- Porter le pilote audio vers les API 6.18 et revoir DMA, SMC et interruptions avant son activation.

État des étapes historiques :

1. Fait : session récupérée, disque et bureau vérifiés ; erreur de module pkcs8 consignée.
2. Fait : acquisitions SMC/ANA/GPU rapatriées et contrôlées par SHA-256, sans refaire la sonde NAND.
3. Manette désormais détectée et événements reçus ; confirmer l’utilisation effective du pointeur, A et Y.
4. Identifier visuellement la carte mère et le type/capacité NAND.
5. Préparer l’acquisition NAND par XeLL ou un lecteur matériel, avec lectures concordantes et vérification ECC. Conserver clés propres à la console et dumps hors Git.
6. Analyser les versions et fonctions des bootloaders de cet exemplaire. Cela ne constitue pas en soi un contournement de leurs signatures.
7. Pour le 1080p : obtenir des états vidéo comparables, comprendre horloges et timings, puis tester un chargeur expérimental sur USB avec une récupération préservée.
8. Étudier séparément support audio, watchdog Ethernet et comportement USB. Ne pas transformer des symptômes isolés en diagnostics matériels définitifs.
9. Le démarrage indépendant exige une méthode compatible et validée ; ne pas effacer le système Xbox tant que le démarrage actuel en dépend.

Une rétro-ingénierie intégrale comprend aussi des mesures électriques, des protocoles et du silicium non accessibles via SSH. Ce dépôt sert à accumuler des preuves, sans revendiquer ces travaux comme achevés.
