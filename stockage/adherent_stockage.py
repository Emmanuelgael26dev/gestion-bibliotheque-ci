# stockage/adherent_stockage.py
# Requêtes SQL concernant la table "adherents".

from datetime import date
from entites.adherent import Adherent
from stockage import connexion

COLONNES = ("id_adherent, nom, prenom, contact, statut, "
            "statut_carte, date_inscription, date_fin_blocage")


def _ligne_vers_adherent(ligne):
    """Transforme une ligne SQL (tuple) en objet Adherent."""
    return Adherent(ligne[0], ligne[1], ligne[2], ligne[3], ligne[4],
                    ligne[5], ligne[6], ligne[7])


def ajouter_adherent(adherent):
    """Insère un adhérent (carte active, inscrit aujourd'hui) et renvoie son numéro de carte."""
    requete = ("INSERT INTO adherents (nom, prenom, contact, statut, date_inscription) "
               "VALUES (%s, %s, %s, %s, %s)")
    parametres = (adherent.nom, adherent.prenom, adherent.contact, adherent.statut, date.today())
    return connexion.ecrire(requete, parametres)


def lister_adherents():
    lignes = connexion.lire(f"SELECT {COLONNES} FROM adherents ORDER BY nom, prenom")
    return [_ligne_vers_adherent(ligne) for ligne in lignes]


def chercher_par_id(id_adherent):
    """Renvoie l'Adherent trouvé, ou None."""
    lignes = connexion.lire(f"SELECT {COLONNES} FROM adherents WHERE id_adherent = %s", (id_adherent,))
    return _ligne_vers_adherent(lignes[0]) if lignes else None


def changer_statut_carte(id_adherent, statut_carte):
    """Passe la carte à 'actif' ou 'suspendu'."""
    connexion.ecrire("UPDATE adherents SET statut_carte = %s WHERE id_adherent = %s",
                     (statut_carte, id_adherent))


def definir_blocage(id_adherent, date_fin):
    """Bloque les emprunts jusqu'à date_fin (ou supprime le blocage si date_fin vaut None)."""
    connexion.ecrire("UPDATE adherents SET date_fin_blocage = %s WHERE id_adherent = %s",
                     (date_fin, id_adherent))
