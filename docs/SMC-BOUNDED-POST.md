# Envoi SMC borné pour l’audio — E54

Le correctif 0010 ajoute une voie d’envoi distincte, `xenon_smc_post`, utilisée par le candidat audio après 0008/0009. Il cible le cœur SMC de linux-custom après les correctifs de cache/export déjà inclus dans obsidian4. Aucune commande envoyée à la Xbox pendant cette expérience ; aucune image installée.

## Contrat et portée

L’appel est réservé au contexte processus et prend un tampon noyau lisible de 16 octets. Le bit haut du premier octet doit être positionné, conformément à la convention « pas de réponse attendue » déjà utilisée dans `_xenon_smc_wait`. Cela ne valide pas la signification de tous les messages possibles ; le seul nouveau client est l’initialisation audio `8d 01 01`.

La fonction valide un budget de 1 à 1 000 microsecondes, copie les octets dans quatre mots alignés et tente immédiatement deux verrous : un mutex protégeant le cycle probe/remove, puis le verrou FIFO existant avec sauvegarde des interruptions. Un verrou occupé donne `-EBUSY`, sans attente et sans lecture du registre. Le transport absent donne `-ENODEV`.

Sous verrou FIFO, `readl_poll_timeout_atomic` interroge le bit de disponibilité, avec un délai nominal d’une microseconde par tentative. Le test emploie **les macros réelles de `include/linux/iopoll.h`**, pas une réécriture de leur boucle. Si le matériel simulé reste occupé, un budget de 1 000 donne 1 001 lectures et 1 000 appels de délai, puis `-ETIMEDOUT`. Un budget de 1 donne deux lectures et un délai. La dernière lecture peut encore réussir, conformément à la macro du noyau.

**Ce budget n’est pas une borne stricte de temps réel.** Le coût des opérations s’ajoute aux délais nominaux ; une transaction MMIO qui ne revient jamais ne peut pas être interrompue par ce mécanisme logiciel. Les anciens expéditeurs et fonctions d’attente restent inchangés et peuvent encore attendre sans borne. E54 ne résout donc pas tous les blocages possibles du SMC ou du noyau.

Après succès seulement, la séquence est exactement : ouverture FIFO par écriture 4, quatre mots de message via `writesl`, fermeture par écriture 0. Échec ou contention : aucune écriture. Les interruptions et verrous acquis sont restaurés sur les chemins testés.

## Protection pendant probe/remove

Le nouveau mutex exclut `xenon_smc_post` pendant les phases d’initialisation et de retrait. Une seconde initialisation est refusée si le transport existe déjà. Les erreurs de mappage et IRQ sont maintenant propagées, le pointeur mappé est effacé après nettoyage, et une activation PCI réussie est équilibrée même si la réservation échoue.

L’interruption PCI est masquée avant l’initialisation puis activée après acquisition du gestionnaire. Au retrait, elle est masquée, le gestionnaire est libéré avant le mappage, et les callbacks/pointeurs sont effacés. Ce mutex protège **la nouvelle voie** ; les accès concurrents des anciennes fonctions, qui ne le prennent pas, restent un audit distinct. Le banc séquentiel ne démontre pas leur sûreté lors d’un unbind concurrent. Ne pas provoquer un unbind réel pour tester cette hypothèse.

Le candidat audio masque aussi son interruption PCI dès l’activation de sa fonction et propage les erreurs du nouvel envoi avant de programmer ses canaux. Il n’effectue pas de tentative infinie ni de reprise automatique cachée en cas de contention.

## Tests et compilation

Dix-neuf scénarios passent sous ASan/UBSan : quatre échecs de probe, appel avant probe, double probe, pointeur nul, message avec réponse, budgets nul/trop grand, deux verrous occupés, disponibilité immédiate/tardive/à la dernière lecture, deux expirations, dernier essai avec budget minimal et restauration d’interruptions initialement désactivées. Le message de test est volontairement désaligné ; la copie transmise doit être alignée et identique octet par octet. L’appel après retrait est rejeté sans nouvelle lecture.

Les API de verrous, IRQ et MMIO sont simulées ; aucun délai physique ni entrelacement SMP n’est mesuré. Les codes numériques errno de la preuve hôte peuvent différer de Linux : les assertions C utilisent les noms symboliques. Le premier essai du banc a échoué sur l’avertissement de paramètre inutilisé de la fonction amont ; ce problème d’outillage est conservé puis corrigé en alignant cette option avec la compilation noyau.

Le banc audio de ressources passe désormais dix-huit scénarios, dont propagation de contention et d’expiration SMC. Les treize cas de comparaison originale et la régression des tampons restent conformes aux résultats attendus.

Deux compilations complètes sont maintenant vérifiées :

| Variante | Correctifs audio | Résultat |
|---|---|---|
| `6.18.11-xenon-audio-lifecycle` | 0008/0009 | Noyau et 70 modules, zéro avertissement |
| `6.18.11-xenon-audio-post` | 0008/0009/0010 | Noyau et 70 modules, zéro avertissement ; export GPL de xenon_smc_post présent |

Les 70 fichiers `.ko` ont un en-tête ELF64 PowerPC big-endian et un vermagic correspondant à leur variante. Les empreintes du noyau, des modules, des sources et les journaux sont conservés. Le second build réutilise une copie indépendante du premier dossier de sortie, avec les trois fichiers candidats montés en lecture seule. Le build obsidian4 reste intact.

Preuves : `evidence/2026-10-02/audio-lifecycle/full-build.*` et `evidence/2026-10-02/smc-post/`. Aucun conditionnement XeLL, initramfs, chargement ni démarrage de ces variantes. Le format des descripteurs, les adresses DMA, les PCM, les notifications et HDMI restent non validés ; ces noyaux ne sont pas prêts à remplacer celui de la console.

## Reproduction hors matériel

Appliquer 0008, 0009 puis 0010 aux sources de travail, et exécuter :

```sh
python3 research/tests/check-smc-post.py --source CANDIDAT/drivers/xenon/smc-core.c --iopoll SOURCE/include/linux/iopoll.h --output smc-post.json
python3 research/tests/check-audio-lifecycle.py --original ORIGINAL/sound/pci/snd-xenon.c --candidate CANDIDAT/sound/pci/snd-xenon.c --output audio-lifecycle.json
```

La compilation utilise les mêmes configuration et image LLVM 16 qu’E53, avec `LOCALVERSION=-audio-post` et les cibles `vmlinux modules`. L’ensemble des diffs doit reproduire exactement les empreintes de sources de `full-build.json` avant d’interpréter ces résultats.
