# Licences et provenance

La licence MIT à la racine couvre les outils, tests et textes originaux du projet. Elle ne remplace pas les licences des sources amont, extraits, diffs et sorties dérivées.

- Les correctifs Linux 0001, 0003–0007 ciblent `techflashYT/linux-custom@a293dd19311668900eb1eeb2f6cb01dcac54f330`. Leurs parties dérivées du noyau restent sous GPL-2.0 ; texte dans `LICENSES/GPL-2.0.txt`. Les désassemblages conservés comme preuves proviennent de ce noyau, pas de jeux propriétaires.
- Les fonctions vidéo analysées viennent de Free60Project/libxenon au commit `a333adef440f28b436a667be0a4f014afce6349d`. Le code complet n'est pas embarqué ; le banc l'extrait de la copie amont locale. Notice BSD conservée dans `LICENSES/libxenon-BSD.txt`.
- Le correctif expérimental XeLL 0002 et les copies d'initramfs tierces restent hors de l'export public initial en attendant la vérification complète de leur provenance et de leur licence. Leur analyse reste documentée ; aucun firmware n'est distribué.
- Les outils peuvent analyser des fichiers fournis localement par l'opérateur. Cela ne donne aucun droit de redistribuer ces fichiers. Jeux, assets, exécutables propriétaires, images de disque, secrets et firmware restent hors de Git.
- Le parseur XEX2 est une implémentation originale de faits de format, confrontés à Xenia `95a5c3ee250f80c3b9d139658649d9ffb6db3eec` et Free60. Aucun code de décryption ou binaire Xenia n'est embarqué. La notice de licence de la référence Xenia est conservée dans `LICENSES/xenia-BSD.txt` à titre d'attribution.

- Le banc X11 reconstruit IceWM 4.0.0 (`5ebafddba37de22fc115d6cde43cb01cfc9ef263`) depuis son archive amont ; il n’embarque pas ce binaire dans Git. Les courts extraits de code dans les diagnostics du compilateur restent soumis à la licence amont GNU Library GPL version 2, dont la copie est conservée dans `LICENSES/icewm-LGPL-2.0.txt`. Ils ne sont pas couverts par la licence MIT des tests originaux.

Les auteurs amont conservent leurs droits. Les liens vers leurs dépôts et les révisions exactes sont dans `docs/SOURCES.md` et les rapports de provenance. Aucun composant amont n'est présenté comme une découverte ou une création originale d'OBSIDIAN-360.

Le correctif audio 0008 et les extraits de diagnostics de snd-xenon.c dérivent du pilote de jc4360 (2009), GPL-2.0-or-later, dans le même noyau linux-custom. La licence MIT ne remplace pas cette licence. Le banc extrait les fonctions de la copie source locale ; les routines amont ne sont pas recopiées dans le test.

Le correctif audio 0009 partage la provenance et la licence GPL-2.0-or-later de 0008. Les tests de ressources et leur modèle sont originaux ; les fonctions du pilote sont extraites à l’exécution de la copie source fournie.

Le correctif 0010 modifie le cœur SMC (GPL-2.0), son en-tête et le pilote audio (GPL-2.0-or-later). Le banc SMC extrait les macros iopoll (GPL-2.0-only) du noyau fourni à l’exécution ; il ne les redistribue pas comme code MIT. Les modèles et assertions sont originaux.

Le correctif 0011 conserve la provenance jc4360/linux-custom et la licence GPL-2.0-or-later du pilote audio. Le nouveau banc PCM et les adaptations des modèles sont originaux ; les callbacks amont sont extraits de la source locale à l’exécution.
