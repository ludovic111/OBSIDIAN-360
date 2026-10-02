# Arrêt analogique ciblé — E65

## Question et limites avant exécution

E64 trouve RUN apparent et des valeurs stables sans pilote audio Linux. Le candidat 0015 retire RUN mais ne vérifie ni halted ni la fin des transactions avant de réutiliser les tampons. La référence Intel attend halted après STOP ; le pilote intel8x0 comporte même une attente sans borne, à ne pas recopier sur Xbox. La similitude des registres SiS reste une hypothèse.

L'essai original `research/audio/stop_analog_once.c` n'effectue qu'une écriture possible : 0x00080000 au mot analogique +0x08, après vérification de l'identité PCI, du BAR de 64 octets, de l'absence de pilote et des deux contrôles exactement égaux à 0x1d08001c. Cela retire RUN/IRQ et ne renvoie pas de un aux statuts W1C supposés. Le champ intermédiaire est conservé. Aucun START, reset, remplacement de descripteur, envoi SMC, changement PCI ou accès flash.

Avant écriture, le programme publie et vide sa sortie standard. Après écriture, il relève les deux contrôles et les deux index : six lectures au total. Aucun polling ni réessai automatique. Le canal numérique n'est pas écrit et sert de comparaison. Si l'état initial diffère, aucune écriture. Aucun retour automatique à RUN : relancer une ancienne adresse DMA serait injustifié. Une lecture seule de suivi peut être effectuée après le retour du programme.

Une perte du réseau ou un gel demande une récupération manuelle par le démarrage obsidian4 connu, Ethernet débranché pendant Rock Band Blitz/XeLL. Un délai logiciel ne protège pas d'une transaction de bus bloquée. Pas de redémarrage volontaire pendant cet essai. Le firmware et les fichiers de démarrage ne sont pas modifiés.

## Vérification hors console

Le banc exécute le vrai C du filtre et de l'écriture sur mémoire ordinaire : seul l'état exact passe, 64 altérations d'un bit sont refusées sans changer la sortie, quatre octets seulement changent à +0x08. ASan/UBSan passent. Le calcul de page reprend celui corrigé en E64 ; cas 0x1600 vérifié. Le lancement sans argument renvoie 2 avant tout accès.

ELF32 PowerPC big-endian compilé sans diagnostic dans l'image audio-observer. Désassemblage : une seule instruction stw dans la séquence MMIO, adresse +8, mot converti en ordre little-endian, précédée de hwsync et suivie de eieio. Le binaire transféré doit avoir la même empreinte avant exécution.

Deux erreurs d'outillage conservées : compteur inutilisé dans le banc, puis extraction cherchant le libellé sync alors qu'objdump écrit hwsync. Les essais corrigés sont séparés des échecs ; aucune exécution matérielle durant ces erreurs.

Références : pilote `sound/pci/intel8x0.c` de la source épinglée a293dd19311668900eb1eeb2f6cb01dcac54f330 ; [Intel ICH4, section 14.2.7](https://www.intel.com/content/dam/www/public/us/en/documents/datasheets/82801db-io-controller-hub-4-datasheet.pdf). Cette référence n'identifie pas le contrôleur Xbox et ne prouve pas ses effets.

## Résultat matériel

Le 2 octobre à 12:47:31 UTC, l'essai a terminé code 0 sous obsidian4. L'écriture analogique de 0x00080000 a donné immédiatement 0x0008001d au contrôle et 0x00000000 à l'index. Le numérique est resté à 0x1d08001c / 0x00009616. Une seule écriture, six lectures, aucune relance automatique.

Le suivi en lecture seule à 12:48:41 UTC donne 0x0000001d pour le contrôle analogique, index zéro et numérique toujours inchangé. Le champ intermédiaire est donc passé de 8 à 0 entre ces deux observations ; son délai précis et son rôle ne sont pas mesurés. Quatre lectures supplémentaires, zéro écriture. SSH répond, framebuffer 1280×720, aucune unité systemd en échec listée. La réactivité visuelle n'a pas été vérifiée.

Sous le découpage étudié : RUN est retiré, DCH passe de 0 à 1 et les bits 2–4 restent à un malgré les zéros écrits. Cela appuie matériellement la séparation contrôle/statut et un indicateur d'arrêt sur ce canal. Cela ne démontre pas encore l'acquittement par écriture de un, le reset, l'absence de transactions en vol, le drain FIFO ou le comportement numérique. Le bit 15 de l'index analogique a disparu ; sa signification exacte reste ouverte.

L'analogique reste dans cet état STOP : aucun ancien RUN n'est restauré. Le canal numérique conserve son état hérité. Le prochain essai doit distinguer acquittement et reset, avec préconditions mises à jour ; ne pas relancer aveuglément l'outil de STOP, dont la condition initiale n'est désormais plus satisfaite.

## Contrat ALSA à respecter — E66

La revue du noyau a identifié une contrainte supplémentaire : retourner une erreur depuis hw_free n'empêche pas ALSA d'appeler snd_pcm_lib_free_pages ; le résultat de sync_stop est ignoré. Trois fonctions réelles extraites de pcm_native.c et pcm_memory.c sont exécutées sous ASan/UBSan : 144 combinaisons de callbacks/erreurs/états et types de tampon. Dans le banc, 24 cas détachent le tampon après une erreur d'un callback, dont 12 libèrent réellement une allocation dynamique. Ce sont des résultats du contrat logiciel, pas un défaut ALSA ni des erreurs observées sur la Xbox.

La distinction compte : les allocations préallouées sont détachées du runtime mais conservées pour réutilisation ; seules les allocations dynamiques sont libérées dans cette fonction. Le candidat réserve actuellement 64 Kio par flux, donc on ne doit pas présenter tous ces scénarios comme des libérations physiques de son tampon. La réutilisation exige néanmoins un état matériel cohérent.

Un simple ajout de polling suivi de return -ETIMEDOUT ne résout donc pas le cycle de vie. Avant toute intégration : arrêt confirmé pour chaque canal, reset borné avant remplacement des descripteurs et stratégie qui conserve/isole réellement la mémoire si l'arrêt échoue. Un effacement du bit PCI bus master n'est pas, à lui seul, une preuve mesurée de vidage des transactions. Les modèles précédents supposaient un STOP instantané ; ils ne couvrent pas ce problème.

Reproduction hors console :

```sh
python3 research/tests/check-audio-stop.py
python3 research/tests/check-audio-free-contract.py \
  --kernel .local/kernel-build/source/linux-custom-a293dd19311668900eb1eeb2f6cb01dcac54f330 \
  --output .local/audio-free-contract.json
```

La compilation croisée et l'empreinte du programme matériel sont décrites dans `evidence/2026-10-02/audio-stop/build.json`. L'exécution sur la console n'est pas incluse dans les commandes de tests.
