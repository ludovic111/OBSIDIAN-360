# Acquittement et reset analogiques — E67/E68

## Plan avant interaction

E65 a laissé le contrôle analogique à 0x0000001d avec index zéro. Une nouvelle lecture le confirme sous obsidian4 à 12:58:51 UTC ; le numérique est toujours 0x1d08001c / 0x00009616. L'hypothèse est que les bits 2, 3 et 4 du statut sont acquittés individuellement en écrivant un, tandis que le bit 0 indique l'arrêt.

L'outil `research/audio/analog_protocol_step.c` permet quatre opérations fixes, jamais enchaînées automatiquement. Chaque appel exige un pilote absent, l'identité PCI 1414:580c, le BAR attendu et quatre mots d'état exacts. Il n'écrit qu'un mot à +0x08 ; RUN et activations IRQ restent à zéro. Huit lectures au maximum sur le chemin accepté, une écriture. Une différence de précondition entraîne un refus avant l'écriture.

| Option | Contrôle analogique requis | Valeur écrite | Résultat prédit, non mesuré à la préparation |
|---|---|---|---|
| --ack-bit2 | 0x0000001d | 0x00000004 | 0x00000019 |
| --ack-bit3 | 0x00000019 | 0x00000008 | 0x00000011 |
| --ack-bit4 | 0x00000011 | 0x00000010 | 0x00000001 |
| --reset-stopped | 0x00000001 | 0x02000000 | reset qui se retire ; statut à observer |

Index analogique zéro et mots numériques inchangés sont exigés pour chaque opération. Examiner la preuve de chaque appel avant le suivant. Si le résultat diverge, ne pas adapter silencieusement les valeurs ni lancer la suite. L'option reset ne doit être exécutée qu'après examen des acquittements et vérification de l'arrêt. Aucune publication de descripteurs, aucun START, aucune commande SMC ou configuration PCI/flash. Le canal numérique n'est pas écrit.

La lecture MMIO peut bloquer malgré les limites de volume. Une perte d'accès nécessite la récupération manuelle obsidian4 connue ; ne pas répéter une opération après timeout sans établir son résultat. Aucun redémarrage volontaire ni relance de l'ancien DMA. Les écritures acquittent seulement des événements déjà enregistrés ou réinitialisent le canal arrêté ; elles ne constituent pas un test de sortie sonore.

## Vérifications de l'outil

Banc C réel sous ASan/UBSan : quatre valeurs permises, 512 altérations d'un bit refusées, quatre octets modifiés seulement à +8 sur mémoire ordinaire, aucune activation RUN/IRQ. ELF32 PowerPC statique compilé sans avertissement ; une stw alignée relue dans le désassemblage, avec conversion d'octets et barrières hwsync/eieio. Ces tests valident l'outil, pas le protocole matériel. Les résultats sont conservés dans `evidence/2026-10-02/audio-ack/`.

## Résultats

E67 exécuté : trois appels distincts ont donné exactement 0x1d → 0x19 → 0x11 → 0x01 après les écritures 4, 8 et 16. Le bit d'arrêt est conservé et seul le bit ciblé disparaît. Les mots numériques et les index restent inchangés. Cela démontre le comportement W1C observé des bits analogiques 2–4 dans cet état arrêté ; cela ne prouve pas la signification de chaque événement pendant un flux.

Preuves : ack-bit2.json, ack-bit3.json et ack-bit4.json. Vingt-quatre lectures MMIO et trois écritures au total pour les acquittements. Tous les appels terminent code 0 et SSH répond. Les horodatages des étapes sont émis par la console ; l'enveloppe du relevé utilise l'horloge du Mac. Leur écart apparent doit être mesuré avant toute comparaison de latence entre les machines.

E68 exécuté depuis 0x00000001 : écriture 0x02000000, puis retour immédiat à la lecture de 0x00000001, index zéro et numérique inchangé. Huit lectures, une écriture, code 0 ; preuve reset-stopped.json. Aucun START ni nouveau tampon.

Cette lecture est compatible avec un bit reset auto-effacé, mais le bit n'a jamais été observé à un et les autres mots observés étaient déjà dans l'état attendu après reset. On ne peut donc pas distinguer entièrement une réinitialisation interne accomplie d'une commande ignorée sur les seules valeurs acquises. Les effets sur les registres non lus ne sont pas démontrés. Ne pas annoncer un reset complet validé.

Au total E67/E68 : quatre écritures au mot analogique, 32 lectures pendant ces opérations, plus quatre lectures initiales. Les adresses de descripteurs n'ont été ni lues ni remplacées. Le canal reste en état arrêté avec statuts d'événements acquittés ; numérique inchangé. L'horloge de la console est ensuite examinée séparément en E69.
