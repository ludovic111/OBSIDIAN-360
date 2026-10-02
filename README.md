# OBSIDIAN-360

**Comprendre la machine. Documenter chaque preuve. Construire son avenir sous Linux.**

Laboratoire d’analyse d'une Xbox 360 : matériel, chaîne de démarrage, pilotes Linux, interface à la manette et expériences reproductibles.

## État vérifié

- ArchPOWER installé et démarré sur le disque interne de 120 Go ; swap de 2 Gio.
- Bureau IceWM personnalisé en 1280 × 720, clavier visuel et moteur de saisie testés.
- Douze fonctions PCI relevées ; GPU identifié par sa signature PCI comme famille Jasper ; six threads CPU visibles.
- obsidian4 a démarré après sélection manuelle dans XeLL : noyau confirmé en SSH, bureau actif, racine interne, zéro service en échec et allocation framebuffer corrigée vérifiée. La cause du blocage précédent reste inconnue.
- Le gel du bureau lors du redimensionnement à la manette est récupéré sans reboot Linux ; le mécanisme X11 est reproduit hors console et corrigé par configuration. Validation physique du redimensionnement encore attendue.
- Lecteur : secteurs de CD audio lus, mais jeu Just Cause 2 et DVD vidéo Big Order non reconnus sous Linux. Composant fautif et compatibilité régionale non déterminés.
- L'entrée obsidian4 reste optionnelle ; linux_hdd demeure le choix par défaut. Stabilité prolongée et redémarrages répétés encore à valider.
- Audio : tampons et suivi par sortie corrigés hors console, noyau candidat haute résolution et 70 modules compilés. Soumission des échantillons et protocole encore incomplets ; aucun son ni chargement du candidat.
- Ni 1080p, ni démarrage indépendant du système Xbox, ni rétro-ingénierie intégrale réalisés.

## Lire et continuer

1. [État courant](docs/STATE.md) et [prochaines étapes](docs/NEXT.md).
2. [Architecture et faits établis](docs/ARCHITECTURE.md).
3. [Incidents et expériences](docs/EXPERIMENTS.md).
4. [Construction et installation](docs/BUILD-AND-RECOVERY.md), [journal](docs/JOURNAL.md) et [actions physiques différées](docs/BLOCKED.md).
5. [Mesures structurées](evidence/2026-10-01/mesures.json), [contrôleurs PCI](evidence/2026-10-01/peripheriques-pci.csv) et [sources](docs/SOURCES.md).
6. [Analyse approfondie : deux défauts mémoire reproduits, vidéo, audio et NAND](docs/DEEP-AUDIT-2026-10-01.md), [correctifs candidats](research/patches/README.md) et [tests hors console](research/tests/README.md).
7. [Noyau réellement installé : désassemblage, DMA, PCI et défaut IPI](docs/BINARY-AUDIT-2026-10-01.md).
8. [Cache et protocole SMC ; premier noyau candidat compilé](docs/SMC-AUDIT-2026-10-01.md) et [diagnostic des interruptions de session](docs/SESSION-RECOVERY.md).
9. [Pilote LED et nettoyage des ressources](docs/LED-AUDIT-2026-10-01.md), [noyau candidat, modules et image vérifiés](docs/KERNEL-CANDIDATE-2026-10-01.md).
10. [Objectif étendu et critères de preuve](docs/OBJECTIVE.md), [préparation et essai obsidian4](docs/BOOT-PREFLIGHT-2026-10-01.md), [diagnostic initial du lecteur](docs/OPTICAL-DRIVE.md).
11. [Trace hors console des fonctions vidéo et limites du passage 1080p](docs/VIDEO-MODE-TRACE-2026-10-01.md).
12. [Première référence de performances](docs/PERFORMANCE-BASELINE-2026-10-01.md) et [carte des inconnues](docs/RESEARCH-MAP.md).
13. [Analyse structurelle XEX2](docs/XEX2-INSPECTION.md) et [inspecteur Rust](game-analysis/xex-inspect/README.md), validé sur échantillons synthétiques uniquement.

14. [Récupération du gel graphique](docs/DESKTOP-RESIZE-RECOVERY.md) et [test reproductible sous Xvfb](docs/DESKTOP-TESTING.md).

15. [Tampons audio ALSA](docs/AUDIO-PCM-DMA.md), [suivi et fermeture des flux](docs/AUDIO-STREAM-POLLING.md), [audit de la soumission](docs/AUDIO-SUBMISSION-AUDIT.md).

16. [File PCM originale et gestion de la fin de flux](research/audio/README.md), testée mais non intégrée au pilote.

## Organisation

- `evidence/` : relevés datés et sommes SHA-256 ; observations ponctuelles, pas état courant garanti.
- `desktop/` : lanceur Python à la manette et configuration vidéo fonctionnelle.
- `tools/` : accès SSH local, collecte d’inventaire et conversion des captures XWD.
- `research/archive/` : scripts historiques d’installation, conservés comme texte non exécutable.
- `research/blocked/` : sonde ayant gelé la console, pour analyse seulement.
- `.local/` : configuration d’accès ignorée par Git ; aucune clé privée versionnée.

## Accès local

```sh
./tools/ssh-xbox 'uptime'
python3 desktop/xbox_desktop.py --self-test
```

Le premier appel nécessite la configuration locale créée sur ce Mac et la clé existante hors dépôt. Il ne recherche pas d’autres machines et conserve la vérification de clé d’hôte. Le test Python ne simule pas une manette physique.

Chaque expérience doit préciser : objectif, état initial, action, preuve, résultat et récupération. Les instructions de travail sont dans [AGENTS.md](AGENTS.md).

L'export public exclut les données privées et les binaires non redistribuables ; certaines preuves restent locales. Lire [la procédure de publication](docs/PUBLICATION.md) et [les licences](THIRD_PARTY.md). La recherche est incomplète et aucun installateur universel n'est fourni.

Adaptateur audio E60 : [soumission ALSA, tests et limite du dernier bloc](docs/AUDIO-ALSA-ADAPTER.md). Candidat non installé ; aucune lecture sonore validée.
