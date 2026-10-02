# File PCM originale — composant logiciel, E59

`pcm_queue.c` et `pcm_queue.h` sont un composant original sous MIT destiné au remplacement de la soumission audio historique. Ils ne constituent pas un pilote. Depuis E60, le correctif 0013 les intègre au candidat `snd-xenon`, sans activation matérielle ; voir `docs/AUDIO-ALSA-ADAPTER.md`. Aucun accès matériel, allocation, copie de son, barrière ou verrou n’est effectué ici.

Le composant conserve séparément la fin des données engagées, les blocs publiables, la portion incomplète, la consommation physique et la consommation logique. La taille est comprise entre 128 et 65 536 octets par pas de 128 ; le modèle utilise 32 blocs égaux et des frames de quatre octets. Chaque instance représente un flux et doit être protégée par le verrou de son appelant.

## API et plans

| Fonction | Effet logiciel |
|---|---|
| `obs_audio_queue_init` | Initialise une file vide, avec positions à zéro |
| `obs_audio_queue_push` | Accepte des frames déjà copiées dans le tampon ; annonce uniquement les nouveaux blocs complets |
| `obs_audio_queue_drain` | Ferme la file aux nouveaux ajouts et prépare, si nécessaire, le remplissage silencieux du dernier bloc |
| `obs_audio_queue_consume` | Enregistre une consommation physique de blocs dont l’adaptateur a préalablement vérifié l’achèvement |
| `obs_audio_forward_delta` | Calcule un avancement de compteur en frames, avec retour circulaire et rejet des reculs/sauts hors capacité |

Un plan contient un indicateur de publication, un index de dernier bloc et une éventuelle plage à mettre à zéro. Un plan sans publication ne doit pas produire d’écriture d’index. Un tampon complet produit bien une publication, même lorsque son index final revient à la valeur circulaire précédente.

La partie incomplète reste engagée mais non publiée. Lors du drain, sa plage restante est mise à zéro dans le plan, puis le dernier bloc devient publiable. L’adaptateur doit **réaliser ce remplissage puis la barrière DMA avant de publier**. Le composant ne les effectue pas. Aucun échantillon déjà engagé ne figure dans la plage à effacer ; celle-ci reste dans l’allocation.

Le remplissage final compte dans les octets consommés par le matériel, mais pas dans les octets logiques retournés à ALSA. À la taille maximale, le silence ajouté peut représenter 2 044 octets, soit environ 10,646 ms au débit attendu de 192 000 octets/s. C’est une limite calculée, pas une mesure de latence.

Toutes les erreurs laissent l’état et les arguments de sortie inchangés. L’ajout après drain est refusé ; un nouveau flux nécessite une nouvelle initialisation. Les appels répétés de drain sont idempotents. L’appelant fournit des objets valides, distincts et non concurrents ; la validation interne des invariants ne protège pas contre un pointeur mémoire arbitraire.

`obs_audio_forward_delta` accepte les limites 64 bits sans multiplier le compteur complet. Seul le delta borné, au plus 16 384 frames, pourra ensuite être converti en octets. Le reset ALSA et le recalage d’un flux en cours doivent être traités par l’adaptateur ; ils ne sont pas implicitement devinés par cette fonction.

## Tests et compilation

Depuis la racine du dépôt :

```sh
python3 research/tests/check-audio-queue.py --output queue-validation.json
clang --analyze -std=c11 -Wall -Wextra -Werror research/audio/pcm_queue.c
clang --target=powerpc64-linux-gnu -ffreestanding -std=c11 -O2 -Wall -Wextra -Werror -c research/audio/pcm_queue.c -o pcm_queue.o
```

Le dernier contrôle a été exécuté avec LLVM 16 dans l’environnement de construction du projet. Les tests hôtes emploient Clang, ASan et UBSan. LeakSanitizer est désactivé sur ce Mac où il n’est pas pris en charge ; son premier refus est conservé comme échec d’outillage, avant toute exécution des cas.

Le banc produit des frames synthétiques numérotées, garde une file de référence indépendante et compare le contenu réellement consommé, y compris les zéros de fin. Il teste les 512 tailles possibles, les tampons pleins, un seul échantillon final, les refus avec état inchangé et 44 800 étapes déterministes de remplissage/consommation sur deux files entrelacées. Cela représente 54 008 opérations et 24 544 033 frames logiques comparées au relevé. Les slots occupés ne peuvent pas être publiés à nouveau avant consommation dans ce modèle.

Un module de liaison minimal a aussi été construit contre les en-têtes/configuration `6.18.11-xenon-audio-poll`. Il contient ces deux sources et un fichier ne déclarant que `MODULE_LICENSE("Dual MIT/GPL")` et une description. Il ne fournit ni init matériel ni pilote PCI. Les cinq fonctions, le format ELF64 PowerPC big-endian et le vermagic sont vérifiés. Aucun module chargé. Recette de liaison :

```make
obj-m += obsidian_pcm_queue.o
obsidian_pcm_queue-y := pcm_queue.o build_check.o
```

Puis `make -C SOURCE O=BUILD M=MODULE ARCH=powerpc LLVM=1 LOCALVERSION=-audio-poll modules`, avec les fichiers du noyau montés en lecture seule dans le contrôle réalisé. Ce test confirme la compilation avec `__KERNEL__` et la liaison ; ce n’est pas une intégration ALSA.

## Conditions avant intégration matérielle

Le modèle suppose des blocs consommés en ordre et une publication du dernier bloc valide. Il ne démontre ni les bits du registre, ni l’encodage de longueur, ni la fin effective d’un bloc, ni l’absence de prélecture DMA. Le pilote devra traduire les registres en consommations vérifiées et ne jamais prendre une position modulo inchangée pour la preuve d’une file vide.

L’adaptateur devra ensuite relier `.ack`, START, DRAIN, `.pointer`, les callbacks de suivi et les resets du cœur ALSA ; propager correctement les erreurs/rollback ; et respecter l’ordre entre remplissage, barrière et publication. E60 remplace les publications depuis pointer par un adaptateur testé hors console. La fin du dernier bloc reste non décodée, ce qui bloque une validation matérielle du drain et de l’audio.

Preuves : `evidence/2026-10-02/audio-queue/`. Dernier état matériel inchangé : E56 ; aucune interaction Xbox durant E59.

E60 : le paramètre `current` devient `position` pour éviter sa collision avec une macro du noyau dans la compilation intégrée. Algorithme inchangé et banc complet réexécuté.
