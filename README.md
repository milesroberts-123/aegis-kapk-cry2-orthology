# AEGIS CRY2 orthology analysis

## Goal

## General procedure

Downloaded orthology assignments between all species on Phytozome and Arabidopsis thaliana `resources/orthology`

Downloaded primary transcript proteomes from all species on Phytozome with unrestricted data usage `resources/proteomes`

Cross-checked these lists of species, keeping only the most recent assembly for species with more than one assembly

Kept all paralogs within a species deemed orthologous to CRY2

Aligned all orthologs with `mafft --linsi`

Plotted resulting alignments with ggmsa

## Summary

* 99 species, after deduplication, excluding species with missing proteome

* 107 assemblies, including a few extra assemblies in species with known high levels of within-species variation

* 153 genes in the CRY2 orthogroup, so some species have more than one CRY2 copy

