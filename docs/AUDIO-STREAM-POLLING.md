# Suivi des flux et synchronisation audio — E57

Le correctif 0012 s’applique après 0011. Chaque sortie possède son propre timer ; START l’arme, STOP marque le flux arrêté, et `.sync_stop` attend la fin des callbacks avant reconfiguration. Les tests hôtes passent. La variante finale avec haute résolution compile avec 70 modules, sans avertissement ; aucun fichier installé sur la console.

## Défauts reproduits dans la version précédente

Le banc extrait les fonctions C de la variante 0011. Après START, aucun timer n’est armé. Il appelle ensuite directement deux fois le callback historique, avec le même registre de position nul : deux notifications de période sont produites, malgré l’absence de déplacement. C’est une reproduction hors matériel d’un défaut latent du calcul, pas une notification observée sur la Xbox ; le timer non armé empêchait justement cette exécution normale.

Le calcul historique comparait la taille du tampon moins une estimation de la file restante à la taille d’une période. Il ne conservait pas de progression depuis la précédente notification. Le callback libérait aussi le verrou puis relisait `playback_substream`, sans synchronisation PCM garantissant sa durée de vie.

## Nouveau suivi

Un `hrtimer` en mode relatif soft est initialisé pour chaque canal avant que la carte ALSA ne devienne propriétaire des ressources. `.open` ne remet plus toute la structure à zéro, ce qui détruirait ce timer. START mémorise la position initiale, remet le compteur de période à zéro et arme le suivi à 200 microsecondes nominales.

Sous le verrou du pilote, le callback lit l’index du descripteur, calcule son déplacement modulo le tampon, puis accumule les octets depuis la dernière période. Une position inchangée n’ajoute rien. Le reste est conservé après notification. Si plusieurs périodes sont franchies, un seul appel à `snd_pcm_period_elapsed` suffit : le cœur ALSA actualise sa position et sa disponibilité, comme l’indique `sound/core/pcm_lib.c`.

La position reste grossière, au niveau des descripteurs. Le champ de longueur résiduelle n’est pas intégré tant que sa sémantique matérielle n’est pas établie. Cette limite peut retarder les notifications des périodes plus petites qu’un descripteur ; aucun objectif de latence réelle n’est annoncé.

Un compteur modulo ne distingue pas zéro déplacement d’un tour entier. Si l’intervalle entre deux observations atteint la durée théorique du tampon à 48 kHz, stéréo 16 bits, le candidat arrête le canal et signale un XRUN au lieu de supposer un déplacement. Un temps simulé négatif est également refusé. Ce choix est conservateur : un gros retard d’ordonnancement peut provoquer un arrêt même si le matériel n’avait pas réellement consommé tout le tampon. Il dépend du débit de lecture attendu et ne valide pas celui du contrôleur.

## Ordre des verrous et fermeture

Les callbacks `.trigger` et `.pointer` sont atomiques et invoqués avec les interruptions locales désactivées selon la documentation ALSA de cette source. Le timer prend le verrou du pilote avec sauvegarde des interruptions. Il en sort avant d’appeler `snd_pcm_period_elapsed` ou `snd_pcm_stop_xrun`, qui peuvent reprendre le verrou ALSA puis rappeler STOP. Un STOP déclenché par cette notification empêche le réarmement.

STOP ne fait pas d’annulation synchrone : attendre un callback qui cherche le verrou ALSA déjà détenu risquerait un interblocage. `.sync_stop` annule le timer hors verrou du pilote, après l’arrêt et avant reconfiguration. `.hw_free` arrête le canal, invalide sa géométrie, puis effectue aussi cette synchronisation avant de rendre la main au cœur ALSA. `.close` passe par ce chemin avant d’effacer le propriétaire.

Le retrait de la carte marque `shutting_down`, arrête les deux canaux, annule les deux timers et désactive la maîtrise du bus avant libération des ressources. Le marqueur interdit un nouveau START. Les accès MMIO restent ceux du pilote ; l’arrêt effectif des transactions DMA n’est pas prouvé par une écriture et une relecture de registre.

## Précision du timer : configuration distincte

La configuration héritée désactivait `CONFIG_HIGH_RES_TIMERS`, avec `CONFIG_HZ=300`. Demander 200 microsecondes ne suffit pas à les obtenir dans ce mode : un tick vaut environ 3,33 ms, contre 0,667 ms de contenu pour le tampon minimal de 128 octets.

La configuration candidate active `CONFIG_HIGH_RES_TIMERS`. Les choix dérivés comprennent `CONFIG_TICK_ONESHOT` et `CONFIG_SCHED_HRTICK` ; leur différence complète est conservée. Le pilote refuse `.open` avec `-ENODEV` si le timer du canal n’a pas la haute résolution active. Une compilation avec l’option ne prouve pas son activation sur chaque CPU ni sa latence réelle : il faudra mesurer celles-ci après un démarrage coordonné, lorsque le protocole audio sera prêt. La cadence nominale représente jusqu’à 5 000 callbacks par seconde et par sortie ; son coût CPU est inconnu, à mesurer avant optimisation.

## Preuves et essais

Les fonctions du pilote sont extraites de la source locale ; les tests ne réimplémentent pas leur algorithme.

- Quinze scénarios de suivi : position fixe et départ non nul, seuil et reste de période, franchissement de plusieurs périodes, retour circulaire, arrêt d’une sortie, annulation d’une sortie, arrêt pendant notification, retards et frontières temporelles, horloge simulée inverse, période nulle, retrait, fermeture concurrente.
- Le cas concurrent utilise deux threads pthread. Une notification est suspendue à un point contrôlé ; `.hw_free` atteint l’annulation et doit attendre. La libération simulée n’est autorisée qu’après sortie du callback. L’autre canal reste armé. Cela couvre cet entrelacement précis, pas tous les ordres possibles dans le noyau.
- Vingt scénarios de ressources passent, dont retrait avec les deux timers actifs et échecs d’allocation partiels.
- Quinze scénarios PCM passent, dont refus d’une période nulle/trop grande et d’un timer sans haute résolution. La régression sur 16 369 tailles conserve 512 tailles acceptées sans descripteur hors tampon.

ASan/UBSan sont activés ; verrous noyau, ALSA, DMA, MMIO et temps matériel sont remplacés par des modèles. L’absence de diagnostic ne constitue pas une validation SMP, temps réel ou matérielle.

Deux premières compilations complètes ont réussi avec l’ancienne configuration basse résolution. La première version a toutefois échoué au banc hôte plus strict sur deux comparaisons signées/non signées ; les conversions et le traitement du temps négatif ont été corrigés. Les premières preuves sont conservées avec leurs empreintes distinctes. Elles ne prouvent pas la compilation de la variante finale haute résolution.

Une erreur de commande du banc de géométrie (`--output` non pris en charge) a été corrigée en redirigeant sa sortie JSON ; la recette E55 est rectifiée. Ce n’était pas un échec de géométrie.

Preuves : `evidence/2026-10-02/audio-poll/`. Les patches 0008 à 0012 reconstruisent exactement les trois sources candidates. La configuration finale y est conservée ; les journaux des premières compilations sont identifiés comme tels.

## Reproduction et limites restantes

```sh
python3 research/tests/check-audio-poll.py --previous APRES_0011/sound/pci/snd-xenon.c --candidate APRES_0012/sound/pci/snd-xenon.c --output polling.json
python3 research/tests/check-audio-lifecycle.py --original ORIGINAL/sound/pci/snd-xenon.c --candidate APRES_0012/sound/pci/snd-xenon.c --output lifecycle.json
python3 research/tests/check-audio-pcm.py --source APRES_0012/sound/pci/snd-xenon.c --output pcm.json
python3 research/tests/check-audio-buffers.py --original ORIGINAL/sound/pci/snd-xenon.c --candidate APRES_0012/sound/pci/snd-xenon.c > buffers.json
```

Utiliser ensuite la configuration fournie et l’environnement LLVM 16 d’E53 avec `LOCALVERSION=-audio-poll`, cibles `olddefconfig vmlinux modules`. Aucun initramfs ou fichier XeLL de cette variante n’est préparé.

La publication des échantillons dans `.pointer` reste à remplacer par un suivi de `appl_ptr` via `.ack`. Restent aussi l’encodage des longueurs, la limite mémoire basse et l’initialisation analogique/HDMI. Aucun son mesuré, aucune nouvelle interaction matérielle durant E57 ; dernier contrôle vivant E56.

## Compilation finale vérifiée

`6.18.11-xenon-audio-poll`, configuration HIGH_RES_TIMERS activée : cibles olddefconfig, vmlinux et modules terminées avec code 0. Les 70 modules et le noyau sont ELF64 PowerPC big-endian, avec vermagic concordant ; configuration et sources correspondent aux empreintes conservées. Aucun avertissement dans le journal. Preuves `final-build.json`, `final-build.log` et `final-artifacts.json`. Aucun initramfs/image XeLL, démarrage ni chargement. E58 ajoute l’audit des défauts restants de publication dans `docs/AUDIO-SUBMISSION-AUDIT.md`.
