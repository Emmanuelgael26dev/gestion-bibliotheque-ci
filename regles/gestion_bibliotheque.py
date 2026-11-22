# regles/gestion_bibliotheque.py
# Les règles de fonctionnement de la bibliothèque.
# Cette couche vérifie les règles, puis demande à la couche "stockage" d'enregistrer.

from datetime import date, timedelta

from entites.livre import Livre
from entites.adherent import Adherent
from stockage import livre_stockage, adherent_stockage, emprunt_stockage, consultation_stockage

# --- Règles de la bibliothèque (faciles à modifier) ---
MAX_EMPRUNTS = 3                 # nombre maximum de livres empruntés en même temps
DUREE_EMPRUNT_JOURS = 14         # durée d'un emprunt
DUREE_PROLONGATION_JOURS = 7     # durée ajoutée lors d'une prolongation
MAX_PROLONGATIONS = 1            # nombre de prolongations autorisées par emprunt
BLOCAGE_APRES_RETARD_JOURS = 7   # blocage des nouveaux emprunts après un retour tardif
STATUTS_VALIDES = ("eleve", "etudiant", "adulte")


class ErreurRegle(Exception):
    """Une règle de la bibliothèque n'est pas respectée (message affiché à l'utilisateur)."""


class GestionBibliotheque:
    """Regroupe toutes les opérations de la bibliothèque."""

    # ------------------------------------------------------------------
    # Livres
    # ------------------------------------------------------------------
    def lister_livres(self):
        return livre_stockage.lister_livres()

    def rechercher_livres(self, mot):
        if mot == "":
            raise ErreurRegle("Le critère de recherche ne peut pas être vide.")
        return livre_stockage.rechercher(mot)

    def ajouter_livre(self, cote, titre, auteur, categorie, nb_exemplaires, consultation_seule):
        if nb_exemplaires < 1:
            raise ErreurRegle("Il faut au moins 1 exemplaire.")
        if livre_stockage.chercher_par_cote(cote) is not None:
            raise ErreurRegle(f"La cote '{cote}' existe déjà.")
        # Au départ, tous les exemplaires sont disponibles (dispo = total)
        livre = Livre(None, cote, titre, auteur, categorie,
                      nb_exemplaires, nb_exemplaires, consultation_seule)
        return livre_stockage.ajouter_livre(livre)

    # ------------------------------------------------------------------
    # Adhérents
    # ------------------------------------------------------------------
    def lister_adherents(self):
        return adherent_stockage.lister_adherents()

    def inscrire_adherent(self, nom, prenom, contact, statut):
        if statut not in STATUTS_VALIDES:
            raise ErreurRegle("Statut invalide (eleve, etudiant ou adulte).")
        adherent = Adherent(None, nom, prenom, contact, statut)
        return adherent_stockage.ajouter_adherent(adherent)   # renvoie le numéro de carte

    def _adherent_existant(self, id_adherent):
        adherent = adherent_stockage.chercher_par_id(id_adherent)
        if adherent is None:
            raise ErreurRegle("Aucun adhérent avec ce numéro de carte.")
        return adherent

    def suspendre_carte(self, id_adherent):
        adherent = self._adherent_existant(id_adherent)
        if not adherent.est_actif():
            raise ErreurRegle("Cette carte est déjà suspendue.")
        adherent_stockage.changer_statut_carte(id_adherent, "suspendu")

    def reactiver_carte(self, id_adherent):
        """Réactive une carte suspendue (et supprime son éventuel blocage)."""
        adherent = self._adherent_existant(id_adherent)
        # Nouvelle vérification : on ne peut réactiver qu'une carte suspendue
        if adherent.est_actif():
            message = "Cette carte n'est pas suspendue (elle est déjà active)."
            if adherent.est_bloque():
                message += f" Les emprunts restent bloqués jusqu'au {adherent.date_fin_blocage}."
            raise ErreurRegle(message)
        adherent_stockage.changer_statut_carte(id_adherent, "actif")
        adherent_stockage.definir_blocage(id_adherent, None)

    # ------------------------------------------------------------------
    # Emprunts
    # ------------------------------------------------------------------
    def emprunter(self, id_livre, id_adherent):
        """Vérifie toutes les règles, puis enregistre l'emprunt. Renvoie (id_emprunt, date_limite)."""
        adherent = self._adherent_existant(id_adherent)

        if not adherent.est_actif():
            raise ErreurRegle("Carte suspendue : l'emprunt est impossible.")
        if adherent.est_bloque():
            raise ErreurRegle(f"Emprunts bloqués jusqu'au {adherent.date_fin_blocage} (retard précédent).")
        if emprunt_stockage.compter_retards_adherent(id_adherent) > 0:
            raise ErreurRegle("Cet adhérent a un livre en retard : il doit d'abord le rendre.")
        if emprunt_stockage.compter_en_cours_adherent(id_adherent) >= MAX_EMPRUNTS:
            raise ErreurRegle(f"Limite atteinte : {MAX_EMPRUNTS} livres maximum en même temps.")

        livre = livre_stockage.chercher_par_id(id_livre)
        if livre is None:
            raise ErreurRegle("Aucun livre avec cet identifiant.")
        if livre.consultation_seule:
            raise ErreurRegle("Ce livre est à consulter sur place uniquement.")
        if livre.exemplaires_dispo <= 0:
            raise ErreurRegle("Aucun exemplaire disponible pour ce livre.")

        date_emprunt = date.today()
        date_limite = date_emprunt + timedelta(days=DUREE_EMPRUNT_JOURS)
        id_emprunt = emprunt_stockage.enregistrer_emprunt(id_livre, id_adherent, date_emprunt, date_limite)
        return id_emprunt, date_limite

    def retourner(self, id_emprunt):
        """
        Enregistre le retour d'un livre.
        Renvoie (jours_de_retard, date_fin_blocage) ; date_fin_blocage vaut None s'il n'y a pas de retard.
        """
        emprunt = emprunt_stockage.chercher_par_id(id_emprunt)
        if emprunt is None:
            raise ErreurRegle("Aucun emprunt avec ce numéro.")
        if not emprunt.est_en_cours():
            raise ErreurRegle("Ce livre a déjà été rendu.")

        jours_retard = emprunt.jours_de_retard()          # à calculer avant d'enregistrer le retour
        emprunt_stockage.enregistrer_retour(emprunt, date.today())

        fin_blocage = None
        if jours_retard > 0:
            # Sanction : blocage temporaire des nouveaux emprunts
            fin_blocage = date.today() + timedelta(days=BLOCAGE_APRES_RETARD_JOURS)
            adherent_stockage.definir_blocage(emprunt.id_adherent, fin_blocage)
        return jours_retard, fin_blocage

    def prolonger(self, id_emprunt):
        """Prolonge un emprunt (une seule fois, et seulement si aucun retard). Renvoie la nouvelle date limite."""
        emprunt = emprunt_stockage.chercher_par_id(id_emprunt)
        if emprunt is None:
            raise ErreurRegle("Aucun emprunt avec ce numéro.")
        if not emprunt.est_en_cours():
            raise ErreurRegle("Ce livre a déjà été rendu.")
        adherent = self._adherent_existant(emprunt.id_adherent)
        if not adherent.est_actif():
            raise ErreurRegle("Carte suspendue : prolongation impossible.")
        if emprunt_stockage.compter_retards_adherent(emprunt.id_adherent) > 0:
            raise ErreurRegle("Prolongation impossible : l'adhérent a un retard en cours.")
        if emprunt.nb_prolongations >= MAX_PROLONGATIONS:
            raise ErreurRegle("Ce livre a déjà été prolongé le nombre de fois autorisé.")

        nouvelle_date = emprunt.date_limite + timedelta(days=DUREE_PROLONGATION_JOURS)
        emprunt_stockage.prolonger(id_emprunt, nouvelle_date)
        return nouvelle_date

    def lister_emprunts_en_cours(self):
        return emprunt_stockage.lister_en_cours()

    def lister_retards(self):
        return emprunt_stockage.lister_retards()

    def lister_historique_emprunts(self):
        """Tous les emprunts, en cours ou rendus."""
        return emprunt_stockage.lister_historique()

    def lister_historique_retours(self):
        """Uniquement les emprunts déjà rendus."""
        return emprunt_stockage.lister_retours()

        # ------------------------------------------------------------------
    # Consultation sur place
    # ------------------------------------------------------------------
    def _trouver_livre(self, identifiant):
        """Cherche un livre par ID (nombre) ou par cote (texte). Lève ErreurRegle s'il est introuvable."""
        if identifiant.isdigit():
            livre = livre_stockage.chercher_par_id(int(identifiant))
        else:
            livre = livre_stockage.chercher_par_cote(identifiant.upper())
        if livre is None:
            raise ErreurRegle("Livre introuvable : vérifiez l'ID ou la cote.")
        return livre

    def consulter_sur_place(self, identifiant):
        """Un livre disponible peut être pris en salle de lecture : le stock diminue de 1."""
        livre = self._trouver_livre(identifiant)
        if livre.exemplaires_dispo <= 0:
            raise ErreurRegle("Ce livre n'est pas disponible (tous les exemplaires sont déjà pris). "
                              "Veuillez choisir un autre livre.")
        consultation_stockage.enregistrer_consultation(livre.id_livre)
        return livre

    def reposer_livre(self, identifiant):
        """Le lecteur a fini : le livre est reposé en rayon, le stock augmente de 1."""
        livre = self._trouver_livre(identifiant)
        consultation = consultation_stockage.chercher_en_cours_par_livre(livre.id_livre)
        if consultation is None:
            raise ErreurRegle("Aucune consultation en cours pour ce livre.")
        consultation_stockage.enregistrer_fin(consultation)
        return livre

    def lister_consultations_en_cours(self):
        return consultation_stockage.lister_en_cours()