# entites/adherent.py
# Un objet Adherent représente une ligne de la table "adherents".

from datetime import date


class Adherent:
    """Un lecteur inscrit à la bibliothèque (il possède une carte d'adhérent)."""

    def __init__(self, id_adherent, nom, prenom, contact, statut,
                 statut_carte="actif", date_inscription=None, date_fin_blocage=None):
        self.id_adherent = id_adherent          # numéro de carte
        self.nom = nom
        self.prenom = prenom
        self.contact = contact                  # téléphone ou matricule
        self.statut = statut                    # "eleve", "etudiant" ou "adulte"
        self.statut_carte = statut_carte        # "actif" ou "suspendu"
        self.date_inscription = date_inscription
        self.date_fin_blocage = date_fin_blocage  # None si aucun blocage

    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def est_actif(self):
        """La carte est-elle active (non suspendue) ?"""
        return self.statut_carte == "actif"

    def est_bloque(self):
        """Y a-t-il un blocage temporaire (suite à un retard) encore en cours ?"""
        return self.date_fin_blocage is not None and self.date_fin_blocage >= date.today()
