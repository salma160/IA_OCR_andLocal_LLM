-- =========================================================
-- BASE DE DONNÉES : gestion_concours
-- Projet : validation automatique des CIN
-- SGBD : MySQL 8.4.7
-- =========================================================


USE gestion_concours;

CREATE TABLE concours (
    id_concours INT AUTO_INCREMENT PRIMARY KEY,
    nom_concours VARCHAR(200) NOT NULL,
    date_concours DATE
);



-- =========================================================
-- TABLE : candidats
-- Contient les informations saisies par PHP.
-- =========================================================

CREATE TABLE candidats (
    id_candidat INT AUTO_INCREMENT PRIMARY KEY,

    -- Concours auquel appartient le candidat
    id_concours INT NOT NULL,

    -- Informations personnelles
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE NOT NULL,
    

    -- Informations de la CIN
    numero_cin VARCHAR(20) NOT NULL,
    date_expiration DATE NOT NULL,

    -- Chemin relatif vers le fichier CIN
    chemin_cin VARCHAR(255) NOT NULL,

    -- Date et heure d'inscription
    date_inscription DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Relation avec la table concours
    CONSTRAINT fk_candidat_concours
        FOREIGN KEY (id_concours)
        REFERENCES concours(id_concours)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
show tables;

-- =========================================================
-- TABLE : verifications
-- Contient les informations extraites par Python/OCR
-- ainsi que le résultat de la vérification.
-- =========================================================

CREATE TABLE verifications (
    id_verification INT AUTO_INCREMENT PRIMARY KEY,

    -- Candidat concerné par la vérification
    id_candidat INT NOT NULL UNIQUE,

    -- Informations extraites de la CIN par OCR
    nom_ocr VARCHAR(100),
    prenom_ocr VARCHAR(100),
    numero_cin_ocr VARCHAR(20),
    date_naissance_ocr DATE,
    date_expiration_ocr DATE,

    -- Résultat de la vérification
    statut ENUM(
        'EN_ATTENTE',
        'VALIDE',
        'NON_VALIDE',
        'DOCUMENT_INVALIDE'
    ) NOT NULL DEFAULT 'EN_ATTENTE',

    -- Date et heure du traitement
    date_verification DATETIME,

    -- Relation avec la table candidats
    CONSTRAINT fk_verification_candidat
        FOREIGN KEY (id_candidat)
        REFERENCES candidats(id_candidat)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE configuration (
    id_configuration INT PRIMARY KEY,
    id_concours_actuel INT NOT NULL,

    CONSTRAINT fk_configuration_concours
        FOREIGN KEY (id_concours_actuel)
        REFERENCES concours(id_concours)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
INSERT INTO concours (nom_concours, date_concours)
VALUES ('Concours 1', CURRENT_DATE);

INSERT INTO configuration
(id_configuration, id_concours_actuel)
VALUES
(1, 1);



DROP TABLE IF EXISTS verifications;

CREATE TABLE verifications (
    id_verification INT AUTO_INCREMENT PRIMARY KEY,

    id_candidat INT NOT NULL UNIQUE,

    nom_ocr VARCHAR(100),
    prenom_ocr VARCHAR(100),
    numero_cin_ocr VARCHAR(20),
    date_naissance_ocr DATE,
    date_expiration_ocr DATE,

    statut ENUM(
        'EN_ATTENTE',
        'VALIDE',
        'NON_VALIDE',
        'DOCUMENT_INVALIDE')
    -- ) NOT NULL DEFAULT 'EN_ATTENTE',

    date_verification DATETIME,

    CONSTRAINT fk_verification_candidat
        FOREIGN KEY (id_candidat)
        REFERENCES candidats(id_candidat)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
ALTER TABLE verifications ENGINE = InnoDB;