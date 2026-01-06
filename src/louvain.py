"""
Module de détection de communautés avec l'algorithme de Louvain.
Approche bottom-up (agglomérative) qui optimise la modularité.
"""

import community  # python-louvain
import networkx as nx
import os
import sys

# Ajouter le chemin parent pour importer graphe
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.graphe import charger_graphe_complet


def detecter_communautes(G):        
    """
    Applique l'algorithme de Louvain pour détecter les communautés.
    
    Retourne un dictionnaire {utilisateur: numéro_communauté}
    """
    partition = community.best_partition(G)
    return partition


def calculer_modularite(G, partition):
    """
    Calcule la modularité de la partition.
    
    Valeur entre -1 et 1. Plus c'est proche de 1, meilleure est la partition.
    """
    modularite = community.modularity(partition, G)
    return modularite


def obtenir_communautes(partition):
    """
    Transforme le dictionnaire partition en liste de communautés.
    
    Retourne une liste de sets: [{membres_comm_0}, {membres_comm_1}, ...]
    """
    # Trouver le nombre de communautés
    nb_communautes = max(partition.values()) + 1
    
    # Créer une liste vide pour chaque communauté
    communautes = [set() for _ in range(nb_communautes)]
    
    # Ajouter chaque utilisateur dans sa communauté
    for utilisateur, num_comm in partition.items():
        communautes[num_comm].add(utilisateur)
    
    return communautes


def afficher_communautes(partition):
    """
    Affiche les communautés de manière lisible.
    """
    communautes = obtenir_communautes(partition)
    
    print("\n" + "="*50)
    print("   COMMUNAUTÉS DÉTECTÉES (LOUVAIN)")
    print("="*50)
    print(f"\n  Nombre de communautés: {len(communautes)}\n")
    
    for i, membres in enumerate(communautes):
        print(f"  Communauté {i+1}: {sorted(membres)}")
    
    print("="*50)
    
    return communautes


def executer_louvain(G):
    """
    Fonction principale qui exécute tout le processus Louvain.
    
    Retourne: (partition, modularité, communautés)
    """
    # Détecter les communautés
    partition = detecter_communautes(G)
    
    # Calculer la modularité
    modularite = calculer_modularite(G, partition)
    
    # Obtenir la liste des communautés
    communautes = obtenir_communautes(partition)
    
    # Afficher les résultats
    afficher_communautes(partition)
    print(f"\n  Modularité: {modularite:.4f}")
    
    return partition, modularite, communautes


# === Test du module ===
if __name__ == "__main__":
    # Chemin vers les données
    chemin = os.path.join(os.path.dirname(__file__), "..", "data", "reseau_amis.csv")
    
    # Charger le graphe
    print("Chargement du graphe...")
    G = charger_graphe_complet(chemin)
    
    # Exécuter Louvain
    print("\nApplication de l'algorithme de Louvain...")
    partition, modularite, communautes = executer_louvain(G)
