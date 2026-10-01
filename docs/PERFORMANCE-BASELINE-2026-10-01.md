# Première référence obsidian4 — E39

Mesures directes du 1 octobre à 21:50:15 UTC, après revérification SSH : noyau `6.18.11-xenon-obsidian4`, racine ext4 interne. Aucun paramètre changé, aucun paquet installé. Le bureau et SSH restent actifs pendant la mesure.

| Mesure | Valeur / portée |
|---|---|
| Fin du démarrage systemd | 34,129 s : 16,133 s classées « kernel » + 17,996 s userspace |
| Cible graphique | 34,125268 s depuis l'origine monotone, confirmé par propriété systemd |
| Premier /init | 3,157328 s dans dmesg |
| Montage racine ext4 | 14,262733 s dans dmesg |
| Mémoire totale exposée | 469 568 Kio = 458,5625 Mio |
| Mémoire disponible avant collecte | 121 344 Kio = 118,5 Mio |
| Swap utilisé avant collecte | 27 520 Kio ; zswap actif |
| Pages noyau | 65 536 octets |
| Topologie exposée | Six CPU logiques, fratries SMT 0–1, 2–3, 4–5 ; package_id -1, donc non renseigné |
| SHA-256, trois échantillons | Médiane 22,553 Mio/s ; plage 22,551–22,557 |
| Copie bytearray Python, trois échantillons | Médiane 136,225 Mio/s de données utiles ; plage 122,407–136,265 |

La durée systemd exclut le dashboard, le jeu et XeLL ; `graphical.target` ne mesure pas le premier bureau visible. L'intervalle d'environ 11,105 s entre /init et le montage racine inclut plusieurs étapes ; il ne peut pas être attribué entièrement à udev avec ce relevé. Le noyau annoncé à 3,2 GHz par cpuinfo n'est pas une mesure de fréquence instantanée.

La mémoire proportionnelle résidente (PSS) est de 22 625 Kio pour Xorg, 21 303 Kio pour IceWM, 2 141 Kio pour icewm-session et 22 440 Kio pour le processus Python préexistant PID 436. Le collecteur Python PID 708 ajoute 13 396 Kio : ne pas l'inclure dans le coût permanent du bureau. Xorg a aussi 10 304 Kio en swap. Les statistiques sont successives et non atomiques ; ne pas additionner naïvement les RSS partagées.

## Méthode et limites

Le script `tools/collect-baseline.py --workloads` lit proc/sysfs et des propriétés systemd. Le calcul utilise le fournisseur `_hashlib` installé (OpenSSL 3.6.3), un tampon de 8 Mio et quatre passages pour chacun des trois échantillons. Le résultat SHA-256 a été recomputé indépendamment sur le Mac. La copie inclut Python et ses allocations, et ne représente pas la bande passante RAM brute. Aucune affinité forcée, aucune modification de fréquence, aucun stress prolongé.

Les sondes hwmon passent de 55,484 / 49,542 / 53,285 / 28,082 °C à 55,507 / 49,503 / 53,238 / 28,054 °C. Cela décrit ce court essai uniquement ; aucune conclusion de stabilité thermique prolongée. Zéro service en échec après la collecte.

`systemd-analyze blame` et `critical-chain` ont chacun expiré après 12 secondes. Les erreurs sont conservées. Le suivi ciblé `tools/collect-boot-detail.py` obtient les timestamps des cibles ; il ne reconstitue pas toute la chaîne critique. Une première tentative de suivi a échoué car `/proc/slabinfo` n'existe pas ; le collecteur traite désormais cette interface comme facultative. `CONFIG_SLUB_DEBUG` est désactivé ; le fichier source exact `mm/slab_common.c` conditionne la création de slabinfo à cette option. Aucune reconstruction du noyau demandée pour ce relevé.

Preuves dans `evidence/2026-10-01/performance-baseline/` : rapport initial, suivi ciblé, empreintes des outils et échec intermédiaire. Reproduction depuis le Mac :

```sh
./tools/ssh-xbox 'python3 - --workloads' < tools/collect-baseline.py
./tools/ssh-xbox 'python3 -' < tools/collect-boot-detail.py
```

Prochaines comparaisons : décomposer l'attente initramfs, attribuer la mémoire noyau non récupérable, mesurer le coût du lanceur et du blit avec des méthodes isolant chaque composant. Pas encore de gain avant/après mesuré.
