# stockage/connexion.py
# Connexion à MySQL et exécution des requêtes SQL.
# Toutes les autres fonctions de la couche "stockage" passent par ce fichier.

import mysql.connector
from mysql.connector import Error

# --- Paramètres de connexion (Wampserver : utilisateur root, sans mot de passe par défaut) ---
HOTE = "localhost"
PORT = 3306            # si le MySQL de Wamp utilise un autre port (3307...), le changer ici
UTILISATEUR = "root"
MOT_DE_PASSE = ""      # vide par défaut sur Wampserver
BASE = "bibliotheque_ci"


class ErreurBase(Exception):
    """Erreur liée à la base de données (message lisible pour l'utilisateur)."""


def _message_erreur(erreur):
    """Transforme une erreur MySQL en phrase compréhensible."""
    if erreur.errno == 1062:
        return "Cette valeur existe déjà dans la base (doublon)."
    if erreur.errno == 1452:
        return "Référence invalide (livre ou adhérent inexistant)."
    return str(erreur)


def obtenir_connexion():
    """Ouvre une connexion à MySQL. Lève ErreurBase si ça échoue."""
    try:
        return mysql.connector.connect(
            host=HOTE, port=PORT, user=UTILISATEUR, password=MOT_DE_PASSE,
            database=BASE, charset="utf8mb4"   # utf8mb4 = accents corrects
        )
    except Error as erreur:
        raise ErreurBase(f"Connexion impossible à MySQL : {erreur}")


def tester_connexion():
    """Utilisé au démarrage pour vérifier que MySQL répond."""
    connexion = obtenir_connexion()
    connexion.close()


def lire(requete, parametres=()):
    """Exécute un SELECT et renvoie la liste des lignes (chaque ligne est un tuple)."""
    connexion = None
    try:
        connexion = obtenir_connexion()
        curseur = connexion.cursor()
        curseur.execute(requete, parametres)   # %s dans la requête = paramètres (protège des injections SQL)
        lignes = curseur.fetchall()
        curseur.close()
        return lignes
    except Error as erreur:
        raise ErreurBase(_message_erreur(erreur))
    finally:
        if connexion is not None and connexion.is_connected():
            connexion.close()


def ecrire_transaction(operations):
    """
    Exécute plusieurs requêtes (INSERT / UPDATE) comme un seul bloc :
    soit tout réussit (commit), soit tout est annulé (rollback).
    'operations' est une liste de tuples (requete, parametres).
    Renvoie l'identifiant généré par la première requête (utile pour un INSERT).
    """
    connexion = None
    try:
        connexion = obtenir_connexion()
        curseur = connexion.cursor()
        premier_id = None
        for numero, (requete, parametres) in enumerate(operations):
            curseur.execute(requete, parametres)
            if numero == 0:
                premier_id = curseur.lastrowid
        connexion.commit()
        curseur.close()
        return premier_id
    except Error as erreur:
        if connexion is not None and connexion.is_connected():
            connexion.rollback()               # on annule tout en cas de problème
        raise ErreurBase(_message_erreur(erreur))
    finally:
        if connexion is not None and connexion.is_connected():
            connexion.close()


def ecrire(requete, parametres=()):
    """Raccourci pour une seule requête d'écriture."""
    return ecrire_transaction([(requete, parametres)])
