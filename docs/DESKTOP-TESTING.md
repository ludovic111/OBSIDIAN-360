# Test du redimensionnement à la manette, hors console

Ce test reproduit un blocage X11 dans un conteneur Linux jetable. Il n’accède ni à la Xbox, ni aux périphériques d’entrée du Mac, ni à un serveur graphique existant. Il lance le vrai programme `desktop/xbox_desktop.py` et utilise sa classe X11 pour les événements synthétiques ; il ne simule pas les paquets du pilote joydev.

## Construire l’environnement

Prérequis : Docker actif, curl, environ 1 Go disponible pour l’environnement. Depuis la racine du dépôt :

```sh
mkdir -p .local/desktop-test-build .local/desktop-resize-tests
curl --fail --location \
  https://codeload.github.com/ice-wm/icewm/tar.gz/5ebafddba37de22fc115d6cde43cb01cfc9ef263 \
  --output .local/desktop-test-build/icewm-source.tar.gz
cp research/Dockerfile.desktop-test .local/desktop-test-build/Dockerfile
docker build -t obsidian360-desktop-test:icewm4 .local/desktop-test-build
```

Le Dockerfile vérifie le SHA-256 de l’archive avant extraction et compilation. Le contexte contient seulement le Dockerfile et cette archive amont. Ne pas utiliser le dépôt entier comme contexte : il contient des données privées ignorées par Git. Le binaire de test est aarch64 sur le Mac utilisé ici ; il n’est pas installé sur la Xbox. Le digest de base, l’identité d’image et les versions des paquets de l’essai sont dans `evidence/2026-10-02/desktop-resize-regression/environment.json`. Les paquets APT ne sont pas figés sur un snapshot ; une reconstruction bit à bit n’est pas garantie.

## Exécuter

```sh
docker run --rm --name obsidian-resize-regression \
  --network none --cpus 2 --memory 512m --pids-limit 128 \
  --mount "type=bind,source=$PWD/desktop,target=/workspace/desktop,readonly" \
  --mount "type=bind,source=$PWD/research/tests,target=/workspace/research/tests,readonly" \
  --mount "type=bind,source=$PWD/.local/desktop-resize-tests,target=/output" \
  obsidian360-desktop-test:icewm4 \
  python3 research/tests/check-desktop-resize.py --output /output/result.json
```

Chaque cas crée son propre Xvfb avec un numéro alloué par `-displayfd`, puis son propre IceWM et lanceur. La variable DISPLAY héritée est supprimée. Les connexions réseau X11 sont désactivées, et aucun socket X11 hôte n’est monté. Le nettoyage termine les groupes de processus créés ; l’arrêt forcé est intentionnel puisque l’ancien comportement doit se bloquer.

L’initiation du redimensionnement passe par le message standard `_NET_WM_MOVERESIZE` en direction bas-droite. La classe X11 réelle envoie ensuite un déplacement de −60/−40 et relâche le bouton. Le test attend une réponse synchrone sur cette connexion et interroge le serveur depuis un client indépendant. Il vérifie aussi la diminution réelle des dimensions : des processus vivants ou une simple réponse sans redimensionnement ne suffisent pas.

Résultat attendu : `passed: true`, ancien mode en expiration, nouveau mode réactif avec fenêtre réduite. Un code de sortie non nul ou un résultat incomplet est un échec à investiguer, pas une permission de déclarer le correctif validé.

## Preuves et limites

L’essai initial utilisant une position de bord supposée n’a provoqué aucun redimensionnement et a échoué. Il est conservé dans `first-attempt.json`. L’essai corrigé est `validation.json`. La compilation contient les avertissements documentés dans `build-diagnostics.log` ; les journaux de police et thème sont également conservés. Aucune compilation sans avertissement n’est revendiquée.

Le mécanisme de blocage est reproduit dans Xvfb, avec IceWM 4.0.0. Cela ne valide pas le GPU Xenos, le noyau PowerPC, l’entrée physique à la manette, tous les déplacements de fenêtre, ni le coût de rafraîchissement sur la console. Le test ne remplace pas l’essai manuel demandé à l’utilisateur.
