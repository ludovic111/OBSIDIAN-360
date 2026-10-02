# Audio : portage des ressources — E53

Travail hors console du 2 octobre 2026. Le correctif `0009-xenon-audio-resource-lifecycle.patch` s’applique après 0008 au pilote linux-custom `a293dd19311668900eb1eeb2f6cb01dcac54f330`. Aucun module chargé ni nouveau noyau installé. Le dernier relevé matériel reste E52 ; ce travail ne rafraîchit pas l’état vivant de la console.

## Défauts reproduits

Le banc extrait les véritables structures et fonctions d’allocation, création de PCM, initialisation, probe, retrait et libération. Les interfaces du noyau sont remplacées par un modèle de ressources ; les callbacks sont exécutés séquentiellement, sans vrai DMA, IRQ, transport SMC ou timer.

Treize scénarios sur l’original : un cycle normal passe et douze erreurs attendues sont reconnues précisément.

| Injection | Résultat de l’original |
|---|---|
| Création de carte retourne ENOSPC | Le pilote le remplace à tort par ENOMEM |
| Activation PCI, allocation chip, mauvais type BAR, réservation PCI | Accès à un pointeur nul dans la libération, détecté par UBSan |
| Demande IRQ, création PCM 0/1, enregistrement lowlevel | Nettoyage d’un timer non initialisé, détecté par le modèle |
| Enregistrement final de carte | Réutilisation de mémoire libérée, détectée par ASan après le premier nettoyage |
| Handle DMA synthétique avec bits hauts | Le handle passé à free diffère de celui retourné par l’allocateur |
| Retrait avec flux et timer simulés actifs | Le modèle détecte la libération des PCM avant leur mise au repos |

Le handle synthétique ne représente pas une adresse effectivement allouée sur Xbox. Le retrait actif est une injection dans le modèle, pas une observation de trafic DMA. Les processus qui échouent tôt ne prouvent pas l’absence ou la présence de tous les défauts masqués par ce premier échec.

Le premier essai du banc n’avait pas compilé : signature fictive du gestionnaire IRQ incorrecte et dépréciation macOS de `sprintf`. Ce défaut d’outillage est conservé dans `harness-first-attempt.json` ; il n’est pas attribué au pilote. Le banc corrigé utilise un prototype conforme et désactive seulement ce diagnostic de dépréciation de la bibliothèque hôte, en conservant `-Wall -Wextra -Werror` pour les autres diagnostics pertinents.

## Correctif candidat

La carte ALSA devient l’unique propriétaire de l’objet privé dès que son verrou et son timer sont initialisés. Les drapeaux d’acquisition indiquent quelles ressources libérer en cas d’échec partiel. `snd_card_free` intervient une seule fois ; son callback privé libère l’objet après les PCM, conformément à `sound/core/init.c:snd_card_do_free`.

Le retrait et les échecs après allocation mettent d’abord les deux canaux au repos, arrêtent le timer avec `timer_shutdown_sync` et désactivent le bus mastering PCI. Le modèle vérifie cet ordre avant la destruction des PCM. L’effet réel des écritures d’arrêt du contrôleur reste à confirmer.

Les descripteurs utilisent `dma_alloc_coherent` hors verrou, avec contrôle d’échec et conservation exacte du handle pour `dma_free_coherent`. Le masque DMA demandé est de 29 bits, cohérent avec le masquage historique mais **non validé comme limite matérielle**. La comparaison LibXenon ci-dessous impose une revue supplémentaire avant activation.

Le transport SMC privé et son mappage direct sont supprimés au profit de `xenon_smc_ready` et `xenon_smc_message`. Cela utilise le verrou commun, mais ne corrige pas l’attente sans borne du cœur SMC : aucune garantie de délai ne doit être revendiquée. L’ancien gestionnaire IRQ répondait toujours « traité » sans reconnaître ni acquitter une source ; il est retiré et l’interruption PCI de cette fonction est désactivée. Le futur fonctionnement par interrogation périodique reste à terminer.

L’API du timer devient `timer_container_of`. Les diagnostics obsolètes `snd_printk` disparaissent avec les anciens chemins d’erreur. Les seize scénarios du candidat passent : cycle normal, carte, PCI, allocation, BAR incorrect ou trop court, masque DMA, réservation, mappage, allocation DMA, SMC indisponible ou en échec, deux PCM, enregistrement final et retrait actif simulé. Le modèle termine avec zéro ressource détenue dans chaque cas, et ASan/UBSan ne signalent aucune erreur. Ces tests ne couvrent pas les entrelacements SMP ni tous les ordres possibles d’ouverture/fermeture ALSA.

La régression E51 reste verte : 16 369 tailles examinées, 512 acceptées, zéro géométrie hors tampon pour ces tailles, huit cas de boucle de cache vérifiés.

## Compilation

La compilation de l’objet PowerPC `sound/pci/snd-xenon.o` réussit sans avertissement avec LLVM 16. Elle utilise un nouveau dossier de sortie et une substitution en lecture seule du seul fichier candidat ; le build obsidian4 reste intact. La compilation complète noyau/modules a ensuite réussi, avec 70 modules et aucun avertissement : consulter `evidence/2026-10-02/audio-lifecycle/` pour son résultat, sans confondre objet compilé, module lié et pilote fonctionnel.

## Divergences de protocole à résoudre

Référence locale vérifiée : Free60Project/libxenon `a333adef440f28b436a667be0a4f014afce6349d`, fichier `libxenon/drivers/xenon_sound/sound.c`, sans modification locale. Comparaison conservée dans `source-comparison.json`.

| Sujet | Linux historique | LibXenon | Conséquence |
|---|---|---|---|
| Placement | Masquage sur 29 bits | Commentaire signalant apparemment les premiers 32 Mio ; sections mémoire basses | La plage DMA réelle n’est pas démontrée ; revoir la borne avant essai |
| Longueur d’un segment de 2 048 octets | `0x800007ff` | `0x80000800` | Encodage longueur moins un contre longueur littérale ; protocole non arbitré |
| HDMI | Message SMC `8d 01 01` | Réinitialisation GPIO du DAC et onze écritures I²C via SMC, puis le message | Un périphérique ALSA ne prouve pas que HDMI émettra du son |

Ne pas copier aveuglément une initialisation provenant d’un autre environnement : LibXenon suppose un placement et un contexte de démarrage différents. Les tests de géométrie E51 suivent explicitement l’encodage du pilote Linux ; ils ne prouvent pas celui du contrôleur physique.

Autre piste confirmée par le code du noyau : `SNDRV_DMA_TYPE_DEV` utilise déjà `dma_alloc_coherent` et `dma_mmap_coherent` dans `sound/core/memalloc.c`. Refaire un `ioremap` à partir de `runtime->dma_addr` et appliquer des instructions de cache privées n’est pas le contrat de cette API. Le prochain portage doit utiliser l’adresse CPU `runtime->dma_area`, les barrières appropriées et une gestion des PCM qui arrête les accès avant de rendre la mémoire.

## Reproduction

Appliquer 0008 puis 0009 à une copie du pilote original. Exécuter :

```sh
python3 research/tests/check-audio-lifecycle.py --original ORIGINAL/snd-xenon.c --candidate CANDIDAT/snd-xenon.c --output validation.json
python3 research/tests/check-audio-buffers.py --original ORIGINAL/snd-xenon.c --candidate CANDIDAT/snd-xenon.c
```

Le premier banc exige les deux fichiers de scaffolding voisins ; il vérifie les diagnostics attendus de l’original, pas simplement un code de sortie non nul. Un succès signifie que les défaillances prévues ont été reproduites et que le candidat passe les scénarios du modèle.

Pour compiler, reprendre la configuration et l’image décrites dans `AUDIO-BUFFER-AUDIT.md`, appliquer les deux diffs à une source de travail séparée, puis construire l’objet ou `vmlinux modules` avec `LOCALVERSION=-audio-lifecycle`. Aucun conditionnement pour XeLL ni installation ne fait partie de cette expérience.

Le candidat reste **impropre à une activation** tant que les points DMA, timer/notifications, fermeture concurrente, délai SMC et protocole réel ne sont pas résolus. Il ne valide ni audio analogique, ni S/PDIF, ni HDMI.
