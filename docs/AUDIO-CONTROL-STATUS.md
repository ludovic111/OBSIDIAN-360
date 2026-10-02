# Contrôle audio et observation ciblée — E63/E64

## Séparation logicielle du contrôle et du statut

Le mot audio +0x08 (+0x18 numérique) ressemble au regroupement SR/PIV/CR de la référence SiS décrite dans `AUDIO-REGISTER-HYPOTHESIS.md`. Si les bits SR 2–4 sont acquittés par écriture de un, réécrire le mot lu pendant START/STOP efface des événements. Ce comportement est une hypothèse de modèle, pas une mesure Xbox.

Le correctif 0015 masque ces bits et les activations IRQ avant de modifier RUN. Prepare conserve un acquittement explicite au repos. Le champ intermédiaire historique reste inchangé, son rôle Xbox n'est pas validé. Aucun décodeur de fin sonore ni attente de reset n'est ajouté.

Le banc extrait les fonctions C réelles : deux canaux, 32 prélectures, 32 statuts et deux transitions, soit 4 096 cas par variante. Avant : 3 584 transitions effacent un statut et toutes conservent les interruptions activées. Après : zéro de chaque. Quinze scénarios adaptateur, vingt ressources et 16 384 descripteurs repassent. ASan/UBSan sans diagnostic. Preuves : `evidence/2026-10-02/audio-control/`.

Le module final est ELF64 big-endian PowerPC, vermagic audio-bytes ; aucune compilation de vmlinux dans E63. La première cible isolée échoue au modpost faute de dépendances ALSA ; la cible modules complète réussit sans avertissement. Aucun chargement.

## Préparation de l'observation — pas de démarrage DMA

Le relevé PCI standard donne 1414:580c, BAR0 de 64 octets, driver absent et enable=0. PCI command=0x0006 signifie que le matériel autorise mémoire et bus mastering, pas qu'un transfert est actif.

L'observateur original `research/audio/read_status_once.c` refuse une identité inattendue, un pilote attaché, une fenêtre incorrecte ou le décodage mémoire désactivé. Il ouvre resource0 en lecture seule et ne lit que +0x04/+0x08/+0x14/+0x18, déjà utilisés par le pilote. Aucune écriture de registre, activation PCI, allocation DMA ou commande SMC. Ne pas confondre cette fenêtre audio avec la fenêtre flash interdite E10. Une lecture MMIO peut toutefois bloquer le bus ; aucun timeout logiciel ne garantit de l'interrompre.

La revue a détecté avant exécution un défaut de la première version : sysfs mappe la page contenant le BAR, pas son premier octet. Le noyau retenu utilise drivers/pci/mmap.c et décale resource_start de PAGE_SHIFT. Il faut donc ajouter 0x1600 au mapping avec les pages de 64 Kio de cette console. La fonction corrigée est testée sur 31 744 positions et sept entrées invalides, sous ASan/UBSan. Aucun ancien binaire n'a lu les registres. L'ELF32 PowerPC final contient quatre lwz alignés, huit eieio, conversions d'ordre des octets et aucune écriture MMIO dans la séquence désassemblée.

L'environnement de compilation ARM ne proposait pas le compilateur croisé ; le constructeur Docker historique sélectionnait encore ARM malgré --platform. Une base explicite amd64/debian avec vérification de l'architecture réussit. Deux échecs conservés. Le binaire statique transféré dans /tmp a la même empreinte ; son lancement sans argument renvoie l'usage avant tout accès matériel. Aucun paquet installé sur la console.

La lecture matérielle proprement dite et son interprétation doivent être enregistrées séparément. Les bits observés, même compatibles avec SiS, ne prouveront ni les effets d'acquittement, ni la progression DMA, ni une sortie sonore.

## Mesure directe du 2 octobre 2026

Les trois captures à 12:05:30.002727, 12:06:27.111764 et 12:06:27.219473 UTC ont réussi et sont identiques. Douze accès MMIO alignés au total, zéro écriture. Le processus et SSH ont répondu après chaque capture sous obsidian4 ; réactivité visuelle non vérifiée.

| Canal | Mot index/résiduel | Mot contrôle/statut |
|---|---|---|
| Analogique | 0x00008000 | 0x1d08001c |
| Numérique | 0x00009616 | 0x1d08001c |

**Interprétation hypothétique** : avec les masques SiS/LibXenon, index courant=dernier index (0 pour analogique, 22 pour numérique), résiduel nul, RUN=1, activations IRQ=0x1c, statut bas=0x1c et bit halted=0. Ce n'est pas la signature simple d'un contrôleur arrêté. Le bit 15 du mot index est présent sur les deux canaux et n'est pas expliqué ici. Le contrôle observé est exactement la constante d'initialisation de LibXenon : on ne sait pas distinguer par ces lectures seules un état hérité, un registre partiellement mémorisé ou des événements matériels.

L'égalité des snapshots ne prouve pas l'absence de DMA entre observations, pas plus que le résiduel nul ne prouve une fin sonore. Le compteur Linux enable et l'absence de pilote ne doivent donc pas servir de preuve de repos matériel avant réinitialisation/libération de tampons. La sémantique W1C du modèle E63 reste à valider séparément ; ces mots ne la démontrent pas. Aucune écriture supplémentaire n'a été tentée pour trancher.

Prochaine étape : concevoir et relire une transition STOP/reset bornée et une observation de sa confirmation avant tout pilote audio actif. Préserver le démarrage éprouvé et une récupération physique coordonnée. L'observateur ne doit pas devenir un balayage arbitraire de registres.
