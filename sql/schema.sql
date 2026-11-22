-- ============================================================
-- schema.sql : création de la base "bibliotheque_ci" et des tables
-- À importer dans phpMyAdmin (onglet "Importer") ou via la ligne de commande.
-- ============================================================

-- Encodage UTF-8 pour conserver les accents (é, è, ç...)
SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS bibliotheque_ci
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

USE bibliotheque_ci;

-- On supprime d'abord les tables (dans l'ordre inverse des dépendances)
-- pour pouvoir ré-importer le fichier sans erreur.
DROP TABLE IF EXISTS emprunts;
DROP TABLE IF EXISTS adherents;
DROP TABLE IF EXISTS livres;

-- ------------------------------------------------------------
-- Table des livres (catalogue)
-- ------------------------------------------------------------
CREATE TABLE livres (
    id_livre           INT AUTO_INCREMENT PRIMARY KEY,
    cote               VARCHAR(20)  NOT NULL UNIQUE,   -- identifiant/cote unique du livre
    titre              VARCHAR(150) NOT NULL,
    auteur             VARCHAR(100) NOT NULL,
    categorie          VARCHAR(50)  NOT NULL,
    exemplaires_total  INT NOT NULL DEFAULT 1,
    exemplaires_dispo  INT NOT NULL DEFAULT 1,
    consultation_seule BOOLEAN NOT NULL DEFAULT FALSE, -- TRUE = lecture sur place uniquement
    CHECK (exemplaires_total >= 1),
    CHECK (exemplaires_dispo >= 0 AND exemplaires_dispo <= exemplaires_total)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table des adhérents (lecteurs inscrits)
-- ------------------------------------------------------------
CREATE TABLE adherents (
    id_adherent      INT AUTO_INCREMENT PRIMARY KEY,   -- numéro de carte d'adhérent
    nom              VARCHAR(60) NOT NULL,
    prenom           VARCHAR(60) NOT NULL,
    contact          VARCHAR(60) NOT NULL,             -- téléphone ou matricule
    statut           ENUM('eleve', 'etudiant', 'adulte') NOT NULL,
    statut_carte     ENUM('actif', 'suspendu') NOT NULL DEFAULT 'actif',
    date_inscription DATE NOT NULL,
    date_fin_blocage DATE NULL                         -- blocage temporaire après un retard
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Table des emprunts
-- ------------------------------------------------------------
CREATE TABLE emprunts (
    id_emprunt       INT AUTO_INCREMENT PRIMARY KEY,
    id_livre         INT NOT NULL,
    id_adherent      INT NOT NULL,
    date_emprunt     DATE NOT NULL,
    date_limite      DATE NOT NULL,                    -- date limite de retour
    date_retour      DATE NULL,                        -- NULL tant que le livre n'est pas rendu
    nb_prolongations INT NOT NULL DEFAULT 0,
    FOREIGN KEY (id_livre)    REFERENCES livres(id_livre),
    FOREIGN KEY (id_adherent) REFERENCES adherents(id_adherent)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Quelques données de départ pour tester l'application
-- ------------------------------------------------------------
INSERT INTO livres (cote, titre, auteur, categorie, exemplaires_total, exemplaires_dispo, consultation_seule) VALUES
('ROM-KOU-01', 'Les Soleils des indépendances', 'Ahmadou Kourouma', 'Roman', 3, 3, FALSE),
('ROM-DAD-01', 'Climbié', 'Bernard Dadié', 'Roman', 2, 2, FALSE),
('ROM-TAD-01', 'Reine Pokou', 'Véronique Tadjo', 'Roman', 2, 2, FALSE),
('ROM-LOB-01', 'Kocoumbo, l''étudiant noir', 'Aké Loba', 'Roman', 1, 1, FALSE),
('INF-ALG-01', 'Algorithmique et programmation', 'Collectif', 'Informatique', 4, 4, FALSE),
('REF-DIC-01', 'Dictionnaire Larousse', 'Larousse', 'Référence', 1, 1, TRUE);

INSERT INTO adherents (nom, prenom, contact, statut, date_inscription) VALUES
('Koné', 'Awa', '0102030405', 'etudiant', CURDATE()),
('Yao', 'Kouadio', '0708091011', 'eleve', CURDATE());
