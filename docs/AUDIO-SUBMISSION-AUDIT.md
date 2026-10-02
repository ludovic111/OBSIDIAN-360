# Publication des échantillons audio — E58

Le suivi ajouté en E57 ne rend pas le pilote utilisable : sa fonction `.pointer` conserve une logique de publication incorrecte. Le nouveau banc reproduit les effets avec la fonction C réelle et les conversions réelles d’ALSA, hors console. Aucun correctif de soumission n’est activé.

## Mesures dans le banc hôte

Avec un tampon de 4 096 octets réparti en 32 descripteurs de 128 octets, l’index matériel lu reste à 7. Trois appels identiques de `.pointer` renvoient donc la même position de 224 frames. Pourtant, ils écrivent alternativement deux index différents dans le champ de file.

Le banc parcourt les 32 index de descripteurs et trois offsets applicatifs dans chacun, soit 96 cas. Pour un index applicatif D et un champ de file initial égal à D, les écritures sont successivement D−1, D, D−1, modulo 32. La condition historique dépend du champ relu, sans vérifier qu’une nouvelle donnée a été engagée par l’application. Ce résultat démontre la non-idempotence de la routine dans le modèle ; il ne mesure pas les registres vivants.

Le modèle n’écrase que les bits de l’index de file lors d’une écriture à ce registre et conserve les bits de position. Cette séparation correspond à l’interprétation des sources étudiées ; le comportement MMIO exact reste à vérifier sur le contrôleur.

Avec une seule frame engagée, soit quatre octets, un autre cas annonce le descripteur 0 entier. Si le champ désigne bien le dernier descripteur valide, comme dans LibXenon, cela annonce 128 octets alors que seulement quatre appartiennent au contenu engagé. Cette conséquence est **conditionnelle à cette sémantique**, pas une lecture DMA hors contenu observée sur la Xbox. Le tampon alloué reste plus grand : ce n’est pas le dépassement d’allocation d’E51.

## Conversion avant réduction : débordement reproduit

La routine convertit le compteur applicatif complet en octets puis le réduit modulo la taille du tampon. L’helper réel `frames_to_bytes` calcule d’abord `size * runtime->frame_bits / 8`, avec un entier signé. Pour 32 bits par frame et `LONG_MAX/32 + 1` frames sur l’hôte 64 bits, UBSan signale le débordement signé attendu. Le banc conserve ce diagnostic comme reproduction réussie d’un défaut, pas comme un test normal terminé avec succès.

La valeur synthétique reste sous une limite ALSA native possible : `pcm_native.c` double `boundary` tant que cette limite reste sous `LONG_MAX - buffer_size`. Le chemin de compatibilité 32 bits recalcule une limite plus petite ; le défaut n’est donc pas annoncé comme atteignable par les applications PowerPC 32 bits actuellement installées. Aucun très long flux réel n’a été exécuté. La correction doit réduire le nombre de frames à une plage bornée **avant** conversion, ou convertir un delta explicitement borné.

## Contrat à préserver pour le remplacement

La documentation ALSA prévoit `.ack` pour suivre les changements de `appl_ptr`. `pcm_lib_apply_appl_ptr` met à jour ce pointeur avant le callback et restaure l’ancienne valeur si le callback refuse. Un échec ne doit donc ni consommer l’avancement dans l’état privé du pilote, ni publier partiellement une nouvelle file. Le drapeau `SNDRV_PCM_INFO_NO_REWINDS` permet de déclarer une consommation monotone ; le retour circulaire de `boundary` doit rester accepté et distinct d’un recul.

Un simple déplacement des écritures vers `.ack` serait insuffisant. Le remplacement doit traiter au moins :

| Cas | Condition à vérifier |
|---|---|
| Aucune donnée nouvelle | Aucune nouvelle publication, même si `.pointer` est rappelé |
| Un tampon complet engagé d’un coup | Ne pas le confondre avec zéro donnée après réduction modulo |
| Écriture qui termine un descripteur | Publier les blocs complets seulement après la barrière DMA |
| Dernière écriture partielle puis drain | Jouer exactement le contenu final ou définir un bourrage silencieux contrôlé, sans attente infinie |
| Retour du compteur à `boundary` | Delta avant correct, sans débordement signé |
| Recul ou saut invalide | Refus avant mutation, en cohérence avec le rollback du cœur ALSA |
| Prepare, reset ou arrêt suivi de reprise | Recaler le suivi privé sur les conventions du cœur |
| Deux sorties | États applicatifs et publications indépendants |

Le `.prepare` du pilote est appelé avant le reset générique du cœur : il ne faut pas mémoriser aveuglément l’ancien `appl_ptr` à cet instant. Le reset en cours de lecture a aussi un chemin distinct. L’encodage des longueurs reste divergent entre Linux et LibXenon ; modifier un descripteur partiel pendant DMA sans comprendre son acquisition serait une nouvelle hypothèse matérielle.

## Références supplémentaires et limites

Le contrôleur audio de [Xenon Emulator](https://github.com/xenon-emu/xenon/blob/0284bbe6c8125935d97bf54ab3132089c6c65c8b/Xenon/Core/PCI/Devices/AUDIOCTRLLR/AudioController.cpp) a été examiné au commit `0284bbe6c8125935d97bf54ab3132089c6c65c8b`. Les écritures y sont journalisées ; aucune consommation de descripteurs ou lecture d’échantillons n’est implémentée dans cette classe. Il ne fournit donc pas un modèle de référence pour trancher la longueur ou la fin de file. Cette conclusion concerne ce fichier à cette révision, pas tous les autres périphériques de l’émulateur.

Sources locales analysées : noyau `a293dd19311668900eb1eeb2f6cb01dcac54f330`, LibXenon `a333adef440f28b436a667be0a4f014afce6349d`. Le fichier `sound.c` de LibXenon emploie un index de dernier bloc complet ; sa fonction de soumission ne règle pas à elle seule le drain d’une taille quelconque dans ALSA. Sa lecture suspecte du registre de base lors du redémarrage ne doit pas être copiée sans vérification.

Preuves : `evidence/2026-10-02/audio-submission/validation.json` et `sources.json`. Les sources tierces récupérées restent locales ; le dépôt publie les empreintes, références, modèles et assertions originaux.

```sh
python3 research/tests/check-audio-submission.py --source APRES_0012/sound/pci/snd-xenon.c --pcm-header SOURCE/include/sound/pcm.h --output submission.json
```

Aucune interaction avec la console pendant E58. L’étape suivante est de fixer le contrat de soumission et de fin de flux avant de proposer le remplacement de `.pointer`/`.ack`. Les variantes audio restent non activables tant que ces chemins et le protocole DMA ne sont pas validés.
