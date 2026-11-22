# Gestion de bibliothèque (Côte d'Ivoire) - Application console Python + MySQL

Projet académique (Licence 2 Génie logiciel). Application console qui gère une bibliothèque
inspirée du fonctionnement des bibliothèques en Côte d'Ivoire : consultation sur place, emprunt
à domicile réservé aux adhérents, carte d'adhérent active ou suspendue, retards et blocages.
Les données sont enregistrées dans une base **MySQL** locale (Wampserver, Windows).

## Fonctionnalités

- **Catalogue** : lister, rechercher (titre, auteur, cote ou ID), consultation sur place,
  reposer un livre consulté, ajouter un livre.
- **Adhérents** : inscription (élève / étudiant / adulte), liste, suspension et réactivation de carte.
- **Emprunts** : emprunter, retourner, prolonger, liste des emprunts en cours, liste des retards,
  historique complet des emprunts, historique des retours.

### Menus de l'application

| Menu | Options |
|---|---|
| Principal | 1. Catalogue, 2. Adhérents, 3. Emprunts et retours, 0. Quitter |
| Catalogue | 1. Lister les livres, 2. Rechercher un livre, 3. Consultation sur place, 4. Reposer un livre consulté, 5. Ajouter un livre |
| Adhérents | 1. Inscrire un adhérent, 2. Lister les adhérents, 3. Suspendre une carte, 4. Réactiver une carte |
| Emprunts | 1. Emprunter, 2. Retourner, 3. Prolonger, 4. Emprunts en cours, 5. Liste des retards, 6. Historique des emprunts, 7. Historique des retours |

### Règles de la bibliothèque

Elles sont définies en haut de `regles/gestion_bibliotheque.py` et se modifient facilement.

| Règle | Valeur |
|---|---|
| Livres empruntés en même temps | 3 maximum |
| Durée d'un emprunt | 14 jours |
| Prolongation | 1 fois, +7 jours, seulement sans retard |
| Retard au retour | nouveaux emprunts bloqués 7 jours |
| Carte suspendue | emprunt et prolongation impossibles |
| Suspendre une carte déjà suspendue | refusé avec un message clair |
| Réactiver une carte non suspendue | refusé : « Cette carte n'est pas suspendue (elle est déjà active). » |
| Livre « sur place uniquement » | consultable, jamais empruntable |

### Consultation sur place

La consultation sur place est libre : elle ne demande ni inscription ni carte d'adhérent.

1. L'utilisateur saisit l'**ID** ou la **cote** du livre.
2. Si le livre n'existe pas, un message indique qu'il est introuvable.
3. Si aucun exemplaire n'est disponible, un message demande de choisir un autre livre.
4. Sinon le livre est pris en salle de lecture : le stock disponible diminue de 1 et la
   consultation est enregistrée dans la table `consultations`.
5. L'option **Reposer un livre consulté** remet l'exemplaire en rayon : le stock remonte de 1.

### Historique des emprunts

Les options 6 et 7 du menu Emprunts affichent, pour chaque emprunt : le numéro, le livre,
l'adhérent, la date d'emprunt, la date de retour prévue, la date de retour effective
(vide tant que le livre n'est pas rendu) et le statut :

| Statut | Signification |
|---|---|
| En cours | le livre n'est pas encore rendu, la date limite n'est pas dépassée |
| EN RETARD (x j) | le livre n'est pas rendu et la date limite est dépassée |
| Rendu | le livre a été rendu à temps |
| Rendu en retard (x j) | le livre a été rendu après la date limite |

L'historique des emprunts contient tous les emprunts. L'historique des retours contient
seulement les emprunts déjà rendus.

### Stock et transactions

Un emprunt ou une consultation diminue le stock disponible, un retour ou une remise en rayon
l'augmente. Chaque opération modifie deux tables à la fois ; elle est faite dans une
**transaction SQL** (tout réussit ou tout est annulé).

## Architecture

```
bibliotheque/
├── main.py                       # point d'entrée : relie les couches
├── requirements.txt              # dépendance : mysql-connector-python
├── .gitignore
├── README.md
├── sql/
│   └── schema.sql                # création de la base, des tables et de données de test
├── entites/                      # les objets de la bibliothèque
│   ├── livre.py
│   ├── adherent.py
│   ├── emprunt.py
│   └── consultation.py
├── regles/                       # la logique métier
│   └── gestion_bibliotheque.py
├── stockage/                     # tout ce qui touche à MySQL
│   ├── connexion.py              # connexion + exécution des requêtes
│   ├── livre_stockage.py
│   ├── adherent_stockage.py
│   ├── emprunt_stockage.py
│   └── consultation_stockage.py
└── affichage/                    # l'interface console
    └── console.py
```

Chaque couche ne parle qu'à la couche juste en dessous :

`affichage` → `regles` → `stockage` → MySQL (les `entites` sont utilisées par toutes les couches).

- `affichage/console.py` : menus et saisies, aucune requête SQL.
- `regles/gestion_bibliotheque.py` : vérifie les règles, puis demande à `stockage` d'enregistrer.
- `stockage/` : requêtes SQL paramétrées (`%s`) et conversion ligne SQL → objet.

### Gestion des erreurs

- Saisies invalides (lettres à la place d'un nombre, champ vide...) : la question est reposée.
- `ErreurRegle` : une règle de la bibliothèque n'est pas respectée (message affiché).
- `ErreurBase` : problème MySQL (connexion, requête) avec un message lisible.
- Erreur imprévue : un message « Erreur inattendue » est affiché, le programme ne se ferme pas.

## Base de données

Base `bibliotheque_ci`, 4 tables :

| Table | Rôle |
|---|---|
| `livres` | catalogue : cote, titre, auteur, catégorie, exemplaires total et disponibles, consultation seule |
| `adherents` | lecteurs : nom, prénom, contact, statut, état de la carte, fin de blocage |
| `emprunts` | emprunts à domicile : dates d'emprunt, limite (retour prévu) et de retour effectif, prolongations |
| `consultations` | livres pris en salle de lecture : date de début et date de fin |

Les tables `emprunts` et `consultations` ont une clé étrangère vers `livres`. La table `emprunts`
a aussi une clé étrangère vers `adherents`.

## Prérequis

- Windows avec **Wampserver** (MySQL/MariaDB)
- **Python 3.8 ou plus** (cocher « Add Python to PATH » à l'installation)
- **Git**

## 1. Préparer la base de données (Wampserver)

1. Lancer Wampserver et attendre que l'icône dans la barre des tâches soit **verte**.
2. Ouvrir phpMyAdmin : http://localhost/phpmyadmin (utilisateur `root`, mot de passe vide).
3. Cliquer sur l'onglet **Importer**, choisir le fichier `sql/schema.sql`, puis **Importer**.
   La base `bibliotheque_ci` est créée avec les tables `livres`, `adherents`, `emprunts`,
   `consultations` et quelques données de test.

Importer le fichier une seconde fois remet la base à zéro.

## 2. Cloner, installer et lancer

Dans l'invite de commandes (cmd) ou PowerShell :

```bash
git clone https://github.com/<utilisateur>/<depot>.git
cd <depot>

python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt

python main.py
```

(PowerShell : si `activate` est bloqué, lancer d'abord
`Set-ExecutionPolicy -Scope Process Bypass`.)

## 3. Configuration de la connexion

Les paramètres sont en haut de `stockage/connexion.py` :

```python
HOTE = "localhost"
PORT = 3306
UTILISATEUR = "root"
MOT_DE_PASSE = ""        # vide par défaut sur Wampserver
BASE = "bibliotheque_ci"
```

## Problèmes fréquents

| Message | Solution |
|---|---|
| `Connexion impossible à MySQL` | Wampserver n'est pas démarré ou l'icône n'est pas verte. |
| `Access denied for user 'root'` | Mettre le bon mot de passe dans `MOT_DE_PASSE`. |
| `Unknown database 'bibliotheque_ci'` | `sql/schema.sql` n'a pas été importé. |
| `Table 'bibliotheque_ci.consultations' doesn't exist` | Réimporter `sql/schema.sql` (version à jour avec la table `consultations`). |
| Connexion refusée sur le port 3306 | Vérifier le port MySQL dans Wamp (parfois 3307) et modifier `PORT`. |
| `ModuleNotFoundError: mysql` | Lancer `python -m pip install -r requirements.txt` (environnement virtuel activé). |

## Scénario de test rapide

1. Adhérents → inscrire un adhérent (ou utiliser la carte n°1 de test).
2. Emprunts → emprunter un livre : un exemplaire disparaît du stock.
3. Emprunter le « Dictionnaire Larousse » : refusé (sur place uniquement).
4. Emprunter 4 livres avec la même carte : le 4e est refusé.
5. Prolonger un emprunt, puis essayer une seconde fois : refusé.
6. Retourner le livre : le stock remonte.
7. Catalogue → Consultation sur place avec un ID inexistant : « Livre introuvable ».
8. Consultation sur place d'un livre disponible : le stock baisse ; essayer de le reprendre
   quand il n'y a plus d'exemplaire : « n'est pas disponible ». Puis « Reposer un livre consulté » :
   le stock remonte.
9. Adhérents → réactiver une carte déjà active : « Cette carte n'est pas suspendue ».
   Suspendre deux fois la même carte : « Cette carte est déjà suspendue ».
10. Emprunts → Historique des emprunts, puis Historique des retours : vérifier les statuts.
11. Pour simuler un retard dans phpMyAdmin, changer `date_limite` d'un emprunt vers une date passée :
    la liste des retards l'affiche, le retour bloque ensuite les nouveaux emprunts.