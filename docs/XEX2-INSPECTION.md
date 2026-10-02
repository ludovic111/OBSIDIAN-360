# Première brique d'analyse des jeux : XEX2 — E41

Analyse de sources et essais synthétiques sur le Mac. Aucun fichier de jeu, accès matériel ou dump de console dans cette expérience.

## Sources et arbitrage

Référence principale : Xenia au commit `95a5c3ee250f80c3b9d139658649d9ffb6db3eec`, notamment [les structures XEX2](https://github.com/xenia-project/xenia/blob/95a5c3ee250f80c3b9d139658649d9ffb6db3eec/src/xenia/kernel/util/xex2_info.h) et [GetOptHeader / chargement](https://github.com/xenia-project/xenia/blob/95a5c3ee250f80c3b9d139658649d9ffb6db3eec/src/xenia/cpu/xex_module.cc). Copie source conservée hors Git ; URLs et empreintes dans `evidence/2026-10-02/xex-inspect/sources.json`. Ce code d'émulateur est une référence d'implémentation, pas une mesure de cet exemplaire Xbox.

La [page historique Free60](https://free60.org/System-Software/Formats/XEX/) confirme l'en-tête de 24 octets en big-endian et la table d'entrées. Sa formulation sur l'octet bas des clés est incomplète pour zéro. Xenia distingue explicitement zéro (valeur directe), un (mot dans l'entrée) et les autres cas (offset externe). Le parseur respecte cette distinction ; interpréter une adresse d'entrée comme un offset de fichier produirait un faux rejet.

## Contrat de lecture

| Zone | Interprétation retenue |
|---|---|
| 0x00 | Magic XEX2 |
| 0x04 | Flags du module |
| 0x08 | Fin des en-têtes / début du corps d'image |
| 0x0c | Valeur réservée, conservée |
| 0x10 | Offset du bloc de sécurité |
| 0x14 | Nombre d'entrées optionnelles |
| 0x18 et suivantes | Paires clé / valeur ou offset |

Pour une entrée externe, les codes de taille 2 à 254 indiquent des mots de quatre octets ; 255 fait lire une longueur dans le bloc. Le corps de l'image peut être empaqueté : son offset ne garantit pas la présence immédiate d'une signature PE lisible. Les modes de compression/chiffrement sont donc rapportés sans extraction.

Le bloc de sécurité est seulement borné : dimensions et nombre de descripteurs. Les signatures, identifiants sensibles et clés ne sont pas interprétés ni copiés. L'inspecteur n'établit aucun verdict d'authenticité. Les propriétés plus strictes choisies pour refuser chevauchements/doublons sont documentées comme politique locale, pas comme règle universelle démontrée.

## Implémentation et preuve

`game-analysis/xex-inspect` est une bibliothèque Rust avec CLI, sans crate externe et avec interdiction de code unsafe. Les nombres sont décodés depuis des octets, sans convertir des structures natives. Les additions de plage utilisent u64 et un contrôle de débordement ; le nombre d'entrées est plafonné. Une erreur ne produit pas de rapport JSON partiel.

Les dix tests Rust passent, dont 10 000 mutations déterministes et toutes les troncatures de l'échantillon avant son offset d'image. Un lecteur instrumenté interdit l'accès aux zones opaques et compte 108 octets lus sur cet échantillon de 1 040 octets. Les neuf cas CLI passent ; le contenu du fichier reste identique et les sorties ne révèlent pas le chemin fourni. Clippy sans avertissement, formatage et compilation release passent. Preuves et empreintes dans `xex-inspect/validation.json`.

Ce composant modernise l'outillage d'analyse ; il ne remplace aucun firmware ou pilote de la console et ne démontre pas de gain de performance. Il reste à éprouver la compatibilité sur des échantillons légitimes, documenter les imports et les images PE disponibles, puis relier les instructions aux appels système et au déroulement d'une frame. Ni désassemblage de jeu, ni analyse de shader, ni réparation du lecteur ne sont réalisés par E41.
