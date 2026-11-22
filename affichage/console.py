# affichage/console.py
# Interface console : menus, saisies sécurisées et affichage des listes.
# Cette couche ne contient AUCUNE requête SQL : elle parle uniquement à GestionBibliotheque.

from regles.gestion_bibliotheque import ErreurRegle, STATUTS_VALIDES
from stockage.connexion import ErreurBase


# ======================================================================
# Fonctions de saisie (elles redemandent tant que la saisie est invalide)
# ======================================================================
def lire_entier(message, minimum=None, maximum=None):
    """Demande un nombre entier (dans un intervalle optionnel)."""
    while True:
        saisie = input(message).strip()
        try:
            valeur = int(saisie)
        except ValueError:
            print("Erreur : veuillez saisir un nombre entier.")
            continue
        if minimum is not None and valeur < minimum:
            print(f"Erreur : la valeur doit être au moins {minimum}.")
            continue
        if maximum is not None and valeur > maximum:
            print(f"Erreur : la valeur doit être au plus {maximum}.")
            continue
        return valeur


def lire_texte(message):
    """Demande un texte non vide."""
    while True:
        texte = input(message).strip()
        if texte != "":
            return texte
        print("Erreur : ce champ ne peut pas être vide.")


def lire_oui_non(message):
    """Demande o/n et renvoie True pour 'oui'."""
    while True:
        reponse = input(message + " (o/n) : ").strip().lower()
        if reponse in ("o", "oui"):
            return True
        if reponse in ("n", "non"):
            return False
        print("Erreur : répondez par o ou n.")


def afficher_menu(titre, options, libelle_zero="Retour"):
    """Affiche un menu numéroté et renvoie le choix de l'utilisateur (0 = retour/quitter)."""
    print("\n" + "=" * 54)
    print(titre.center(54))
    print("=" * 54)
    for numero, texte in enumerate(options, start=1):
        print(f"  {numero}. {texte}")
    print(f"  0. {libelle_zero}")
    return lire_entier("Votre choix : ", 0, len(options))


# ======================================================================
# Fonctions d'affichage des listes
# ======================================================================
def afficher_livres(livres):
    if not livres:
        print("Aucun livre trouvé.")
        return
    print(f"\n{'ID':<4}{'Cote':<12}{'Titre':<32}{'Auteur':<22}{'Catégorie':<14}{'Dispo':<8}Accès")
    print("-" * 105)
    for livre in livres:
        stock = f"{livre.exemplaires_dispo}/{livre.exemplaires_total}"
        print(f"{livre.id_livre:<4}{livre.cote:<12}{livre.titre[:30]:<32}{livre.auteur[:20]:<22}"
              f"{livre.categorie[:12]:<14}{stock:<8}{livre.mode_acces()}")

def afficher_consultations(consultations):
    if not consultations:
        print("Aucun livre n'est actuellement en consultation.")
        return
    print(f"\n{'ID livre':<10}{'Titre':<36}Pris le")
    print("-" * 62)
    for c in consultations:
        print(f"{c.id_livre:<10}{c.titre_livre[:34]:<36}{c.date_debut.strftime('%d/%m/%Y %H:%M')}")

def afficher_adherents(adherents):
    if not adherents:
        print("Aucun adhérent inscrit.")
        return
    print(f"\n{'Carte':<7}{'Nom complet':<28}{'Contact':<16}{'Statut':<10}{'Carte':<11}Blocage")
    print("-" * 85)
    for a in adherents:
        carte = "ACTIVE" if a.est_actif() else "SUSPENDUE"
        blocage = f"jusqu'au {a.date_fin_blocage}" if a.est_bloque() else "-"
        print(f"{a.id_adherent:<7}{a.nom_complet()[:26]:<28}{a.contact:<16}{a.statut:<10}{carte:<11}{blocage}")


def afficher_emprunts(emprunts):
    if not emprunts:
        print("Aucun emprunt à afficher.")
        return
    print(f"\n{'N°':<5}{'Livre':<30}{'Adhérent':<24}{'Emprunté le':<13}{'Limite':<13}Situation")
    print("-" * 100)
    for e in emprunts:
        if e.est_en_retard():
            situation = f"EN RETARD ({e.jours_de_retard()} j)"
        else:
            situation = "En cours"
        print(f"{e.id_emprunt:<5}{e.titre_livre[:28]:<30}{e.nom_adherent[:22]:<24}"
              f"{str(e.date_emprunt):<13}{str(e.date_limite):<13}{situation}")

def afficher_historique(emprunts):
    """Affiche des emprunts avec toutes les dates et le statut."""
    if not emprunts:
        print("Aucun emprunt à afficher.")
        return
    print(f"\n{'N°':<5}{'Livre':<22}{'Adhérent':<20}{'Emprunté le':<12}"
          f"{'Retour prévu':<13}{'Retour effectif':<16}Statut")
    print("-" * 110)
    for e in emprunts:
        # Tant que le livre n'est pas rendu, il n'y a pas de date de retour effective
        retour_effectif = str(e.date_retour) if e.date_retour is not None else "-"
        print(f"{e.id_emprunt:<5}{e.titre_livre[:20]:<22}{e.nom_adherent[:18]:<20}"
              f"{str(e.date_emprunt):<12}{str(e.date_limite):<13}{retour_effectif:<16}{e.statut()}")


# ======================================================================
# Actions du menu (une fonction par action)
# ======================================================================
def action_lister_livres(gestion):
    afficher_livres(gestion.lister_livres())


def action_rechercher_livre(gestion):
    mot = lire_texte("Titre, auteur, cote ou ID à rechercher : ")
    afficher_livres(gestion.rechercher_livres(mot))


def action_consultation_sur_place(gestion):
    print("\n--- Consultation sur place (libre, sans inscription) ---")
    identifiant = lire_texte("ID ou cote du livre à consulter : ")
    livre = gestion.consulter_sur_place(identifiant)
    print(f"Le livre « {livre.titre} » est disponible : vous pouvez le prendre.")
    print("Il reste dans la salle de lecture et doit être reposé en rayon après consultation.")


def action_reposer_livre(gestion):
    print("\n--- Reposer un livre consulté ---")
    afficher_consultations(gestion.lister_consultations_en_cours())
    identifiant = lire_texte("ID ou cote du livre à reposer : ")
    livre = gestion.reposer_livre(identifiant)
    print(f"Le livre « {livre.titre} » est reposé en rayon et de nouveau disponible.")


def action_ajouter_livre(gestion):
    print("\n--- Ajout d'un livre ---")
    cote = lire_texte("Cote (ex : ROM-KOU-02) : ").upper()
    titre = lire_texte("Titre : ")
    auteur = lire_texte("Auteur : ")
    categorie = lire_texte("Catégorie : ")
    nb = lire_entier("Nombre d'exemplaires : ", 1)
    sur_place = lire_oui_non("Consultation sur place uniquement ?")
    id_livre = gestion.ajouter_livre(cote, titre, auteur, categorie, nb, sur_place)
    print(f"Livre ajouté avec l'ID {id_livre}.")


def action_inscrire_adherent(gestion):
    print("\n--- Inscription d'un adhérent ---")
    nom = lire_texte("Nom : ")
    prenom = lire_texte("Prénom : ")
    contact = lire_texte("Contact (téléphone ou matricule) : ")
    print("Statut : 1. élève   2. étudiant   3. adulte")
    choix = lire_entier("Votre choix : ", 1, 3)
    statut = STATUTS_VALIDES[choix - 1]
    id_adherent = gestion.inscrire_adherent(nom, prenom, contact, statut)
    print(f"Inscription réussie. Numéro de carte d'adhérent : {id_adherent}")


def action_lister_adherents(gestion):
    afficher_adherents(gestion.lister_adherents())


def action_suspendre_carte(gestion):
    id_adherent = lire_entier("Numéro de carte à suspendre : ", 1)
    gestion.suspendre_carte(id_adherent)
    print("Carte suspendue.")


def action_reactiver_carte(gestion):
    id_adherent = lire_entier("Numéro de carte à réactiver : ", 1)
    gestion.reactiver_carte(id_adherent)
    print("Carte réactivée avec succès.")


def action_emprunter(gestion):
    print("\n--- Nouvel emprunt à domicile ---")
    id_adherent = lire_entier("Numéro de carte de l'adhérent : ", 1)
    id_livre = lire_entier("ID du livre : ", 1)
    id_emprunt, date_limite = gestion.emprunter(id_livre, id_adherent)
    print(f"Emprunt n°{id_emprunt} enregistré. Date limite de retour : {date_limite}")


def action_retourner(gestion):
    print("\n--- Retour d'un livre ---")
    afficher_emprunts(gestion.lister_emprunts_en_cours())
    id_emprunt = lire_entier("N° de l'emprunt à rendre : ", 1)
    jours_retard, fin_blocage = gestion.retourner(id_emprunt)
    print("Retour enregistré.")
    if jours_retard > 0:
        print(f"ATTENTION : retard de {jours_retard} jour(s). "
              f"Nouveaux emprunts bloqués jusqu'au {fin_blocage}.")


def action_prolonger(gestion):
    print("\n--- Prolongation d'un emprunt ---")
    afficher_emprunts(gestion.lister_emprunts_en_cours())
    id_emprunt = lire_entier("N° de l'emprunt à prolonger : ", 1)
    nouvelle_date = gestion.prolonger(id_emprunt)
    print(f"Emprunt prolongé. Nouvelle date limite : {nouvelle_date}")


def action_emprunts_en_cours(gestion):
    afficher_emprunts(gestion.lister_emprunts_en_cours())


def action_retards(gestion):
    afficher_emprunts(gestion.lister_retards())

def action_historique_emprunts(gestion):
    print("\n--- Historique complet des emprunts ---")
    afficher_historique(gestion.lister_historique_emprunts())


def action_historique_retours(gestion):
    print("\n--- Historique des retours ---")
    afficher_historique(gestion.lister_historique_retours())


# ======================================================================
# Menus
# ======================================================================
def executer(action, gestion):
    """Lance une action en attrapant les erreurs prévues, pour éviter un plantage brutal."""
    try:
        action(gestion)
    except ErreurRegle as erreur:
        print(f"Règle de la bibliothèque : {erreur}")
    except ErreurBase as erreur:
        print(f"Erreur de base de données : {erreur}")


def menu_catalogue(gestion):
    actions = {
        1: action_lister_livres,
        2: action_rechercher_livre,
        3: action_consultation_sur_place,
        4: action_reposer_livre,
        5: action_ajouter_livre,
    }
    options = ["Lister les livres", "Rechercher un livre", "Consultation sur place",
               "Reposer un livre consulté", "Ajouter un livre"]
    while True:
        choix = afficher_menu("CATALOGUE", options)
        if choix == 0:
            return
        executer(actions[choix], gestion)


def menu_adherents(gestion):
    actions = {
        1: action_inscrire_adherent,
        2: action_lister_adherents,
        3: action_suspendre_carte,
        4: action_reactiver_carte,
    }
    options = ["Inscrire un adhérent", "Lister les adhérents",
               "Suspendre une carte", "Réactiver une carte"]
    while True:
        choix = afficher_menu("ADHÉRENTS", options)
        if choix == 0:
            return
        executer(actions[choix], gestion)


def menu_emprunts(gestion):
    actions = {
        1: action_emprunter,
        2: action_retourner,
        3: action_prolonger,
        4: action_emprunts_en_cours,
        5: action_retards,
        6: action_historique_emprunts,
        7: action_historique_retours,
    }
    options = ["Emprunter un livre", "Retourner un livre", "Prolonger un emprunt",
               "Emprunts en cours", "Liste des retards",
               "Historique des emprunts", "Historique des retours"]
    while True:
        choix = afficher_menu("EMPRUNTS", options)
        if choix == 0:
            return
        executer(actions[choix], gestion)


def lancer(gestion):
    """Boucle du menu principal."""
    sous_menus = {1: menu_catalogue, 2: menu_adherents, 3: menu_emprunts}
    options = ["Catalogue (livres)", "Adhérents", "Emprunts et retours"]
    try:
        while True:
            choix = afficher_menu("BIBLIOTHÈQUE - MENU PRINCIPAL", options, "Quitter")
            if choix == 0:
                print("Au revoir !")
                return
            sous_menus[choix](gestion)
    except (KeyboardInterrupt, EOFError):
        print("\nFermeture du programme. Au revoir !")
