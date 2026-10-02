# Banc d'analyse hors console

`check-memory-bounds.py` utilise Python 3 et un Clang disposant d'AddressSanitizer. Les sources externes sont récupérées localement dans `.local/upstream/` et identifiées par `evidence/2026-10-01/deep-audit/sources.json`. Ne pas remplacer silencieusement les commits figés par les dernières branches.

Les copies `.local/analysis-source/xenos.c` et `snd-xenon.c` proviennent des fichiers nouvellement ajoutés dans `patch-6.18-xenon0.30.diff`. `prepare-research-sources.py` vérifie les commits et empreintes avant de les extraire. L'empreinte de `xenos.c` est également consignée dans les résultats des tests.

Exécution depuis la racine du dépôt :

```sh
python3 tools/prepare-research-sources.py

python3 research/tests/check-memory-bounds.py \
  --xenos .local/analysis-source/xenos.c \
  --xell .local/upstream/xell-reloaded/source/lv2/httpd/httpd_flash.c

python3 tools/analyze-video.py \
  --ana evidence/2026-10-01/ana-720p.bin \
  --gpu evidence/2026-10-01/gpu-display-registers.json \
  --tables .local/upstream/libxenon/libxenon/drivers/xenos/xenos_videomodesdata.h
```

Le premier programme vérifie quatre résolutions avec allocation initiale puis arrondie, et le gestionnaire HTTP XeLL avant/après correction du tampon. Il échoue si un dépassement attendu n'est pas détecté ou si un cas corrigé échoue. La compilation utilise `-O0` pour empêcher l'élimination des écritures graphiques dont le résultat n'est pas affiché. Les essais de dépassement ont lieu uniquement dans les processus locaux du banc.

Le second programme ne lit que des fichiers ; il ne programme aucun registre. Il vérifie la longueur de la capture et des tables, puis expose les différences sans assimiler la comparaison à une validation matérielle.

Collecte vivante, après lecture de STATE et EXPERIMENTS :

```sh
./tools/ssh-xbox 'python3 -' < tools/collect-runtime.py
```

Cette collecte utilise `/proc`, des attributs sysfs standards et des commandes d'état. Elle ne lit ni BAR PCI, ni `/dev/mem`, ni NAND, ni eFuses ; elle ne relève pas d'adresse IP ou de clé. Les sorties restent des instantanés et les erreurs sont conservées.

## Cache SMC et compilation

`check-smc-cache.py --original CHEMIN_SOURCE --candidate CHEMIN_CORRIGE` compile le tableau et la fonction de recherche réels dans un processus ASan local. Les identifiants connus et l'ensemble des 256 valeurs possibles sont testés dans les deux variantes. Aucun périphérique n'est ouvert. Les chemins et SHA-256 de l'expérience sont décrits dans `docs/SMC-AUDIT-2026-10-01.md` et `smc-audit/cache-bounds.json`.

`tools/build-kernel.py --source CHEMIN_SOURCE --output CHEMIN_BUILD --jobs 4` compile une arborescence déjà préparée, avec son `.config`, dans l'image locale LLVM 16. Il ne télécharge, n'installe et ne démarre rien sur la Xbox. Conserver le journal et suivre le processus existant avant toute reprise ; voir `docs/SESSION-RECOVERY.md`. Le succès de `vmlinux` ne vaut pas validation des modules, du chargeur ni du fonctionnement physique.

## Cycle de vie LED

```sh
python3 research/tests/check-led-lifecycle.py --source CHEMIN_LED_CORRIGE --output CHEMIN_RAPPORT.json
```

Le fichier C réel est compilé avec ASan/UBSan et des modèles de ressources/FIFO. Les 21 cas comprennent neuf échecs d'allocation, huit échecs d'enregistrement LED, les erreurs de création du pilote/périphérique, le report de probe et le succès avec retrait. Les en-têtes et le main du banc sont adjacents au script. Aucune vérification de concurrence physique ; voir `docs/LED-AUDIT-2026-10-01.md`.

`tools/check-kernel-artifacts.py` vérifie le format et la version des modules de `modules.order`, ainsi que six sections entre le noyau et son image. Le rapport est publié seulement si ces contrôles passent ; il ne prouve pas un démarrage.

## Traces vidéo

`tools/trace-video-modes.py` exécute les fonctions C f1/f2 réelles de libxenon sur le Mac sous ASan/UBSan et remplace les accès GPU par une trace bornée. Les tables standard/Corona sont parcourues, puis les valeurs finales sont comparées à une capture ancienne. L'attente LUT est simulée ; aucune validation d'horloge, d'ANA ou de sortie vidéo physique. Commande et limites dans `docs/VIDEO-MODE-TRACE-2026-10-01.md`.

## Publication et exécutables

`python3 research/tests/check-public-audit.py` utilise un Git temporaire avec données fictives. Il vérifie contenu non audité, empreinte modifiée, motif de jeton factice et persistance du motif dans un ancien commit après nettoyage du fichier courant. Il n'accède à aucune vraie clé.

Le parseur Rust et les neuf essais de sa CLI sont décrits dans `game-analysis/xex-inspect/README.md`. Les échantillons synthétiques sont construits pendant les tests ; aucun fichier XEX commercial n'est nécessaire.

## Audio : modèles de fonctions réelles

- `check-audio-buffers.py` : 16 369 tailles, descripteurs et ancienne boucle de cache. La boucle supprimée après 0011 représente zéro cas candidat, pas une validation du cache réel. Sortie JSON sur stdout.
- `check-audio-lifecycle.py` : treize scénarios originaux et vingt candidats après 0011/0012, bilan des ressources et injections d’erreurs.
- `check-smc-post.py` : dix-neuf scénarios SMC avec fonctions et macros iopoll extraites.
- `check-audio-pcm.py` : quinze scénarios après 0012 ; zones mémoire, contraintes, tailles, adresses, fermeture séquentielle et refus du timer basse résolution.
- `check-audio-poll.py` : un scénario précédent reproduit deux défauts ; quinze scénarios candidats vérifient progression, arrêt et un entrelacement pthread contrôlé pendant la libération.
- `check-audio-submission.py` : reproduit 96 cas de publication non idempotente, un débordement signé attendu dans les helpers ALSA et un cas de bloc partiel sous hypothèse de protocole. Il ne valide pas une correction.

Recettes et limites dans `docs/AUDIO-PCM-DMA.md`, `docs/AUDIO-STREAM-POLLING.md` et `docs/AUDIO-SUBMISSION-AUDIT.md`. ASan/UBSan ne remplace ni tests matériels, ni preuves générales de concurrence. `check-kernel-artifacts.py --kernel-only` valide noyau/modules sans exiger d’image de démarrage.

`check-audio-queue.py` teste le composant original de `research/audio/` avec une file de contenu de référence, 512 tailles et deux flux entrelacés. Il compare les frames synthétiques et le silence final, pas des registres ou de la mémoire DMA réelle. Voir `research/audio/README.md`.

## Adaptateur ALSA (E60)

`check-audio-adapter.py --source CANDIDAT --kernel SOURCE_LINUX --output RAPPORT` extrait les callbacks du correctif 0013, le rollback applicatif réel et les gardes mmap ALSA. Quinze scénarios, dont les 512 tailles et une fermeture concurrente contrôlée. Les registres et achèvements DMA sont simulés ; la stagnation du dernier bloc doit produire une erreur, pas un succès. Voir `docs/AUDIO-ALSA-ADAPTER.md`.

## Descripteurs et piste de registres audio (E62)

`check-audio-descriptors.py` compare les prepare avant/après 0014 sur 512 tailles et 16 384 entrées par variante. Il compile les définitions de registres SiS réelles et exécute les fonctions LibXenon sur des mots simulés. La concordance de sources ne démontre ni le protocole Xbox ni la fin de sortie sonore. Recette et limites : `docs/AUDIO-REGISTER-HYPOTHESIS.md`.


## Arrêt audio et durée de vie ALSA (E65/E66)

`check-audio-stop.py` teste le filtre et l'emprise de l'unique écriture sur mémoire ordinaire, sans matériel. `check-audio-free-contract.py --kernel SOURCE --output RAPPORT` extrait trois fonctions ALSA pour confronter les retours d'erreur à la libération et au détachement des tampons. Le comportement réel du canal analogique et les limites sont dans `docs/AUDIO-STOP-EXPERIMENT.md`. Les tests n'exécutent pas l'outil matériel.


## Protocole analogique et horloges (E67–E70)

`check-audio-protocol-step.py` vérifie le sélecteur, les préconditions et l'emprise des écritures ACK/reset sur mémoire ordinaire. Il ne lance pas les opérations matérielles. `check-clock-analysis.py` teste les bornes temporelles avec un taux connu et des captures invalides. `tools/measure-clock-drift.py --analyze CAPTURE --output NOUVEAU_RAPPORT` reproduit l'analyse sans accès SSH ; sans --analyze, il effectue seulement des lectures standard sur la console. Voir `docs/AUDIO-ACK-RESET.md` et `docs/TIMEBASE-CALIBRATION.md`.
