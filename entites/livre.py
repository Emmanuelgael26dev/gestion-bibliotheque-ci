# entites/livre.py
# Un objet Livre représente une ligne de la table "livres".


class Livre:
    """Un ouvrage du catalogue de la bibliothèque."""

    def __init__(self, id_livre, cote, titre, auteur, categorie,
                 exemplaires_total, exemplaires_dispo, consultation_seule=False):
        self.id_livre = id_livre                    # identifiant en base (None avant l'enregistrement)
        self.cote = cote                            # cote unique, ex : "ROM-KOU-01"
        self.titre = titre
        self.auteur = auteur
        self.categorie = categorie
        self.exemplaires_total = exemplaires_total  # nombre d'exemplaires possédés
        self.exemplaires_dispo = exemplaires_dispo  # nombre d'exemplaires actuellement en rayon
        self.consultation_seule = consultation_seule  # True = lecture sur place uniquement

    def est_empruntable(self):
        """Un livre est empruntable s'il n'est pas réservé à la consultation et s'il reste un exemplaire."""
        return (not self.consultation_seule) and self.exemplaires_dispo > 0

    def mode_acces(self):
        """Texte décrivant comment on peut utiliser ce livre."""
        if self.consultation_seule:
            return "Sur place uniquement"
        return "Emprunt possible"
