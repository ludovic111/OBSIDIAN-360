# obsidian-xex-inspect

Inspecteur XEX2 en Rust, en lecture seule, sans dépendance externe ni code `unsafe`. Il fonctionne sur l'hôte et ne se connecte pas à la console. Les tests n'utilisent aucun jeu : leurs échantillons sont construits en mémoire ou dans un répertoire temporaire.

```sh
cargo test --offline --manifest-path game-analysis/xex-inspect/Cargo.toml
cargo clippy --offline --manifest-path game-analysis/xex-inspect/Cargo.toml --all-targets -- -D warnings
cargo build --offline --release --manifest-path game-analysis/xex-inspect/Cargo.toml
python3 game-analysis/xex-inspect/tests/check_cli.py --binary game-analysis/xex-inspect/target/release/obsidian-xex-inspect
game-analysis/xex-inspect/target/release/obsidian-xex-inspect CHEMIN_LOCAL_DU_FICHIER
```

Rust 1.99.0 a été utilisé sur le Mac ; aucune compilation PowerPC ni comparaison de performances n'est revendiquée. Le chemin en capitales est à remplacer par un fichier régulier local obtenu légitimement. Conserver ce fichier hors Git. Le programme écrit le JSON sur stdout, les erreurs sur stderr, code 0 en cas de contrôle structurel réussi et 2 en cas d'erreur.

## Ce qui est inspecté

En-tête principal, entrées optionnelles directes/fixes/variables, dimensions déclarées du bloc de sécurité, compte des descripteurs de pages, types de compression/chiffrement et métadonnées d'exécution si présentes. Les octets sont décodés explicitement en big-endian ; la taille du fichier provient du descripteur ouvert.

Les lectures utilisent des offsets contrôlés et de petits tableaux fixes. Aucune allocation ne dépend d'une taille de payload déclarée ; les collections sont plafonnées à 4 096 entrées. Les doublons, chevauchements de blocs optionnels, alias vers les données de sécurité et plages sortant des en-têtes sont refusés. Ce sont aussi des choix conservateurs de l'inspecteur, pas une preuve que toute variante légitime partage cette politique.

Les champs inconnus restent descriptifs. Aucun contenu brut de bloc externe, clé LAN, signature, clé de chiffrement ou corps de programme n'est imprimé. Les tests de lecture instrumentée vérifient que les zones opaques de leur échantillon ne sont pas lues. Une exécution concurrente modifiant le fichier pendant l'inspection n'est pas prise en charge : travailler sur une copie locale stable.

## Limites

`structural_check: passed` ne signifie ni signature valide, ni fichier complet exécutable, ni jeu compatible. Les signatures, descripteurs individuels, imports, image PE, shaders et assets ne sont pas validés. XEX1 est explicitement refusé. Les types de compression/chiffrement inconnus sont conservés sous forme numérique ; aucune décompression ou décryption n'est effectuée.

Dix tests Rust couvrent notamment 1 024 troncatures et 10 000 mutations déterministes, puis neuf cas CLI vérifient erreurs et invariance de l'entrée. Aucun véritable exécutable de jeu n'a encore validé la compatibilité de ce parseur. Les mutations ne sont pas du fuzzing guidé par couverture.

Les sources primaires et la portée de l'analyse figurent dans [le dossier XEX2](../../docs/XEX2-INSPECTION.md). Implémentation originale sous MIT ; faits de format confrontés aux sources Xenia et à la documentation historique Free60.
