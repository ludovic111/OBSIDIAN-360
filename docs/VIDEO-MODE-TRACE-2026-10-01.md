# Trace des modes vidéo — E37

Analyse du code hors console, sans nouvel accès matériel. Source locale libxenon au commit `a333adef440f28b436a667be0a4f014afce6349d`, fichiers `drivers/xenos/xenos.c`, `xenos.h`, `xenos_videomodesdata.h` et `include/xetypes.h`. Leurs empreintes figurent dans le rapport.

## Méthode et résultat

`tools/trace-video-modes.py` extrait sans modification les fonctions `xenos_set_mode_f1` et `xenos_set_mode_f2`, inclut les tables originales et les compile sur le Mac avec ASan/UBSan. Les écritures deviennent des lignes de trace ; la seule lecture attendue simule explicitement la fin du remplissage de LUT. Le banc borne le nombre d'accès et interrompt tout accès inattendu. Il n'émule ni le GPU, ni l'ordonnancement physique, ni les horloges.

Les deux familles de 13 modes ont produit chacune 71 écritures par entrée, soit 1 846 écritures au total, sans diagnostic du compilateur ou des sanitizers. Aucune entrée ne contient une largeur de 1920 pixels. Preuve : `evidence/2026-10-01/video-mode-trace/modes.json`.

Pour HDMI 720p, treize des quinze registres de l'ancienne capture sont écrits par ces deux fonctions. Douze valeurs concordent ; l'adresse du framebuffer diffère (`0x1e000000` dans libxenon, `0x04000000` dans la capture Linux). Le pilote Linux programme lui-même cette adresse à partir de son allocation DMA : cette différence est compatible avec la prise en charge par Linux, sans reconstituer le déroulement temporel exact.

Les registres `0x6024` et `0x652c` ne sont pas écrits dans ce sous-ensemble de fonctions : aucun verdict d'égalité ne leur est attribué. Le standard et la famille Corona donnent les mêmes résultats f1/f2 en HDMI 720p ; ces traces ne permettent donc pas d'identifier la carte mère.

## Conséquences pour le 1080p

Le code écrit `total_height - 1` à `0x6010`, malgré le nom de macro `D1CRTC_H_SYNC_B`, et zéro à `0x6020`, nommé `D1CRTC_V_TOTAL`. Un décodage fondé uniquement sur les noms des macros serait trompeur. Pour le mode 720p tracé, les totaux sont 1650 × 750 ; le total vertical calculé n'est pas une mesure, car l'ancienne capture ne contient pas `0x6010`.

Le pilote Linux installé impose un mode DRM 1280 × 720. Son activation programme l'adresse et l'activation du framebuffer ; elle ne remplace pas la séquence HDMI/ANA. Ajouter une résolution DRM ou augmenter seulement l'allocation ne règle pas le signal de sortie.

La suite utile consiste à analyser séparément la programmation ANA/HANA et les horloges, puis à fournir un mode complet au chargeur et au pilote. Une table 1920 × 1080 inventée à partir de simples dimensions n'est pas une expérience prête à déployer. Il faut également conserver la disposition en tuiles, le pitch et la mémoire réservée cohérents. Aucun mode 1080p n'a été installé ou testé par E37.

## Reproduction

```sh
python3 tools/trace-video-modes.py \
  --source-dir .local/upstream/libxenon/libxenon/drivers/xenos \
  --capture evidence/2026-10-01/gpu-display-registers.json \
  --output .local/video-trace-recheck.json
```

La première tentative du banc manquait l'en-tête xetypes ; il est maintenant inclus avec son empreinte. Une erreur de découpage des noms de mode contenant des espaces a ensuite été corrigée avant production du rapport. Les résultats publiés proviennent de l'exécution terminée avec succès. La source libxenon n'est toujours pas démontrée identique au binaire XeLL réellement lancé.
