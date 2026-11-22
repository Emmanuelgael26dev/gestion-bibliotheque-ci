# entites/emprunt.py
# Un objet Emprunt représente une ligne de la table "emprunts".

from datetime import date


class Emprunt:
    """Un livre emprunté à domicile par un adhérent."""

    def __init__(self, id_emprunt, id_livre, id_adherent, date_emprunt, date_limite,
                 date_retour=None, nb_prolongations=0, titre_livre="", nom_adherent=""):
        self.id_emprunt = id_emprunt
        self.id_livre = id_livre
        self.id_adherent = id_adherent
        self.date_emprunt = date_emprunt
        self.date_limite = date_limite          # date limite de retour
        self.date_retour = date_retour          # None tant que le livre n'est pas rendu
        self.nb_prolongations = nb_prolongations
        # Champs pratiques pour l'affichage (récupérés grâce à une jointure SQL)
        self.titre_livre = titre_livre
        self.nom_adherent = nom_adherent

    def est_en_cours(self):
        """Le livre n'a pas encore été rendu."""
        return self.date_retour is None

    def est_en_retard(self):
        """En cours ET date limite dépassée."""
        return self.est_en_cours() and date.today() > self.date_limite

    def jours_de_retard(self):
        """Nombre de jours de retard (0 si aucun retard).
        Si le livre est rendu, on compare la date de retour à la date limite.
        S'il est encore en cours, on compare la date d'aujourd'hui à la date limite."""
        if self.date_retour is not None:
            return max((self.date_retour - self.date_limite).days, 0)
        return max((date.today() - self.date_limite).days, 0)

    def statut(self):
        """Texte décrivant la situation de l'emprunt."""
        if self.est_en_cours():
            if self.est_en_retard():
                return f"EN RETARD ({self.jours_de_retard()} j)"
            return "En cours"
        if self.jours_de_retard() > 0:
            return f"Rendu en retard ({self.jours_de_retard()} j)"
        return "Rendu"
