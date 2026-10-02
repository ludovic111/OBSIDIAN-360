# Gel lors du redimensionnement — 2 octobre 2026

## Mesures et retour utilisateur

Après plus de neuf heures, Linux répond en SSH et aucun service systemd n’est en échec. Cela ne démontrait pas que le bureau répondait : son état manette était resté inchangé depuis la veille. XRandR expire, Xorg attend dans epoll et IceWM dans poll. L’utilisateur indique finalement que l’image est figée depuis une tentative de redimensionnement, avec pilotage à la manette. Son premier retour « le bureau réagit » est explicitement corrigé.

## Récupération effectuée

Le lanceur ne termine pas sur SIGTERM ; son arrêt forcé ne débloque pas XRandR. Le SIGHUP de redémarrage documenté d’IceWM ne suffit pas non plus. Après arrêt forcé de ce seul gestionnaire, icewm-session lance un nouveau processus : XRandR répond en 1280 × 720, Xorg et Linux restent en place. La session Linux n’a pas redémarré. Les anciens états de boutons synthétiques sont relâchés avant relance du lanceur. Ce dernier rouvre la manette et actualise son fichier d’état.

## Analyse du code et correction

Les préférences installées étaient `OpaqueMove=0` et `OpaqueResize=0`. Dans [IceWM 4.0.0, movesize.cc](https://github.com/ice-wm/icewm/blob/4.0.0/src/movesize.cc), `startMoveSize` choisit alors `outlineMove` ou `outlineResize`. Ce dernier garde `XGrabServer` pendant sa boucle d’attente d’événements. Les autres clients, dont la connexion XTest de notre pont manette, peuvent ainsi être bloqués pendant que le gestionnaire attend précisément leurs événements. Le comportement et la récupération observés concordent avec cette analyse ; la pile utilisateur originale n’a pas été acquise et le gel n’a pas été reproduit volontairement.

La correction de configuration active `OpaqueMove=1` et `OpaqueResize=1` : déplacement et redimensionnement directs, évitant ces branches de dessin du contour. Fragment réutilisable : `desktop/icewm-controller.conf`. Le fichier antérieur est sauvegardé sur la console sous `~/.icewm/preferences.before-resize-fix-20261002`. Le coût potentiel est davantage de rafraîchissements pendant le déplacement ; aucun gain de vitesse revendiqué. Aucune modification noyau, GPU ou micrologiciel.

La [documentation IceWM](https://ice-wm.org/man/icewm.html) décrit le SIGHUP ; celle de [icewm-session](https://ice-wm.org/man/icewm-session.html) décrit le redémarrage après crash. Les étapes et limites sont conservées dans `evidence/2026-10-02/desktop-recovery/`. Validation physique de redimensionnement demandée, encore en attente à ce relevé. La réécriture périodique du fichier d’état reste une optimisation possible du code, mais la mesure initiale sur un processus bloqué ne peut servir de référence de performance.

## Reproduction isolée du mécanisme (E47)

IceWM 4.0.0 a été recompilé depuis le commit `5ebafddba37de22fc115d6cde43cb01cfc9ef263` sur aarch64, puis testé dans deux serveurs Xvfb jetables. Le vrai lanceur du dépôt est lancé, et sa classe X11/XTest injecte les événements. L’initiation du redimensionnement utilise `_NET_WM_MOVERESIZE`, direction bas-droite, puis déplacement relatif et relâchement du bouton. Aucun accès à la Xbox pendant E47.

| Réglage | Requête du contrôleur après relâchement | Autre client X11 | Taille finale |
|---|---|---|---|
| OpaqueResize=0 | Expiration à 3 s | Expiration à 1 s | Impossible à interroger |
| OpaqueResize=1 | Réponse reçue | Réponse reçue | 1180 × 600 au lieu de 1240 × 640 |

Le mécanisme de blocage est désormais **reproduit hors console**, et le réglage l’évite dans ce scénario. Le premier essai, par coordonnées de bord supposées, n’avait provoqué aucun redimensionnement ; le test a correctement échoué malgré des processus répondants. Ce résultat rejeté est conservé dans `first-attempt.json`. Le test final exige à la fois la réduction effective des deux dimensions et la réponse d’un client indépendant.

Ce banc n’est ni une émulation PowerPC ni un test du GPU Xbox, du joystick physique ou de tous les types de déplacements. Xvfb utilise Xorg 21.1.7, contre 21.1.24 sur la console. La compilation amont contient des avertissements (fonctionnalités optionnelles, deux diagnostics GCC dans le gestionnaire de chaînes d’une applet réseau), et le thème de repli émet des avertissements de police ; ils sont conservés, sans conclure à un build amont entièrement sain. La configuration installée sur Xbox désactive l’applet réseau. La validation manuelle reste en attente. Reproduction détaillée : `docs/DESKTOP-TESTING.md`.
