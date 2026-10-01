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
