# stockage/consultation_stockage.py
# Requêtes SQL concernant la table "consultations".

from datetime import datetime
from entites.consultation import Consultation
from stockage import connexion


def enregistrer_consultation(id_livre):
    """Enregistre la consultation ET diminue le stock disponible (transaction)."""
    operations = [
        ("INSERT INTO consultations (id_livre, date_debut) VALUES (%s, %s)",
         (id_livre, datetime.now())),
        ("UPDATE livres SET exemplaires_dispo = exemplaires_dispo - 1 "
         "WHERE id_livre = %s AND exemplaires_dispo > 0", (id_livre,)),
    ]
    return connexion.ecrire_transaction(operations)


def chercher_en_cours_par_livre(id_livre):
    """Renvoie la plus ancienne consultation non terminée de ce livre, ou None."""
    lignes = connexion.lire(
        "SELECT id_consultation, id_livre, date_debut, date_fin FROM consultations "
        "WHERE id_livre = %s AND date_fin IS NULL ORDER BY date_debut LIMIT 1", (id_livre,))
    return Consultation(*lignes[0]) if lignes else None


def enregistrer_fin(consultation):
    """Marque la consultation comme terminée ET remet l'exemplaire en stock (transaction)."""
    operations = [
        ("UPDATE consultations SET date_fin = %s WHERE id_consultation = %s",
         (datetime.now(), consultation.id_consultation)),
        ("UPDATE livres SET exemplaires_dispo = exemplaires_dispo + 1 WHERE id_livre = %s",
         (consultation.id_livre,)),
    ]
    connexion.ecrire_transaction(operations)


def lister_en_cours():
    """Les livres actuellement en salle de lecture."""
    lignes = connexion.lire(
        "SELECT c.id_consultation, c.id_livre, c.date_debut, c.date_fin, l.titre "
        "FROM consultations c JOIN livres l ON c.id_livre = l.id_livre "
        "WHERE c.date_fin IS NULL ORDER BY c.date_debut")
    return [Consultation(*ligne) for ligne in lignes]