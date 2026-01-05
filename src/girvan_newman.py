# -*- coding: utf-8 -*-
"""
Module de détection de communautés avec l'algorithme de Girvan-Newman.
Approche top-down (divisive) basée sur la centralité d'intermédiarité.
"""

import networkx as nx
from networkx.algorithms.community import girvan_newman
import os
import sys

# Ajouter le chemin parent pour importer graphe
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.graphe import charger_graphe_complet


def detecter_communautes(G, k=None):
    """
    Applique l'algorithme de Girvan-Newman.
    
    Arguments:
        G: le graphe
        k: nombre de communautés souhaité (si None, on prend la meilleure modularité)
    
    Retourne une liste de sets: [{membres_comm_0}, {membres_comm_1}, ...]
    """
    # Appliquer Girvan-Newman (retourne un générateur)
    comp = girvan_newman(G)
    
    # Si k est spécifié, on s'arrête quand on a k communautés
    if k is not None:
        for communautes in comp:
            if len(communautes) >= k:
                return [set(c) for c in communautes]
    
    # Sinon, on cherche la meilleure modularité
    meilleure_modularite = -1
    meilleures_communautes = None
    
    # On teste les premières partitions (limité pour la performance)
    for i, communautes in enumerate(comp):
        # Convertir en liste de sets
        communautes_list = [set(c) for c in communautes]
        
        # Calculer la modularité
        mod = calculer_modularite(G, communautes_list)
        
        # Garder si meilleure
        if mod > meilleure_modularite:
            meilleure_modularite = mod
            meilleures_communautes = communautes_list
        
        # Arrêter après un certain nombre d'itérations
        if i >= 10 or len(communautes) >= G.number_of_nodes() // 2:
            break
    
    return meilleures_communautes


def calculer_modularite(G, communautes):
    """
    Calcule la modularité pour une liste de communautés.
    
    Arguments:
        G: le graphe
        communautes: liste de sets [{membres_1}, {membres_2}, ...]
    
    Retourne la modularité (entre -1 et 1)
    """
    modularite = nx.community.modularity(G, communautes)
    return modularite


def convertir_en_partition(communautes):
    """
    Convertit une liste de communautés en dictionnaire partition.
    
    Retourne {utilisateur: numéro_communauté}
    """
    partition = {}
    for i, membres in enumerate(communautes):
        for utilisateur in membres:
            partition[utilisateur] = i
    return partition


def afficher_communautes(communautes):
    """
    Affiche les communautés de manière lisible.
    """
    print("\n" + "="*50)
    print("   COMMUNAUTÉS DÉTECTÉES (GIRVAN-NEWMAN)")
    print("="*50)
    print(f"\n  Nombre de communautés: {len(communautes)}\n")
    
    for i, membres in enumerate(communautes):
        print(f"  Communauté {i+1}: {sorted(membres)}")
    
    print("="*50)
    
    return communautes


def executer_girvan_newman(G, k=None):
    """
    Fonction principale qui exécute tout le processus Girvan-Newman.
    
    Arguments:
        G: le graphe
        k: nombre de communautés souhaité (optionnel)
    
    Retourne: (partition, modularité, communautés)
    """
    # Détecter les communautés
    communautes = detecter_communautes(G, k)
    
    # Calculer la modularité
    modularite = calculer_modularite(G, communautes)
    
    # Convertir en partition (dictionnaire)
    partition = convertir_en_partition(communautes)
    
    # Afficher les résultats
    afficher_communautes(communautes)
    print(f"\n  Modularité: {modularite:.4f}")
    
    return partition, modularite, communautes


# === Test du module ===
if __name__ == "__main__":
    # Chemin vers les données
    chemin = os.path.join(os.path.dirname(__file__), "..", "data", "reseau_amis.csv")
    
    # Charger le graphe
    print("Chargement du graphe...")
    G = charger_graphe_complet(chemin)
    
    # Exécuter Girvan-Newman (avec 5 communautés)
    print("\nApplication de l'algorithme de Girvan-Newman...")
    partition, modularite, communautes = executer_girvan_newman(G, k=5)
