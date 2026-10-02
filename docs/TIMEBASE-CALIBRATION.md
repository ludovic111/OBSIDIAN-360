# Horloge Xenon mesurée et correction optionnelle — E69/E70

## Mesure directe

Les horodatages console et Mac des expériences audio divergeaient d'environ 44 secondes. Sept échanges dans une session SSH persistante, sur environ 60 secondes, encadrent chaque lecture distante par deux horodatages monotones du Mac. Les allers-retours mesurés sont de 1,37 à 1,94 ms. Aucun réglage de date, fréquence, NTP ou matériel n'est modifié.

La console déclare `timebase` comme clocksource et **50 000 000 Hz** pour les trois propriétés timebase-frequency du device tree vivant. Pendant 60,0354 à 60,0384 secondes du Mac, CLOCK_MONOTONIC_RAW console avance de 59,8864 secondes. Le rapport encadré est 0,9974687 à 0,9975187 : environ **−0,25 %**, soit un retard calculé proche de neuf secondes par heure si ce taux reste constant. Les horloges monotone et civile présentent un rapport voisin pendant cette minute.

En prenant le Mac comme référence, la fréquence effective compatible avec les bornes d'échange est **49 873 437 à 49 875 933 Hz**. Ce n'est pas une mesure électrique de l'oscillateur ni un étalonnage absolu du Mac. La valeur **49 875 000 Hz** est contenue dans cet intervalle et correspond exactement à la formule de [LibXenon épinglé](https://github.com/Free60Project/libxenon/blob/a333adef440f28b436a667be0a4f014afce6349d/libxenon/drivers/ppc/timebase.h). Fichier local comparé à l'API GitHub, empreinte identique ; le premier accès web brut avait échoué sans résultat exploitable.

Un contrôle ultérieur de timedatectl déclare CanNTP=yes, NTP=yes et NTPSynchronized=yes. Ces indicateurs n'annulent pas l'écart et la dérive mesurés ; le statut affiché ne suffit donc pas comme vérification d'exactitude. CLOCK_MONOTONIC_RAW et la comparaison au Mac restent les preuves utilisées ici. Aucun réglage NTP n'a été changé.

La différence de date à la fin du relevé est entre −44,2806 et −44,2789 secondes, console moins Mac. Les anciennes captures conservent leurs horodatages originaux : ne pas corriger rétroactivement toutes les observations à partir d'un seul écart mesuré. Pour corréler les preuves, préciser la machine qui fournit l'heure et utiliser l'uptime/les compteurs monotones. Les durées de performances historiques peuvent être affectées ; leur correction exacte reste à vérifier sur le noyau et le démarrage concernés.

Preuves : `evidence/2026-10-02/clock-calibration/`. Le relevé court collector-smoke valide le nouvel outil ; sa durée de deux secondes ne remplace pas la mesure principale de 60 secondes. Sept tests hors console vérifient les bornes sur un taux synthétique connu et rejettent les relevés incomplets ou mal ordonnés.

## Analyse du chemin logiciel

Le code Xenon utilise generic_calibrate_decr, qui lit timebase-frequency dans le device tree. Le DTS de la source noyau et celui de XeLL consultés contiennent 50 MHz. L'image zImage.xenon construite ici est une conversion ELF du noyau ; sa recette n'embarque pas automatiquement le DTS voisin. Modifier seulement ce fichier DTS n'aurait donc pas démontré une correction du démarrage réel.

Le setup initial loops_per_jiffy=50000000 est une estimation transitoire, distincte de ppc_tb_freq : ne pas modifier cette constante comme s'il s'agissait de la conversion de l'horloge.

## Candidat logiciel — pas encore démarré

Le correctif indépendant **0016** ajoute l'option précoce `xenon_tb_hz=49875000`. Sans option, la calibration du firmware est conservée. L'alternative `xenon_tb_hz=50000000` permet de comparer explicitement la valeur nominale ; les autres valeurs sont refusées. L'option est analysée avant time_init. La fonction Xenon appelle d'abord generic_calibrate_decr puis remplace ppc_tb_freq, en journalisant la valeur firmware et celle retenue.

Cette option change le facteur logiciel utilisé pour convertir les ticks ; elle ne programme ni PLL, ni tension, ni oscillateur. Elle est optionnelle car une mesure d'un seul exemplaire ne caractérise pas toutes les révisions. La fréquence CPU publiée séparément par le firmware n'est pas recalibrée par ce correctif.

À partir des objets et de la configuration du noyau obsidian4 éprouvé, un volume Linux distinct a produit **6.18.11-xenon-obsidian-clock**, son image XeLL et **65 modules**. Les trois constructions ont terminé code 0 sans avertissement. Formats ELF, six sections de charge utile, vermagic de tous les modules, présence de l'option et des symboles de calibration vérifiés. Reconstruction du patch identique au candidat. Les correctifs audio expérimentaux ne sont pas inclus dans ce noyau.

Il reste à préparer son initramfs et une entrée USB optionnelle, puis à coordonner un démarrage physique et refaire le relevé. Le noyau et l'image restent sur le Mac ; **aucune correction de cadence n'est installée ou mesurée en fonctionnement**. Ni synchronisation de l'heure civile ni test de charge n'est revendiqué.

## Reproduction

Lecture standard sur la console via la configuration SSH privée existante :

```sh
python3 tools/measure-clock-drift.py --samples 7 --interval 10 \
  --output .local/clock-observation-new.json
```

Analyse hors console d'une capture existante :

```sh
python3 tools/measure-clock-drift.py \
  --analyze evidence/2026-10-02/clock-calibration/samples.json \
  --output .local/clock-analysis-new.json
python3 research/tests/check-clock-analysis.py
```

Les chemins de sortie doivent être nouveaux pour préserver les preuves. Les commandes de construction exactes, sources et empreintes sont dans timebase-build/build.json, reconstruction.json et clock-calibration/sources.json. Pour un futur test, garder obsidian4 et linux_hdd comme solutions de retour, puis vérifier l'option effectivement présente dans /proc/cmdline et la fréquence retenue dans le journal du noyau.

## Préparation ultérieure E71

Le candidat est désormais préparé sur le disque et la clé avec initramfs vérifié et entrée distincte **obsidian_clock**. Aucun démarrage encore constaté ; voir [TIMEBASE-BOOT.md](TIMEBASE-BOOT.md) pour les preuves, le test demandé et le retour à obsidian4.
