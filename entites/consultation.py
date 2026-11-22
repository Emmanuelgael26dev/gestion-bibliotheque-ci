# entites/consultation.py
# Un objet Consultation représente une ligne de la table "consultations".


class Consultation:
    """Un livre pris en salle de lecture (consultation sur place)."""

    def __init__(self, id_consultation, id_livre, date_debut, date_fin=None, titre_livre=""):
        self.id_consultation = id_consultation
        self.id_livre = id_livre
        self.date_debut = date_debut      # moment où le livre a été pris
        self.date_fin = date_fin          # None tant que le livre n'est pas reposé
        self.titre_livre = titre_livre    # pour l'affichage (jointure SQL)

    def est_en_cours(self):
        return self.date_fin is None