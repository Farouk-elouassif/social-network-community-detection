# -*- coding: utf-8 -*-
"""
Module d'analyse des communautés détectées.
Calcule les relations internes/externes et la densité de chaque communauté.
"""

import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.graphe import charger_graphe_complet
from src.louvain import executer_louvain


def compter_aretes_internes(G, membres):
    """
    Compte les arêtes à l'intérieur d'une communauté.
    
    Arguments:
        G: le graphe
        membres: set des membres de la communauté
    
    Retourne le nombre d'arêtes internes
    """
    count = 0
    for u, v in G.edges():
        if u in membres and v in membres:
            count += 1
    return count


def compter_aretes_externes(G, membres):
    """
    Compte les arêtes qui sortent d'une communauté.
    
    Arguments:
        G: le graphe
        membres: set des membres de la communauté
    
    Retourne le nombre d'arêtes externes
    """
    count = 0
    for u, v in G.edges():
        # Une arête est externe si un seul des deux noeuds est dans la communauté
        u_dedans = u in membres
        v_dedans = v in membres
        if u_dedans != v_dedans:  # XOR: un seul est dedans
            count += 1
    return count


def calculer_densite(G, membres):
    """
    Calcule la densité d'une communauté.
    
    Densité = arêtes existantes / arêtes possibles
    
    Retourne une valeur entre 0 et 1
    """
    n = len(membres)
    if n < 2:
        return 0.0
    
    # Nombre d'arêtes possibles dans un groupe de n personnes
    aretes_possibles = n * (n - 1) / 2
    
    # Nombre d'arêtes existantes
    aretes_existantes = compter_aretes_internes(G, membres)
    
    densite = aretes_existantes / aretes_possibles
    return densite


def analyser_communaute(G, membres, num):
    """
    Analyse une seule communauté.
    
    Retourne un dictionnaire avec toutes les métriques
    """
    aretes_int = compter_aretes_internes(G, membres)
    aretes_ext = compter_aretes_externes(G, membres)
    densite = calculer_densite(G, membres)
    
    # Ratio interne/externe
    if aretes_ext > 0:
        ratio = aretes_int / aretes_ext
    else:
        ratio = float('inf')  # Pas d'arêtes externes
    
    return {
        'numero': num,
        'taille': len(membres),
        'membres': sorted(membres),
        'aretes_internes': aretes_int,
        'aretes_externes': aretes_ext,
        'ratio_int_ext': ratio,
        'densite': densite
    }


def analyser_toutes_communautes(G, communautes):
    """
    Analyse toutes les communautés.
    
    Arguments:
        G: le graphe
        communautes: liste de sets [{membres_1}, {membres_2}, ...]
    
    Retourne une liste d'analyses
    """
    analyses = []
    for i, membres in enumerate(communautes):
        analyse = analyser_communaute(G, membres, i + 1)
        analyses.append(analyse)
    return analyses


def calculer_statistiques_globales(G, analyses):
    """
    Calcule les statistiques globales sur toutes les communautés.
    """
    total_internes = sum(a['aretes_internes'] for a in analyses)
    total_externes = sum(a['aretes_externes'] for a in analyses) // 2  # Divisé par 2 car comptées 2 fois
    densite_moyenne = sum(a['densite'] for a in analyses) / len(analyses)
    
    return {
        'nb_communautes': len(analyses),
        'total_aretes_internes': total_internes,
        'total_aretes_externes': total_externes,
        'densite_moyenne': densite_moyenne
    }


def afficher_analyse(analyses, stats_globales):
    """
    Affiche l'analyse de manière lisible.
    """
    print("\n")
    print("="*70)
    print("                    ANALYSE DES COMMUNAUTÉS")
    print("="*70)
    
    # Tableau par communauté
    print()
    print(f"  {'Comm.':<8} {'Taille':<8} {'Internes':<10} {'Externes':<10} {'Densité':<10}")
    print("  " + "-"*50)
    
    for a in analyses:
        print(f"  {a['numero']:<8} {a['taille']:<8} {a['aretes_internes']:<10} {a['aretes_externes']:<10} {a['densite']:<10.2f}")
    
    print("  " + "-"*50)
    
    # Statistiques globales
    print()
    print("  STATISTIQUES GLOBALES:")
    print("  " + "-"*50)
    print(f"  Nombre de communautés:      {stats_globales['nb_communautes']}")
    print(f"  Total arêtes internes:      {stats_globales['total_aretes_internes']}")
    print(f"  Total arêtes externes:      {stats_globales['total_aretes_externes']}")
    print(f"  Densité moyenne:            {stats_globales['densite_moyenne']:.2f}")
    print("  " + "-"*50)
    
    # Interprétation
    print()
    print("  INTERPRÉTATION:")
    print("  " + "-"*50)
    
    if stats_globales['densite_moyenne'] > 0.5:
        print("  ✓ Les communautés sont bien connectées en interne")
    else:
        print("  ⚠ Les communautés ont une faible densité interne")
    
    ratio_global = stats_globales['total_aretes_internes'] / max(stats_globales['total_aretes_externes'], 1)
    if ratio_global > 1:
        print(f"  ✓ Plus de liens internes qu'externes (ratio: {ratio_global:.1f})")
    else:
        print(f"  ⚠ Plus de liens externes qu'internes (ratio: {ratio_global:.1f})")
    
    print("="*70)
    
    # Détails par communauté
    print()
    print("  DÉTAILS PAR COMMUNAUTÉ:")
    print("  " + "-"*50)
    for a in analyses:
        print(f"\n  Communauté {a['numero']}: {a['membres']}")
    
    print()


def executer_analyse(G, communautes):
    """
    Fonction principale: analyse les communautés et affiche les résultats.
    """
    analyses = analyser_toutes_communautes(G, communautes)
    stats = calculer_statistiques_globales(G, analyses)
    afficher_analyse(analyses, stats)
    return analyses, stats


# === Test du module ===
if __name__ == "__main__":
    # Chemin vers les données
    chemin = os.path.join(os.path.dirname(__file__), "..", "data", "reseau_amis.csv")
    
    # Charger le graphe
    print("Chargement du graphe...")
    G = charger_graphe_complet(chemin)
    
    # Détecter les communautés avec Louvain
    print("\nDétection des communautés avec Louvain...")
    partition, modularite, communautes = executer_louvain(G)
    
    # Analyser les communautés
    print("\nAnalyse des communautés...")
    analyses, stats = executer_analyse(G, communautes)
