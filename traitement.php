<?php

// =========================================================
// CONNEXION À MYSQL
// =========================================================

$host = "localhost";
$dbname = "gestion_concours";
$user = "root";
$password = "";

try {

    $pdo = new PDO(
        "mysql:host=$host;dbname=$dbname;charset=utf8mb4",
        $user,
        $password
    );

    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

} catch (PDOException $e) {

    die("Erreur de connexion à MySQL : " . $e->getMessage());

}


// =========================================================
// INITIALISATION
// =========================================================

$erreurs = [];


// =========================================================
// TRAITEMENT DU FORMULAIRE
// =========================================================

if ($_SERVER["REQUEST_METHOD"] == "POST")
{

    // =====================================================
    // Récupération des champs
    // =====================================================

    $nom_fr = trim($_POST["nom_fr"]);
    $prenom_fr = trim($_POST["prenom_fr"]);

    $nom_ar = trim($_POST["nom_ar"]);
    $prenom_ar = trim($_POST["prenom_ar"]);

    $date_naissance = trim($_POST["date_naissance"]);

    $cin = strtoupper(trim($_POST["cin"]));

    $date_expiration = trim($_POST["date_expiration"]);

    $email = trim($_POST["email"]);


    // =====================================================
    // ID DU CONCOURS
    // =====================================================

    // TEMPORAIRE :
    // on utilise ici le concours dont l'id est 1.
    // Plus tard, cet ID pourra venir du formulaire.

    $id_concours = 1;


    // =====================================================
    // VÉRIFICATIONS DES CHAMPS
    // =====================================================

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


    // =====================================================
    // VÉRIFICATION DU FICHIER CIN
    // =====================================================

    if (!isset($_FILES["cin_image"]))
    {
        $erreurs[] = "Veuillez joindre une image.";
    }
    else
    {

        if ($_FILES["cin_image"]["error"] != UPLOAD_ERR_OK)
        {
            $erreurs[] = "Erreur lors du téléchargement.";
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


    // =====================================================
    // SI AUCUNE ERREUR
    // =====================================================

    if (empty($erreurs))
    {

        // =================================================
        // CRÉATION DU DOSSIER UPLOADS
        // =================================================

        $dossier_uploads =
            __DIR__ .
            DIRECTORY_SEPARATOR .
            "uploads";


        if (!is_dir($dossier_uploads))
        {
            mkdir($dossier_uploads, 0777, true);
        }


        // =================================================
        // NOM UNIQUE POUR LA CIN
        // =================================================

        $nom_fichier =
            "cin_" .
            date("Ymd_His") .
            "_" .
            bin2hex(random_bytes(4)) .
            "." .
            $extension;


        // Chemin réel sur le serveur
        $chemin_absolu =
            $dossier_uploads .
            DIRECTORY_SEPARATOR .
            $nom_fichier;


        // Chemin relatif qui sera stocké dans MySQL
        $chemin_relatif =
            "uploads/" .
            $nom_fichier;


        // =================================================
        // ENREGISTREMENT DU FICHIER
        // =================================================

        if (
            !move_uploaded_file(
                $_FILES["cin_image"]["tmp_name"],
                $chemin_absolu
            )
        )
        {

            $erreurs[] =
                "Impossible d'enregistrer le fichier.";

        }
        else
        {

            try
            {

                // =========================================
                // INSERTION DANS LA TABLE candidats
                // =========================================

                $requete = $pdo->prepare("
                    INSERT INTO candidats (
                        id_concours,
                        nom,
                        prenom,
                        date_naissance,
                        numero_cin,
                        date_expiration,
                        chemin_cin,
                        email
                    )
                    VALUES (
                        :id_concours,
                        :nom,
                        :prenom,
                        :date_naissance,
                        :numero_cin,
                        :date_expiration,
                        :chemin_cin,
                        :email
                    )
                ");


                $requete->execute([

                    ":id_concours" =>
                        $id_concours,

                    ":nom" =>
                        $nom_fr,

                    ":prenom" =>
                        $prenom_fr,

                    ":date_naissance" =>
                        $date_naissance,

                    ":numero_cin" =>
                        $cin,

                    ":date_expiration" =>
                        $date_expiration,

                    ":chemin_cin" =>
                        $chemin_relatif,

                    ":email" =>
                        $email

                ]);


                // =========================================
                // RÉCUPÉRATION DE L'ID CANDIDAT
                // =========================================

                $id_candidat = $pdo->lastInsertId();


                // =========================================
                // AFFICHAGE DE LA CONFIRMATION
                // =========================================

                ?>

                <!DOCTYPE html>

                <html lang="fr">

                <head>

                    <meta charset="UTF-8">

                    <title>
                        Inscription enregistrée
                    </title>

                </head>

                <body>

                    <h2>
                        Inscription enregistrée avec succès.
                    </h2>

                    <p>
                        Identifiant candidat :
                        <strong>
                            <?= htmlspecialchars($id_candidat) ?>
                        </strong>
                    </p>

                    <p>
                        Votre dossier a bien été enregistré.
                    </p>

                    <p>
                        La vérification de votre CIN sera effectuée
                        automatiquement.
                    </p>

                    <br>

                    <a href="formulaire.php">
                        Retour au formulaire
                    </a>

                </body>

                </html>

                <?php

            }
            catch (PDOException $e)
            {

                // =========================================
                // SI MYSQL REFUSE L'INSERTION
                // =========================================

                // Suppression du fichier déjà enregistré
                // puisque le candidat n'a pas été enregistré
                // dans la base.

                if (file_exists($chemin_absolu))
                {
                    unlink($chemin_absolu);
                }


                $erreurs[] =
                    "Erreur lors de l'enregistrement dans la base de données.";

                // Pour afficher l'erreur exacte pendant
                // le développement, tu peux temporairement
                // utiliser :
                //
                // $erreurs[] = $e->getMessage();

            }

        }

    }


    // =====================================================
    // AFFICHAGE DES ERREURS
    // =====================================================

    if (!empty($erreurs))
    {
        include("formulaire.php");
    }

}
else
{
    include("formulaire.php");
}

?>