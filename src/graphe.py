"""
Module de construction du graphe.
Charge les données CSV et construit le réseau d'amis.
"""

import pandas as pd
import networkx as nx


def charger_donnees(chemin_csv):
    """
    Charge les relations d'amitié depuis un fichier CSV.
    """
    df = pd.read_csv(chemin_csv)
    print(f"✓ Données chargées: {len(df)} relations trouvées")
    return df


def construire_graphe(df):
    """
    Construit le graphe à partir des données.
    """
    # Créer un graphe vide
    G = nx.Graph()
    
    # Ajouter chaque relation comme une arête
    for i in range(len(df)):
        ami1 = df.loc[i, 'utilisateur1']
        ami2 = df.loc[i, 'utilisateur2']
        G.add_edge(ami1, ami2)
    
    print(f"✓ Graphe construit: {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes")
    return G


def afficher_informations_graphe(G):
    """
    Affiche les informations du graphe.
    """
    # Calculer les statistiques de base
    nb_noeuds = G.number_of_nodes()
    nb_aretes = G.number_of_edges()
    degre_moyen = sum(dict(G.degree()).values()) / nb_noeuds
    densite = nx.density(G)
    est_connexe = nx.is_connected(G)
    
    # Afficher
    print("\n" + "="*50)
    print("       INFORMATIONS DU GRAPHE")
    print("="*50)
    print(f"  Nombre de nœuds (utilisateurs): {nb_noeuds}")
    print(f"  Nombre d'arêtes (relations):    {nb_aretes}")
    print(f"  Degré moyen:                    {degre_moyen:.2f}")
    print(f"  Densité du graphe:              {densite:.4f}")
    print(f"  Graphe connexe:                 {'Oui' if est_connexe else 'Non'}")
    print("="*50)
    
    # Afficher le degré de chaque utilisateur
    print("\n  Degré de chaque utilisateur:")
    print("  " + "-"*30)
    for nom in G.nodes():
        degre = G.degree(nom)
        print(f"    {nom}: {degre} ami(s)")
    
    return {
        'nb_noeuds': nb_noeuds,
        'nb_aretes': nb_aretes,
        'degre_moyen': degre_moyen,
        'densite': densite
    }


def charger_graphe_complet(chemin_csv):
    """
    Charge les données et construit le graphe en une seule étape.
    """
    df = charger_donnees(chemin_csv)
    G = construire_graphe(df)
    return G


# === Test du module ===
if __name__ == "__main__":
    # Chemin vers le fichier CSV
    chemin = './data/reseau_amis.csv'
    
    # Charger le graphe
    G = charger_graphe_complet(chemin)
    
    # Afficher les informations
    afficher_informations_graphe(G)
