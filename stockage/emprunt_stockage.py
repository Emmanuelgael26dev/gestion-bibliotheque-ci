# stockage/emprunt_stockage.py
# Requêtes SQL concernant la table "emprunts".

from datetime import date
from entites.emprunt import Emprunt
from stockage import connexion

# Requête de base : on joint les 3 tables pour récupérer aussi le titre et le nom de l'adhérent.
REQUETE_BASE = (
    "SELECT e.id_emprunt, e.id_livre, e.id_adherent, e.date_emprunt, e.date_limite, "
    "e.date_retour, e.nb_prolongations, l.titre, CONCAT(a.prenom, ' ', a.nom) "
    "FROM emprunts e "
    "JOIN livres l ON e.id_livre = l.id_livre "
    "JOIN adherents a ON e.id_adherent = a.id_adherent "
)


def _ligne_vers_emprunt(ligne):
    """Transforme une ligne SQL (tuple) en objet Emprunt."""
    return Emprunt(ligne[0], ligne[1], ligne[2], ligne[3], ligne[4],
                   ligne[5], ligne[6], ligne[7], ligne[8])


def enregistrer_emprunt(id_livre, id_adherent, date_emprunt, date_limite):
    """
    Crée l'emprunt ET diminue le stock du livre, dans une seule transaction.
    Renvoie l'identifiant de l'emprunt.
    """
    operations = [
        ("INSERT INTO emprunts (id_livre, id_adherent, date_emprunt, date_limite) "
         "VALUES (%s, %s, %s, %s)", (id_livre, id_adherent, date_emprunt, date_limite)),
        ("UPDATE livres SET exemplaires_dispo = exemplaires_dispo - 1 "
         "WHERE id_livre = %s AND exemplaires_dispo > 0", (id_livre,)),
    ]
    return connexion.ecrire_transaction(operations)


def enregistrer_retour(emprunt, date_retour):
    """Marque l'emprunt comme rendu ET remet un exemplaire en stock (transaction)."""
    operations = [
        ("UPDATE emprunts SET date_retour = %s WHERE id_emprunt = %s",
         (date_retour, emprunt.id_emprunt)),
        ("UPDATE livres SET exemplaires_dispo = exemplaires_dispo + 1 WHERE id_livre = %s",
         (emprunt.id_livre,)),
    ]
    connexion.ecrire_transaction(operations)


def prolonger(id_emprunt, nouvelle_date_limite):
    connexion.ecrire(
        "UPDATE emprunts SET date_limite = %s, nb_prolongations = nb_prolongations + 1 "
        "WHERE id_emprunt = %s", (nouvelle_date_limite, id_emprunt))


def chercher_par_id(id_emprunt):
    """Renvoie l'Emprunt trouvé, ou None."""
    lignes = connexion.lire(REQUETE_BASE + "WHERE e.id_emprunt = %s", (id_emprunt,))
    return _ligne_vers_emprunt(lignes[0]) if lignes else None


def lister_en_cours():
    lignes = connexion.lire(REQUETE_BASE + "WHERE e.date_retour IS NULL ORDER BY e.date_limite")
    return [_ligne_vers_emprunt(ligne) for ligne in lignes]


def lister_retards():
    lignes = connexion.lire(
        REQUETE_BASE + "WHERE e.date_retour IS NULL AND e.date_limite < %s ORDER BY e.date_limite",
        (date.today(),))
    return [_ligne_vers_emprunt(ligne) for ligne in lignes]


def compter_en_cours_adherent(id_adherent):
    """Nombre de livres actuellement empruntés par cet adhérent."""
    lignes = connexion.lire(
        "SELECT COUNT(*) FROM emprunts WHERE id_adherent = %s AND date_retour IS NULL",
        (id_adherent,))
    return lignes[0][0]


def compter_retards_adherent(id_adherent):
    """Nombre de livres en retard pour cet adhérent."""
    lignes = connexion.lire(
        "SELECT COUNT(*) FROM emprunts "
        "WHERE id_adherent = %s AND date_retour IS NULL AND date_limite < %s",
        (id_adherent, date.today()))
    return lignes[0][0]

def lister_historique():
    """Tous les emprunts (en cours et rendus), du plus récent au plus ancien."""
    lignes = connexion.lire(
        REQUETE_BASE + "ORDER BY e.date_emprunt DESC, e.id_emprunt DESC")
    return [_ligne_vers_emprunt(ligne) for ligne in lignes]


def lister_retours():
    """Seulement les emprunts déjà rendus, du retour le plus récent au plus ancien."""
    lignes = connexion.lire(
        REQUETE_BASE + "WHERE e.date_retour IS NOT NULL "
        "ORDER BY e.date_retour DESC, e.id_emprunt DESC")
    return [_ligne_vers_emprunt(ligne) for ligne in lignes]