---
layout: distill
title: INTER 2025
date: 2025-06-08 8:00:00-0400
# date: 2025-06-11 8:00:00-0400
description: FAIRSET pour l'évaluation d'IA de détection de repères de visages

authors:
    - name: Ian-Mathieu Joly, Nikola Zelovic, Eléonor Riesco, Karina Lebel
      affiliations:
        name: Université de Sherbrooke, Faculté de génie
        name: Université de Sherbrooke, Faculté des sciences de l'activité physique

bibliography: papers.bib

img: assets/img/sigmo-logo-S-square.png
importance: 1
category: posters
related_publications: false
---

# FAIRSET pour l'évaluation des biais démographiques d'IA de détection de repères sur le visage <a href="https://event.fourwaves.com/fr/inter2025/resumes/70ef94e2-94a0-47ae-9ff6-0932dd16b325" target="_blank" rel="noopener noreferrer" class="btn z-depth-0 btn-pdf">PDF</a>

<div id="fairset-bd" class="row justify-content-sm-center">
    <div class="col-sm mt-1 mt-md-0">
        {% include figure.liquid path="assets/img/bd-fairset.png" title="FAIRSET" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>

## Introduction
Plusieurs études ont été effectuées afin d'évaluer l'existance de biais dans les modèles d'intelligence artificielle par apprentissage profond. À cet effet, dans le cas des IA de détection dans des images, la majorité des biais démographiques répertoriés touche le sexe, la couleur de peau et l'âge des individus <d-cite key="buolamwini_gender_2018"></d-cite><d-cite key="hazirbas_towards_2021"></d-cite><d-cite key="khalil_investigating_2020"></d-cite><d-cite key="menezes_bias_2021"></d-cite>. Toutefois, l'existance de ces biais dans les modèles de détection de repères de visages n'est pas connue. Les algorithmes de placement de repères de visage « face landmark detection » (FLD) sont des algorithmes servant à annoter certains points clés sur le visage des différentes personnes dans une image.

<div class="row justify-content-sm-center">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/face-landmark-detection-steps.png" title="Face Landmarks Detection Steps" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    <b>Figure 1)</b> Étapes de détection des repères de visages d'un individu <d-cite key="yang_enhancing_2022"></d-cite>
</div>

Ces types d'algorithmes sont couramment utilisés dans des contextes de divertissement, mais aussi dans des contextes plus critiques comme des études médicales. Cependant, dans ces tâches plus difficiles, leurs lacunes commencent à être apparentes. Il est bien documenté que des facteurs environnementaux, tels que les occlusions ou le mauvais éclairage, peuvent engendrer une perte de précision. En plus, pour certains algorithmes similaires, un lien significatif a été observé entre la qualité des résultats et certains facteurs démographiques, comme l'âge, le sexe et la couleur de peau. Les algorithmes modernes de FLD sont en fait des réseaux de neurones, dont la source de données d'apprentissage peut grandement influencer les biais des models.

Cependant, ces biais en lien avec les démographies n'a pas été validé pour les algorithmes de « face landmarking ». Alors, à notre connaissance, il n'y a pas de moyens actuels pour déterminer si ce lien existe pour ces algorithmes spécifiques, mais surtout de valider si un algorithme envisagé présente certains biais.

Comme résultat, nous avons développé le jeu de données FAIRSET afin de valider ces biais. (ajouter explication FAIRSET + graphiques que tu veux mettre)

Par la suite, nous avons été capables de conduire une analyse statistique afin de valider si les algorithmes de "face landmarking" présentent bel et bien des biais démographiques. Les algorithmes Mediapipe FaceMeshV2, 3DDFAv3 et OpenFace2 ont été choisis pour leur popularité. La métrique utilisée pour cette étude était la NME (Normalized Mean Error), soit l'erreur de placement normalisée par la distance entre les coins externes des yeux de la personne.
(Mettre image NME poster)
Pour débuter, les statistiques descriptives ont été extraites et présentées dans les graphiques ci-dessous.
(mettre boxplots)
De ces résultats, on voit qu'OpenFace2 performe significativement moins bien que les deux autres, ce qui n'est pas surprenant puisqu’il est plus âgé que les deux autres algorithmes. De plus, on peut observer que les médianes sont relativement similaires entre les différentes démographies, mais que la variance varie. Alors, des analyses subséquentes étaient requises pour pousser l'analyse. Une ANOVA pour les facteurs d'âge et de couleur de peau, puis un t-test pour le sexe. Les nombres de points statistiquement affectés (p < 0.05) par les différents facteurs démographiques sont présentés dans le tableau ci-dessous.
(mettre tableau anova)
On peut donc voir que pour certains points, pour tous les algorithmes, un lien statistique semble exister entre la démographie des personnes et les résultats. Afin de voir quelles démographies spécifiques impactent les résultats, une analyse post-hoc de Tukey a été conduite pour l'âge et la couleur de peau, puis les résultats du t-test ont été analysés pour le sexe.
(mettre post-hoc)
Les tableaux ci-dessus présentent l'augmentation moyenne de la NME pour les points significativement impactés par le facteur démographique par rapport à la moyenne globale de l'algorithme. En d'autres mots, ils démontrent à quel point les différents groupes démographiques impactent les résultats.
En conclusion, (mettre mini conclusion dataset). Au niveau de l'analyse, on a conclu qu'un lien existe entre les facteurs démographiques de sexe et d'âge, avec une augmentation de l'erreur allant jusqu'à 48 %. Cependant, comme FAIRSET n'est pas balancé dans les différentes couleurs de peau et que l'analyse a montré moins de points impactés, plus d'analyses sont requises pour tisser un lien définitif pour ce facteur.
