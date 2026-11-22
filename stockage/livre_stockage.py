# stockage/livre_stockage.py
# Requêtes SQL concernant la table "livres".

from entites.livre import Livre
from stockage import connexion

COLONNES = ("id_livre, cote, titre, auteur, categorie, "
            "exemplaires_total, exemplaires_dispo, consultation_seule")


def _ligne_vers_livre(ligne):
    """Transforme une ligne SQL (tuple) en objet Livre."""
    return Livre(ligne[0], ligne[1], ligne[2], ligne[3], ligne[4],
                 ligne[5], ligne[6], bool(ligne[7]))


def ajouter_livre(livre):
    """Insère un livre et renvoie son identifiant."""
    requete = ("INSERT INTO livres (cote, titre, auteur, categorie, "
               "exemplaires_total, exemplaires_dispo, consultation_seule) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    parametres = (livre.cote, livre.titre, livre.auteur, livre.categorie,
                  livre.exemplaires_total, livre.exemplaires_dispo, livre.consultation_seule)
    return connexion.ecrire(requete, parametres)


def lister_livres():
    lignes = connexion.lire(f"SELECT {COLONNES} FROM livres ORDER BY titre")
    return [_ligne_vers_livre(ligne) for ligne in lignes]


def chercher_par_id(id_livre):
    """Renvoie le Livre trouvé, ou None."""
    lignes = connexion.lire(f"SELECT {COLONNES} FROM livres WHERE id_livre = %s", (id_livre,))
    return _ligne_vers_livre(lignes[0]) if lignes else None


def chercher_par_cote(cote):
    lignes = connexion.lire(f"SELECT {COLONNES} FROM livres WHERE cote = %s", (cote,))
    return _ligne_vers_livre(lignes[0]) if lignes else None


def rechercher(mot):
    """Recherche dans le titre, l'auteur ou la cote ; si le mot est un nombre, teste aussi l'ID."""
    motif = f"%{mot}%"
    requete = (f"SELECT {COLONNES} FROM livres "
               "WHERE titre LIKE %s OR auteur LIKE %s OR cote LIKE %s")
    parametres = [motif, motif, motif]
    if mot.isdigit():
        requete += " OR id_livre = %s"
        parametres.append(int(mot))
    requete += " ORDER BY titre"
    lignes = connexion.lire(requete, tuple(parametres))
    return [_ligne_vers_livre(ligne) for ligne in lignes]
