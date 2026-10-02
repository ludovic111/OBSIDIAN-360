# Adaptateur de soumission ALSA — E60

Le correctif `0013-xenon-audio-submission.patch`, appliqué après 0008–0012, intègre la file E59 au pilote candidat. Les requêtes de position ne publient plus de données. Les engagements passent par `.ack`, avec calcul du delta en frames avant conversion en octets. **Ce candidat reste expérimental et non installé : la fin du dernier descripteur DMA n'est pas décodée.**

## Contrat logiciel

- `.prepare` initialise la file, remet le canal à zéro et attend le RESET du cœur ALSA. Il ne prend pas l'ancien `appl_ptr` pour origine : `post_prepare` ne le recale qu'après le callback du pilote.
- `.ack` prépare une copie de la file, vérifie le delta et la position initiale si nécessaire, puis engage l'état. Les erreurs ne modifient ni file, ni curseur, ni registre. Le vrai `pcm_lib_apply_appl_ptr` restaure le curseur de l'application si le callback échoue.
- Seuls les blocs complets sont publiés, après barrière DMA. Un tampon plein publie bien 32 blocs ; une requête identique ne republie rien. Les reculs sont refusés avec `NO_REWINDS` et validation interne.
- Les deux sorties annoncent `SYNC_APPLPTR`. Le code ALSA refuse alors le mmap du contrôle, ce qui impose la synchronisation du curseur par ioctl et permet d'appeler `.ack`. Sans cette option, le déplacement des écritures depuis `.pointer` serait incomplet. Le mmap des échantillons reste permis. Pour les anciennes versions d'alsa-lib, le mmap du statut est également refusé par le cœur.
- START arme le suivi, mais n'active DMA que lorsqu'un bloc entier existe. Ceci permet l'ordre START puis DRAIN employé par ALSA pour un flux court.
- DRAIN ferme la file aux nouveaux engagements, met à zéro le reste du dernier bloc, puis publie. Le silence n'est pas compté dans la position logique communiquée à ALSA. Un drain répété n'écrit pas une seconde fois.
- `.pointer` renvoie la position logique mise en cache par le suivi. Il ne lit ni écrit de registre et ne convertit jamais le compteur applicatif complet.
- Le timer comptabilise les changements d'index, rejette une progression supérieure aux données soumises et signale les périodes hors verrou du pilote. La fermeture attend toujours le callback en cours.
- RESET n'est accepté que sur une file préparée, vide et à son origine. RESET pendant la lecture ou après soumission renvoie `-EBUSY`, sans rebaser arbitrairement les compteurs. STOP puis PREPARE permet un nouveau flux. Ce refus est une limitation fonctionnelle explicite du candidat.

Les verrous suivent l'ordre ALSA puis pilote pour RESET. Les services ALSA de notification restent appelés après libération du verrou du pilote. Le composant de file ne réalise lui-même ni synchronisation ni accès matériel.

## Fin de bloc : hypothèse encore ouverte

Le suivi continue d'interpréter l'index matériel comme celui du bloc courant ; un changement d'index signifie, dans le modèle, que les blocs précédents sont terminés. Cette interprétation et l'absence de prélecture doivent encore être vérifiées sur la console.

En particulier, un dernier index inchangé et un résiduel nul peuvent être observés avant même que le moteur ait commencé. Le candidat **ne les transforme pas en succès de lecture**. Si le matériel reste sur le dernier index après avoir joué le bloc, la fin du drain ne sera donc pas reconnue. Le test `stalled_final` reproduit cette limite : le candidat finit par déclarer une erreur de flux, pas une lecture réussie.

Un suivi trop tardif, une horloge reculant ou une absence de progression pendant une durée de tampon déclenche un XRUN. Cette borne est une politique logicielle calculée à 192 000 octets/s ; aucune borne de latence réelle n'est mesurée. Elle peut provoquer des faux refus et doit être évaluée. Une progression fictive vers l'index suivant dans le banc permet de tester la comptabilité du silence final ; elle ne démontre pas que le contrôleur produit cet événement.

Les divergences d'encodage des longueurs, les adresses DMA et l'initialisation HDMI/analogique restent aussi ouvertes. Aucun de ces points n'est résolu par le succès d'une compilation. Ne pas charger ce candidat pour déclarer l'audio fonctionnel.

## Vérifications reproductibles

Sur la source reconstruite avec les correctifs, et les sources Linux épinglées au commit `a293dd19311668900eb1eeb2f6cb01dcac54f330` :

```sh
python3 research/tests/check-audio-adapter.py \
  --source CANDIDAT/sound/pci/snd-xenon.c \
  --kernel SOURCE_LINUX --output adapter-validation.json
python3 research/tests/check-audio-queue.py --output queue-validation.json
python3 research/tests/check-audio-lifecycle.py \
  --original SOURCE_LINUX/sound/pci/snd-xenon.c \
  --candidate CANDIDAT/sound/pci/snd-xenon.c --output lifecycle-validation.json
```

Le nouveau banc extrait les callbacks C candidats, le vrai `pcm_lib_apply_appl_ptr` et les deux fonctions ALSA qui décident l'accès mmap au contrôle/statut. Quinze scénarios passent sous ASan/UBSan : fragments, tampon plein, erreurs avec rollback, remise à zéro, grands compteurs et retour de boundary, deux sorties, stagnation, retard, mmap et fermeture concurrente contrôlée. L'un des scénarios parcourt les 512 tailles. Les registres, l'horloge et les services ALSA restants sont simulés ; ce n'est pas une exécution du cœur ALSA complet ou une preuve SMP générale.

Vingt scénarios de ressources du candidat passent également, avec les treize scénarios de référence aux résultats attendus. La file renommée repasse ses 54 008 opérations et 24 544 033 frames comparées. La reconstruction du correctif produit exactement les trois fichiers compilés ; la copie intégrée de la file est égale au composant canonique, à son nom d'en-tête près.

Échecs conservés :

1. Le premier banc hôte traite une comparaison signée du cœur ALSA comme erreur. L'avertissement est désactivé uniquement autour de cette fonction amont inchangée, pas dans le candidat.
2. Docker ne peut créer de nouveaux points de montage sous le répertoire source en lecture seule. Une copie indépendante de `sound/pci` contenant les nouveaux fichiers est montée à la place ; les sources de référence restent inchangées.
3. La première compilation intégrée révèle que le paramètre `current` de la file entre en collision avec une macro du noyau déjà incluse par le pilote. Il devient `position` dans les sources canoniques. Le test E59 isolé n'incluait pas cette macro et n'avait donc pas détecté le conflit.

Les premiers échecs, la recette de construction, les empreintes et les résultats finaux sont dans `evidence/2026-10-02/audio-adapter/`. Le nouveau répertoire de construction est une copie indépendante de celui d'audio-poll ; les artefacts obsidian4 restent préservés. Aucun initramfs ni image XeLL préparé pour ce candidat.

Noyau `6.18.11-xenon-audio-submit` et 70 modules compilés sans avertissement à 10:52:58 UTC ; formats ELF PowerPC et vermagic vérifiés. Aucune installation ni image de démarrage produite.

## Contrôle vivant distinct — E61

Le 2 octobre à 10:49:58 UTC, SSH répond sous `6.18.11-xenon-obsidian4`, avec 9 327,35 secondes de fonctionnement, aucune unité en échec listée et framebuffer 1280 × 720. Ce relevé utilise les interfaces noyau/systemd standards ; il ne vérifie ni la réactivité visuelle, ni le son, ni la stabilité sous charge. Aucun redémarrage ni changement de configuration de la console pendant E60/E61.
