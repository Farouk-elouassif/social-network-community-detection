# -*- coding: utf-8 -*-
"""
Module de visualisation des graphes et communautés.
Crée des graphiques avec matplotlib et networkx.
"""

import matplotlib.pyplot as plt
import networkx as nx
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.graphe import charger_graphe_complet
from src.louvain import executer_louvain
from src.girvan_newman import executer_girvan_newman


# Couleurs pour les communautés
COULEURS = [
    '#FF6B6B',  # Rouge
    '#4ECDC4',  # Turquoise
    '#45B7D1',  # Bleu
    '#96CEB4',  # Vert
    '#FFEAA7',  # Jaune
    '#DDA0DD',  # Violet
    '#98D8C8',  # Menthe
    '#F7DC6F',  # Or
    '#BB8FCE',  # Lavande
    '#85C1E9',  # Bleu clair
]


def dessiner_graphe_simple(G, titre="Graphe du réseau"):
    """
    Dessine le graphe sans couleurs de communauté.
    """
    plt.figure(figsize=(10, 8))
    
    # Position des noeuds
    pos = nx.spring_layout(G, seed=42)
    
    # Dessiner les arêtes
    nx.draw_networkx_edges(G, pos, alpha=0.5, width=1)
    
    # Dessiner les noeuds
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')
    
    # Dessiner les labels
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    plt.title(titre, fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    return plt.gcf()


def dessiner_communautes(G, partition, titre="Communautés détectées"):
    """
    Dessine le graphe avec les noeuds colorés par communauté.
    
    Arguments:
        G: le graphe
        partition: dictionnaire {utilisateur: numéro_communauté}
        titre: titre du graphique
    """
    plt.figure(figsize=(10, 8))
    
    # Position des noeuds (même seed pour cohérence)
    pos = nx.spring_layout(G, seed=42)
    
    # Créer la liste des couleurs pour chaque noeud
    couleurs_noeuds = []
    for noeud in G.nodes():
        num_comm = partition[noeud]
        couleur = COULEURS[num_comm % len(COULEURS)]
        couleurs_noeuds.append(couleur)
    
    # Dessiner les arêtes
    nx.draw_networkx_edges(G, pos, alpha=0.4, width=1)
    
    # Dessiner les noeuds avec couleurs
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color=couleurs_noeuds)
    
    # Dessiner les labels
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    # Légende
    nb_comm = max(partition.values()) + 1
    for i in range(nb_comm):
        plt.scatter([], [], c=COULEURS[i % len(COULEURS)], s=100, label=f'Communauté {i+1}')
    plt.legend(loc='upper left', fontsize=9)
    
    plt.title(titre, fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    return plt.gcf()


def dessiner_comparaison(G, partition_louvain, partition_gn):
    """
    Dessine les deux résultats côte à côte.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Position commune pour les deux graphes
    pos = nx.spring_layout(G, seed=42)
    
    # === Louvain (gauche) ===
    ax1 = axes[0]
    couleurs_l = [COULEURS[partition_louvain[n] % len(COULEURS)] for n in G.nodes()]
    
    nx.draw_networkx_edges(G, pos, alpha=0.4, width=1, ax=ax1)
    nx.draw_networkx_nodes(G, pos, node_size=400, node_color=couleurs_l, ax=ax1)
    nx.draw_networkx_labels(G, pos, font_size=7, ax=ax1)
    
    ax1.set_title("Louvain", fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    # === Girvan-Newman (droite) ===
    ax2 = axes[1]
    couleurs_gn = [COULEURS[partition_gn[n] % len(COULEURS)] for n in G.nodes()]
    
    nx.draw_networkx_edges(G, pos, alpha=0.4, width=1, ax=ax2)
    nx.draw_networkx_nodes(G, pos, node_size=400, node_color=couleurs_gn, ax=ax2)
    nx.draw_networkx_labels(G, pos, font_size=7, ax=ax2)
    
    ax2.set_title("Girvan-Newman", fontsize=14, fontweight='bold')
    ax2.axis('off')
    
    plt.suptitle("Comparaison des Algorithmes", fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return fig


def sauvegarder_image(fig, nom_fichier, dossier="resultats"):
    """
    Sauvegarde une figure dans le dossier resultats.
    """
    # Créer le chemin complet
    chemin_dossier = os.path.join(os.path.dirname(__file__), "..", dossier)
    
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(chemin_dossier):
        os.makedirs(chemin_dossier)
    
    # Sauvegarder
    chemin_complet = os.path.join(chemin_dossier, nom_fichier)
    fig.savefig(chemin_complet, dpi=150, bbox_inches='tight')
    print(f"  ✓ Image sauvegardée: {chemin_complet}")


def afficher_images():
    """
    Affiche toutes les figures ouvertes.
    """
    plt.show()


def generer_toutes_visualisations(G, partition_louvain, partition_gn, sauvegarder=True):
    """
    Génère toutes les visualisations du projet.
    """
    print("\n" + "="*50)
    print("       GÉNÉRATION DES VISUALISATIONS")
    print("="*50 + "\n")
    
    # 1. Graphe original
    print("  Création du graphe original...")
    fig1 = dessiner_graphe_simple(G, "Réseau d'amis - Graphe original")
    if sauvegarder:
        sauvegarder_image(fig1, "graphe_original.png")
    
    # 2. Communautés Louvain
    print("  Création du graphe Louvain...")
    fig2 = dessiner_communautes(G, partition_louvain, "Communautés détectées - Louvain")
    if sauvegarder:
        sauvegarder_image(fig2, "graphe_louvain.png")
    
    # 3. Communautés Girvan-Newman
    print("  Création du graphe Girvan-Newman...")
    fig3 = dessiner_communautes(G, partition_gn, "Communautés détectées - Girvan-Newman")
    if sauvegarder:
        sauvegarder_image(fig3, "graphe_girvan_newman.png")
    
    # 4. Comparaison côte à côte
    print("  Création de la comparaison...")
    fig4 = dessiner_comparaison(G, partition_louvain, partition_gn)
    if sauvegarder:
        sauvegarder_image(fig4, "comparaison.png")
    
    print("\n" + "="*50)
    
    return [fig1, fig2, fig3, fig4]


# === Test du module ===
if __name__ == "__main__":
    # Chemin vers les données
    chemin = os.path.join(os.path.dirname(__file__), "..", "data", "reseau_amis.csv")
    
    # Charger le graphe
    print("Chargement du graphe...")
    G = charger_graphe_complet(chemin)
    
    # Détecter les communautés
    print("\nDétection avec Louvain...")
    partition_l, mod_l, comm_l = executer_louvain(G)
    
    print("\nDétection avec Girvan-Newman...")
    partition_gn, mod_gn, comm_gn = executer_girvan_newman(G, k=5)
    
    # Générer les visualisations
    figures = generer_toutes_visualisations(G, partition_l, partition_gn, sauvegarder=True)
    
    # Afficher
    print("\nAffichage des graphiques...")
    afficher_images()
