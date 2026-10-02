# Gel lors du redimensionnement — 2 octobre 2026

## Mesures et retour utilisateur

Après plus de neuf heures, Linux répond en SSH et aucun service systemd n’est en échec. Cela ne démontrait pas que le bureau répondait : son état manette était resté inchangé depuis la veille. XRandR expire, Xorg attend dans epoll et IceWM dans poll. L’utilisateur indique finalement que l’image est figée depuis une tentative de redimensionnement, avec pilotage à la manette. Son premier retour « le bureau réagit » est explicitement corrigé.

## Récupération effectuée

Le lanceur ne termine pas sur SIGTERM ; son arrêt forcé ne débloque pas XRandR. Le SIGHUP de redémarrage documenté d’IceWM ne suffit pas non plus. Après arrêt forcé de ce seul gestionnaire, icewm-session lance un nouveau processus : XRandR répond en 1280 × 720, Xorg et Linux restent en place. La session Linux n’a pas redémarré. Les anciens états de boutons synthétiques sont relâchés avant relance du lanceur. Ce dernier rouvre la manette et actualise son fichier d’état.

## Analyse du code et correction

Les préférences installées étaient `OpaqueMove=0` et `OpaqueResize=0`. Dans [IceWM 4.0.0, movesize.cc](https://github.com/ice-wm/icewm/blob/4.0.0/src/movesize.cc), `startMoveSize` choisit alors `outlineMove` ou `outlineResize`. Ce dernier garde `XGrabServer` pendant sa boucle d’attente d’événements. Les autres clients, dont la connexion XTest de notre pont manette, peuvent ainsi être bloqués pendant que le gestionnaire attend précisément leurs événements. Le comportement et la récupération observés concordent avec cette analyse ; la pile utilisateur originale n’a pas été acquise et le gel n’a pas été reproduit volontairement.

La correction de configuration active `OpaqueMove=1` et `OpaqueResize=1` : déplacement et redimensionnement directs, évitant ces branches de dessin du contour. Fragment réutilisable : `desktop/icewm-controller.conf`. Le fichier antérieur est sauvegardé sur la console sous `~/.icewm/preferences.before-resize-fix-20261002`. Le coût potentiel est davantage de rafraîchissements pendant le déplacement ; aucun gain de vitesse revendiqué. Aucune modification noyau, GPU ou micrologiciel.

La [documentation IceWM](https://ice-wm.org/man/icewm.html) décrit le SIGHUP ; celle de [icewm-session](https://ice-wm.org/man/icewm-session.html) décrit le redémarrage après crash. Les étapes et limites sont conservées dans `evidence/2026-10-02/desktop-recovery/`. Validation physique de redimensionnement demandée, encore en attente à ce relevé. La réécriture périodique du fichier d’état reste une optimisation possible du code, mais la mesure initiale sur un processus bloqué ne peut servir de référence de performance.
