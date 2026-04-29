import sqlite3
import os
import json

# Chemin de la base de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "digitallife.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS pays (
            id_pays      INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_pays     TEXT NOT NULL,
            code_devise  TEXT NOT NULL,
            symbole      TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS universite (
            id_universite   INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_universite  TEXT NOT NULL,
            ville           TEXT NOT NULL,
            id_pays         INTEGER NOT NULL,
            FOREIGN KEY (id_pays) REFERENCES pays(id_pays)
        );

        CREATE TABLE IF NOT EXISTS etudiant (
            id_etudiant     INTEGER PRIMARY KEY AUTOINCREMENT,
            age             INTEGER NOT NULL,
            genre           TEXT NOT NULL,
            filiere         TEXT NOT NULL,
            niveau          TEXT NOT NULL,
            id_universite   INTEGER NOT NULL,
            FOREIGN KEY (id_universite) REFERENCES universite(id_universite)
        );

        CREATE TABLE IF NOT EXISTS reponse (
            id_reponse       INTEGER PRIMARY KEY AUTOINCREMENT,
            id_etudiant      INTEGER NOT NULL,
            date_soumission  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_etudiant) REFERENCES etudiant(id_etudiant)
        );

        CREATE TABLE IF NOT EXISTS habitudes_numeriques (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            id_reponse          INTEGER NOT NULL,
            temps_ecran_h       REAL NOT NULL,
            reseaux_sociaux     TEXT NOT NULL,
            types_connexion     TEXT NOT NULL,
            depenses_internet   REAL NOT NULL,
            appareil_principal  TEXT NOT NULL,
            FOREIGN KEY (id_reponse) REFERENCES reponse(id_reponse)
        );

        CREATE TABLE IF NOT EXISTS bien_etre (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            id_reponse              INTEGER NOT NULL,
            qualite_sommeil         INTEGER NOT NULL,
            heures_sommeil          REAL NOT NULL,
            niveau_stress           INTEGER NOT NULL,
            heures_revision         REAL NOT NULL,
            satisfaction_academique INTEGER NOT NULL,
            FOREIGN KEY (id_reponse) REFERENCES reponse(id_reponse)
        );
    """)

    conn.commit()
    conn.close()


def seed_pays():
    conn = get_connection()
    cursor = conn.cursor()

    pays_data = [
        ("Cameroun",        "XAF", "FCFA"),
        ("Sénégal",         "XOF", "FCFA"),
        ("Côte d'Ivoire",   "XOF", "FCFA"),
        ("Mali",            "XOF", "FCFA"),
        ("France",          "EUR", "€"),
        ("Allemagne",       "EUR", "€"),
        ("Canada",          "CAD", "CA$"),
        ("Hong Kong",       "HKD", "HK$"),
        ("Autre",           "---", "---"),
    ]

    cursor.execute("SELECT COUNT(*) FROM pays")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO pays (nom_pays, code_devise, symbole) VALUES (?, ?, ?)",
            pays_data
        )

    conn.commit()
    conn.close()


def insert_universite(nom, ville, id_pays):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_universite FROM universite
        WHERE nom_universite = ? AND id_pays = ?
    """, (nom, id_pays))

    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]

    cursor.execute("""
        INSERT INTO universite (nom_universite, ville, id_pays)
        VALUES (?, ?, ?)
    """, (nom, ville, id_pays))

    conn.commit()
    id_new = cursor.lastrowid
    conn.close()
    return id_new


def insert_etudiant(age, genre, filiere, niveau, id_universite):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO etudiant (age, genre, filiere, niveau, id_universite)
        VALUES (?, ?, ?, ?, ?)
    """, (age, genre, filiere, niveau, id_universite))
    conn.commit()
    id_new = cursor.lastrowid
    conn.close()
    return id_new


def insert_reponse(id_etudiant):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reponse (id_etudiant)
        VALUES (?)
    """, (id_etudiant,))
    conn.commit()
    id_new = cursor.lastrowid
    conn.close()
    return id_new


def insert_habitudes(id_reponse, temps_ecran, reseaux,
                     connexions, depenses, appareil):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO habitudes_numeriques
        (id_reponse, temps_ecran_h, reseaux_sociaux,
         types_connexion, depenses_internet, appareil_principal)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        id_reponse,
        temps_ecran,
        json.dumps(reseaux),
        json.dumps(connexions),
        depenses,
        appareil
    ))
    conn.commit()
    conn.close()


def insert_bien_etre(id_reponse, qualite_sommeil, heures_sommeil,
                     niveau_stress, heures_revision, satisfaction):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bien_etre
        (id_reponse, qualite_sommeil, heures_sommeil,
         niveau_stress, heures_revision, satisfaction_academique)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id_reponse, qualite_sommeil, heures_sommeil,
          niveau_stress, heures_revision, satisfaction))
    conn.commit()
    conn.close()


def get_all_pays():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_pays, nom_pays, code_devise, symbole FROM pays")
    rows = cursor.fetchall()
    conn.close()
    return rows


def init_db():
    create_tables()
    seed_pays()