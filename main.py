# main.py
# Point d'entrée : relie les couches et lance l'application.
# Lancement : python main.py

from regles.gestion_bibliotheque import GestionBibliotheque
from stockage.connexion import tester_connexion, ErreurBase
from affichage import console


def main():
    # 1. On vérifie que MySQL est joignable avant d'afficher le menu
    try:
        tester_connexion()
    except ErreurBase as erreur:
        print(f"Erreur : {erreur}")
        print("Vérifiez que Wampserver est démarré (icône verte), que schema.sql a été importé")
        print("et que les paramètres de stockage/connexion.py sont corrects.")
        return

    # 2. On crée l'objet qui contient les règles, puis on lance l'interface console
    gestion = GestionBibliotheque()
    console.lancer(gestion)


if __name__ == "__main__":
    main()
