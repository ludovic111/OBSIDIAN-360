# Longueurs audio et piste SiS — E62

L'historique de LibXenon permet de trancher un choix du **candidat logiciel** : les longueurs deviennent des nombres d'octets, sans soustraction de un. Le correctif 0014 adopte ce comportement et supprime le champ de compensation devenu inutile avec les géométries bornées. Aucun son ni registre vivant n'est mesuré dans cette expérience.

## Preuve historique plus précise

Le [correctif LibXenon du 15 décembre 2010](https://github.com/Free60Project/libxenon/commit/30966e043f4b1e488967142bafb680286552d77f) change explicitement le champ de `taille−1` vers `taille` pour corriger du bruit. La révision LibXenon déjà étudiée conserve cette correction. Ce n'est donc pas seulement une divergence inexpliquée entre deux fichiers contemporains.

Le [correctif du 25 juin 2011](https://github.com/Free60Project/libxenon/commit/80cc0f2bcaac4827152eb4dd323cbd34cbeaeb39) décale aussi la publication vers le dernier bloc complet. Cette modification appuie le choix effectué en E59/E60. Le [changement de placement mémoire de 2012](https://github.com/Free60Project/libxenon/commit/34dd21465b6b9ee7ac747bb2723d8a402d299a03) est un contournement rapporté par les auteurs, pas une démonstration de la largeur du bus DMA. La limite des premiers 32 Mio reste à évaluer ; le masque 29 bits du candidat ne la garantit pas.

Les preuves publiques conservent les commits, dates, empreintes de différences et liens. Les réponses API brutes avec métadonnées d'identité restent dans `.local/`. Les recherches web générales ont surtout renvoyé des pages périphériques ; l'analyse utile vient des commits primaires et des pilotes.

## Correspondance avec le pilote SiS d'ALSA

Dans `sound/pci/intel8x0.c` de la source Linux épinglée, SiS7012 utilise les mêmes définitions de base qu'ICH, mais inverse les positions de SR et PICB et compte les données en octets. La correspondance suivante est une **hypothèse de famille de protocole**, pas l'identification du contrôleur Xbox comme un SiS7012 standard.

| Champ de la référence SiS | Offset dans un canal | Correspondance dans les sources Xenon |
|---|---:|---|
| Adresse de table BDBAR | +0x00 | Table de 32 descripteurs à deux mots |
| Index courant CIV | +0x04, bits 4:0 | `reg & 0x1f` |
| Dernier index LVI | +0x05, bits 4:0 | `(reg >> 8) & 0x1f` sur le mot à +4 |
| Compteur résiduel PICB | +0x06, 16 bits | `reg >> 16` sur le mot à +4 |
| Statut SR | +0x08, 16 bits | Bas du mot écrit `0x1c08001c` |
| Prélecture PIV | +0x0a | Octet contenant historiquement `0x08` |
| Contrôle CR | +0x0b | RUN/RESET aux bits 24/25 du mot à +8 |

Le banc compile les définitions réelles d'ALSA et confronte dix offsets/masques aux valeurs utilisées par Xenon. La constante de préparation contient en bas le masque des trois statuts et en haut le masque des trois activations d'interruption de la référence. Cette concordance oriente les prochaines lectures ; elle ne prouve pas les effets d'accès sur Xbox. En particulier, l'écriture historique de l'octet PIV, en lecture seule dans la référence, doit être expliquée avant de remplacer aveuglément tous les mots magiques.

## Fin de transfert et son effectivement sorti

La [documentation Intel ICH4, sections 14.2.4–14.2.7](https://www.intel.com/content/dam/www/public/us/en/documents/datasheets/82801db-io-controller-hub-4-datasheet.pdf) précise que LVBCI signale, en émission, la récupération du dernier tampon en mémoire, sans garantir sa transmission. PICB concerne également les accès mémoire. DCH décrit un arrêt pouvant avoir plusieurs causes ; CELV décrit un état, tandis que LVBCI est un événement mémorisé jusqu'à acquittement. Des bits de statut se nettoient en écrivant un. Ces définitions concernent ICH4 ; leur application à la Xbox reste une hypothèse à vérifier. Les tableaux des pages imprimées 484 et 486 ont été consultés avec leur rendu PDF.

**Conséquences pour notre conception, encore non mises en œuvre :**

- Une position mémoire peut permettre de libérer un tampon sans démontrer que la sortie audio est vide. Le drain final doit tenir compte du chemin situé après DMA ; sa profondeur et sa cadence restent inconnues ici.
- Un résiduel nul et des index égaux sont insuffisants pour reconnaître une nouvelle fin. Le banc appelle les deux fonctions LibXenon réelles sur 32 mots synthétiques : elles renvoient zéro restant et tout l'espace libre. Elles n'ont aucun historique permettant de distinguer un état initial équivalent d'une fin réelle.
- Un futur suivi doit contrôler l'état initial, la fraîcheur de l'événement et sa relation avec le dernier index publié. Une ancienne interruption mémorisée ne doit pas terminer une nouvelle soumission.
- Une lecture du mot à +8 suivie de sa réécriture avec RUN peut aussi acquitter des statuts si la sémantique SiS s'applique. Le candidat actuel conserve ce read-modify-write : il faut séparer contrôle et acquittement avant d'utiliser ces événements.
- Les activations d'interruption dans la constante historique doivent être conciliées avec le polling et l'absence de gestionnaire IRQ audio. La désactivation PCI INTx existante ne démontre pas le bon traitement des statuts internes.

Le correctif 0014 change uniquement la longueur et la géométrie de la table. Il **n'implémente pas** un nouveau décodeur de fin. Le refus de déduire le succès d'un zéro demeure ; le cas `stalled_final` doit encore produire une erreur de flux.

## Mesures dans le banc

La fonction `.prepare` réelle est exécutée avant et après correction, pour 512 tailles de tampon et 32 entrées chacune. Le banc vérifie adresses, longueurs, indicateur haut, absence de sortie d'allocation et sentinelles mémoire. Sous l'interprétation en octets littéraux :

| Mesure | Avant 0014 | Après 0014 |
|---|---:|---:|
| Descripteurs vérifiés | 16 384 | 16 384 |
| Longueurs non multiples d'une frame stéréo | 16 384 | 0 |
| Octets omis par anneau de 32 entrées | 32 | 0 |

Le total des déficits sur toutes les tailles vaut 16 384 octets ; ce n'est pas une quantité perdue dans un flux réel. La correction est cohérente avec l'historique LibXenon et le pilote SiS ; sa validation audio sur cette console manque encore. Quinze scénarios de l'adaptateur et vingt scénarios de ressources repassent avec ce candidat.

```sh
python3 research/tests/check-audio-descriptors.py \
  --previous APRES_0013/sound/pci/snd-xenon.c \
  --candidate APRES_0014/sound/pci/snd-xenon.c \
  --kernel SOURCE_LINUX --libxenon SOURCE_LIBXENON --output descriptors.json
```

Les sources épinglées sont Linux `a293dd19311668900eb1eeb2f6cb01dcac54f330` et LibXenon `a333adef440f28b436a667be0a4f014afce6349d`. Le rapport conserve les empreintes. ASan/UBSan ne signalent aucune erreur dans les exécutions finales. Une première extraction des macros a oublié un saut de ligne entre deux fragments ; l'échec de compilation du banc est conservé séparément.

## Construction et suite

Les deux constructions initiales terminent code zéro mais signalent un décalage d'horodatage inférieur à trois millisecondes sur les fichiers partagés Mac/Linux. Un second appel identique reproduit le problème : il ne suffit pas de relancer pour déclarer la chaîne fiable. La vérification suivante déplace le répertoire de sortie dans un volume Linux propre à ce projet, en conservant les sources en lecture seule et les mêmes options ; la copie finale est exportée seulement après fin de construction. Les commandes et diagnostics restent dans `evidence/2026-10-02/audio-protocol/`.

Les prochaines étapes sont la maîtrise des statuts/acquittements, une collecte audio ciblée préparée et réversible, puis la distinction mesurée entre consommation DMA et fin de sortie. Le dernier contrôle matériel reste E61 ; aucun chargement, redémarrage ou changement de la console pendant E62.

Résultat final : construction sur volume Linux terminée le 2 octobre à 11:09:56 UTC, code zéro, aucun avertissement. `6.18.11-xenon-audio-bytes`, noyau et 70 modules PowerPC vérifiés après export. Aucun initramfs, image XeLL, installation ou démarrage de ce candidat. Le succès final ne supprime pas les deux avertissements antérieurs conservés.
