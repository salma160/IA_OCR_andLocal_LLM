<?php

$erreurs = [];

if ($_SERVER["REQUEST_METHOD"] == "POST")
{

    // =========================================================
    // RÉCUPÉRATION DES CHAMPS
    // =========================================================

    $nom_fr = trim($_POST["nom_fr"] ?? "");
    $prenom_fr = trim($_POST["prenom_fr"] ?? "");

    $nom_ar = trim($_POST["nom_ar"] ?? "");
    $prenom_ar = trim($_POST["prenom_ar"] ?? "");

    $date_naissance = trim($_POST["date_naissance"] ?? "");

    $cin = strtoupper(trim($_POST["cin"] ?? ""));

    $date_expiration = trim($_POST["date_expiration"] ?? "");

    $email = trim($_POST["email"] ?? "");


    // =========================================================
    // VÉRIFICATIONS DES CHAMPS
    // =========================================================

    if (empty($nom_fr))
        $erreurs[] = "Veuillez saisir le nom (français).";

    if (empty($prenom_fr))
        $erreurs[] = "Veuillez saisir le prénom (français).";

    if (empty($nom_ar))
        $erreurs[] = "Veuillez saisir le nom (arabe).";

    if (empty($prenom_ar))
        $erreurs[] = "Veuillez saisir le prénom (arabe).";

    if (empty($date_naissance))
        $erreurs[] = "Veuillez saisir la date de naissance.";

    if (empty($cin))
        $erreurs[] = "Veuillez saisir le numéro de CIN.";

    if (empty($date_expiration))
        $erreurs[] = "Veuillez saisir la date d'expiration.";

    if (empty($email))
        $erreurs[] = "Veuillez saisir votre adresse e-mail.";

    if (
        !empty($email) &&
        !filter_var($email, FILTER_VALIDATE_EMAIL)
    )
    {
        $erreurs[] = "Adresse e-mail invalide.";
    }


    // =========================================================
    // VÉRIFICATION DU FICHIER CIN
    // =========================================================

    if (!isset($_FILES["cin_image"]))
    {
        $erreurs[] = "Veuillez joindre une image.";
    }
    else
    {

        if ($_FILES["cin_image"]["error"] != UPLOAD_ERR_OK)
        {
            $erreurs[] = "Erreur lors du téléchargement du fichier.";
        }
        else
        {

            $extension = strtolower(
                pathinfo(
                    $_FILES["cin_image"]["name"],
                    PATHINFO_EXTENSION
                )
            );

            if (
                $extension != "jpg" &&
                $extension != "jpeg" &&
                $extension != "pdf"
            )
            {
                $erreurs[] =
                    "Le fichier doit être au format JPG, JPEG ou PDF.";
            }

        }

    }


    // =========================================================
    // S'IL N'Y A AUCUNE ERREUR
    // =========================================================

    if (empty($erreurs))
    {

        // =====================================================
        // CONNEXION À MYSQL
        // =====================================================

        $connexion = new mysqli(
            "localhost",
            "root",
            "",
            "gestion_concours"
        );

        if ($connexion->connect_error)
        {
            die(
                "Erreur de connexion à MySQL : "
                . $connexion->connect_error
            );
        }

        $connexion->set_charset("utf8mb4");


        // =====================================================
        // RÉCUPÉRATION DU CONCOURS ACTUEL
        // =====================================================

        $requete_concours = "
            SELECT id_concours_actuel
            FROM configuration
            WHERE id_configuration = 1
        ";

        $resultat_concours =
            $connexion->query($requete_concours);


        if (
            !$resultat_concours ||
            $resultat_concours->num_rows == 0
        )
        {
            $connexion->close();

            die(
                "Aucun concours actuel n'est configuré."
            );
        }


        $ligne_concours =
            $resultat_concours->fetch_assoc();

        $id_concours =
            $ligne_concours["id_concours_actuel"];


        // =====================================================
        // CRÉATION DU DOSSIER uploads
        // =====================================================

        $dossier_uploads =
            __DIR__ . DIRECTORY_SEPARATOR . "uploads";


        if (!is_dir($dossier_uploads))
        {
            if (
                !mkdir(
                    $dossier_uploads,
                    0777,
                    true
                )
            )
            {
                $connexion->close();

                die(
                    "Impossible de créer le dossier uploads."
                );
            }
        }


        // =====================================================
        // NOM UNIQUE DU FICHIER
        // =====================================================

        $nom_fichier =
            uniqid("cin_", true)
            . "."
            . $extension;


        // =====================================================
        // CHEMIN ABSOLU
        // =====================================================

        $chemin_absolu =
            $dossier_uploads
            . DIRECTORY_SEPARATOR
            . $nom_fichier;


        // =====================================================
        // CHEMIN RELATIF À STOCKER DANS MYSQL
        // =====================================================

        $chemin_relatif =
            "uploads/"
            . $nom_fichier;


        // =====================================================
        // ENREGISTREMENT DU FICHIER
        // =====================================================

        if (
            !move_uploaded_file(
                $_FILES["cin_image"]["tmp_name"],
                $chemin_absolu
            )
        )
        {
            $connexion->close();

            die(
                "Impossible d'enregistrer le fichier CIN."
            );
        }


        // =====================================================
        // INSERTION DU CANDIDAT
        // =====================================================

        $requete = "
            INSERT INTO candidats
            (
                id_concours,
                nom,
                prenom,
                date_naissance,
                numero_cin,
                date_expiration,
                chemin_cin
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ";


        $stmt =
            $connexion->prepare($requete);


        if (!$stmt)
        {
            $connexion->close();

            die(
                "Erreur lors de la préparation SQL : "
                . $connexion->error
            );
        }


        $stmt->bind_param(
            "issssss",
            $id_concours,
            $nom_fr,
            $prenom_fr,
            $date_naissance,
            $cin,
            $date_expiration,
            $chemin_relatif
        );


        if (!$stmt->execute())
        {
            $stmt->close();
            $connexion->close();

            die(
                "Erreur lors de l'enregistrement du candidat : "
                . $stmt->error
            );
        }


        // =====================================================
        // ID DU CANDIDAT CRÉÉ
        // =====================================================

        $id_candidat =
            $connexion->insert_id;


        // =====================================================
        // FERMETURE MYSQL
        // =====================================================

        $stmt->close();

        $connexion->close();


        // =====================================================
        // SUCCÈS
        // =====================================================

        ?>

        <!DOCTYPE html>

        <html lang="fr">

        <head>

            <meta charset="UTF-8">

            <title>Inscription réussie</title>

        </head>

        <body>

            <h2>
                Inscription enregistrée avec succès.
            </h2>

            <p>
                Votre candidature a bien été enregistrée.
            </p>

            <p>
                Numéro de candidature :
                <?= htmlspecialchars($id_candidat) ?>
            </p>

            <p>
                Le traitement de votre CIN sera effectué automatiquement.
            </p>

            <br>

            <a href="formulaire.php">
                Retour au formulaire
            </a>

        </body>

        </html>

        <?php

    }
    else
    {

        // =====================================================
        // AFFICHAGE DU FORMULAIRE AVEC LES ERREURS
        // =====================================================

        include("formulaire.php");

    }

}
else
{

    // =========================================================
    // ACCÈS DIRECT À LA PAGE
    // =========================================================

    include("formulaire.php");

}

?>