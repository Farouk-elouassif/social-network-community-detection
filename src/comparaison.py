# -*- coding: utf-8 -*-
"""
Module de comparaison des algorithmes Louvain et Girvan-Newman.
Compare les performances et résultats des deux algorithmes.
"""

import time
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.graphe import charger_graphe_complet
from src.louvain import executer_louvain
from src.girvan_newman import executer_girvan_newman


def mesurer_temps(fonction, *args):
    """
    Mesure le temps d'exécution d'une fonction.
    
    Retourne: (résultat, temps_en_secondes)
    """
    debut = time.time()
    resultat = fonction(*args)
    fin = time.time()
    temps = fin - debut
    return resultat, temps


def comparer_algorithmes(G, k=None):
    """
    Compare Louvain et Girvan-Newman sur le même graphe.
    
    Arguments:
        G: le graphe à analyser
        k: nombre de communautés pour Girvan-Newman (optionnel)
    
    Retourne un dictionnaire avec les résultats
    """
    resultats = {}
    
    # === Louvain ===
    print("\n" + "="*60)
    print("          ALGORITHME DE LOUVAIN")
    print("="*60)
    
    (partition_l, mod_l, comm_l), temps_l = mesurer_temps(executer_louvain, G)
    
    resultats['louvain'] = {
        'partition': partition_l,
        'modularite': mod_l,
        'communautes': comm_l,
        'nb_communautes': len(comm_l),
        'temps': temps_l
    }
    
    # === Girvan-Newman ===
    print("\n" + "="*60)
    print("          ALGORITHME DE GIRVAN-NEWMAN")
    print("="*60)
    
    (partition_gn, mod_gn, comm_gn), temps_gn = mesurer_temps(executer_girvan_newman, G, k)
    
    resultats['girvan_newman'] = {
        'partition': partition_gn,
        'modularite': mod_gn,
        'communautes': comm_gn,
        'nb_communautes': len(comm_gn),
        'temps': temps_gn
    }
    
    return resultats


def calculer_taille_moyenne(communautes):
    """
    Calcule la taille moyenne des communautés.
    """
    if len(communautes) == 0:
        return 0
    total = sum(len(c) for c in communautes)
    return total / len(communautes)


def afficher_comparaison(resultats):
    """
    Affiche un tableau comparatif des deux algorithmes.
    """
    louvain = resultats['louvain']
    gn = resultats['girvan_newman']
    
    # Calculer les tailles moyennes
    taille_l = calculer_taille_moyenne(louvain['communautes'])
    taille_gn = calculer_taille_moyenne(gn['communautes'])
    
    print("\n")
    print("="*70)
    print("                    COMPARAISON DES ALGORITHMES")
    print("="*70)
    print()
    print(f"  {'Métrique':<30} {'Louvain':>15} {'Girvan-Newman':>15}")
    print("  " + "-"*60)
    print(f"  {'Complexité':<30} {'O(n log n)':>15} {'O(m²n)':>15}")
    print(f"  {'Modularité':<30} {louvain['modularite']:>15.4f} {gn['modularite']:>15.4f}")
    print(f"  {'Nombre de communautés':<30} {louvain['nb_communautes']:>15} {gn['nb_communautes']:>15}")
    print(f"  {'Taille moyenne':<30} {taille_l:>15.1f} {taille_gn:>15.1f}")
    print(f"  {'Temps exécution (s)':<30} {louvain['temps']:>15.4f} {gn['temps']:>15.4f}")
    print("  " + "-"*60)
    print()
    print("  n = nombre de noeuds, m = nombre d'arêtes")
    print("  " + "-"*60)
    
    # Déterminer le meilleur
    print()
    print("  ANALYSE:")
    print("  " + "-"*60)
    
    # Meilleure modularité
    if louvain['modularite'] > gn['modularite']:
        print("  ✓ Louvain a une meilleure modularité")
    elif gn['modularite'] > louvain['modularite']:
        print("  ✓ Girvan-Newman a une meilleure modularité")
    else:
        print("  = Modularité identique")
    
    # Plus rapide
    if louvain['temps'] < gn['temps']:
        ratio = gn['temps'] / louvain['temps']
        print(f"  ✓ Louvain est {ratio:.1f}x plus rapide")
    else:
        ratio = louvain['temps'] / gn['temps']
        print(f"  ✓ Girvan-Newman est {ratio:.1f}x plus rapide")
    
    print("="*70)
    
    return resultats


def executer_comparaison(G, k=None):
    """
    Fonction principale: compare les algorithmes et affiche les résultats.
    """
    resultats = comparer_algorithmes(G, k)
    afficher_comparaison(resultats)
    return resultats


# === Test du module ===
if __name__ == "__main__":
    # Chemin vers les données
    chemin = os.path.join(os.path.dirname(__file__), "..", "data", "reseau_amis.csv")
    
    # Charger le graphe
    print("Chargement du graphe...")
    G = charger_graphe_complet(chemin)
    
    # Comparer les algorithmes
    resultats = executer_comparaison(G, k=5)
