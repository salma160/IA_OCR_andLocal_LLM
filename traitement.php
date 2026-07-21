<?php

$erreurs = [];

if ($_SERVER["REQUEST_METHOD"] == "POST")
{

    //=========================================================
    // Récupération des champs
    //=========================================================

    $nom_fr = trim($_POST["nom_fr"]);
    $prenom_fr = trim($_POST["prenom_fr"]);

    $nom_ar = trim($_POST["nom_ar"]);
    $prenom_ar = trim($_POST["prenom_ar"]);

    $date_naissance = trim($_POST["date_naissance"]);

    $cin = strtoupper(trim($_POST["cin"]));

    $date_expiration = trim($_POST["date_expiration"]);

    $email = trim($_POST["email"]);


    //=========================================================
    // Vérifications
    //=========================================================

    if(empty($nom_fr))
        $erreurs[] = "Veuillez saisir le nom (français).";

    if(empty($prenom_fr))
        $erreurs[] = "Veuillez saisir le prénom (français).";

    if(empty($nom_ar))
        $erreurs[] = "Veuillez saisir le nom (arabe).";

    if(empty($prenom_ar))
        $erreurs[] = "Veuillez saisir le prénom (arabe).";

    if(empty($date_naissance))
        $erreurs[] = "Veuillez saisir la date de naissance.";

    if(empty($cin))
        $erreurs[] = "Veuillez saisir le numéro de CIN.";

    if(empty($date_expiration))
        $erreurs[] = "Veuillez saisir la date d'expiration.";

    if(empty($email))
        $erreurs[] = "Veuillez saisir votre adresse e-mail.";

    if(!empty($email) && !filter_var($email, FILTER_VALIDATE_EMAIL))
        $erreurs[] = "Adresse e-mail invalide.";


    //=========================================================
    // Vérification du fichier
    //=========================================================

    if(!isset($_FILES["cin_image"]))
    {
        $erreurs[] = "Veuillez joindre une image.";
    }
    else
    {

        if($_FILES["cin_image"]["error"] != UPLOAD_ERR_OK)
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

            if(
                $extension != "jpg" &&
                $extension != "jpeg" &&
                $extension != "pdf"
            )
            {
                $erreurs[] = "Le fichier doit être au format JPG, JPEG ou PDF.";
            }

        }

    }


    //=========================================================
    // Si aucune erreur
    //=========================================================

    if(empty($erreurs))
    {

        if(!is_dir("uploads"))
        {
            mkdir("uploads");
        }

        $image = __DIR__ . "\\uploads\\cin." . $extension;

        move_uploaded_file(
            $_FILES["cin_image"]["tmp_name"],
            $image
        );


        //=====================================================
        // Commande Python
        //=====================================================

        $commande =
        '"C:\\Users\\mlk\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" ' .
        escapeshellarg(__DIR__ . "\\main.py") . " " .
        escapeshellarg($image) . " " .
        escapeshellarg($nom_fr) . " " .
        escapeshellarg($prenom_fr) . " " .
        escapeshellarg($nom_ar) . " " .
        escapeshellarg($prenom_ar) . " " .
        escapeshellarg($date_naissance) . " " .
        escapeshellarg($cin) . " " .
        escapeshellarg($date_expiration);

        ?>

        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Commande Python</title>
        </head>
        <body>

            <h2>Fichier enregistré avec succès.</h2>

            <p>Copiez cette commande et exécutez-la dans le terminal VS Code :</p>

            <textarea rows="8" cols="180" readonly><?=
                htmlspecialchars($commande)
            ?></textarea>

            <br><br>

            <a href="formulaire.php">
                Retour au formulaire
            </a>

        </body>
        </html>

        <?php

    }
    else
    {

        include("formulaire.php");

    }

}
else
{

    include("formulaire.php");

}

?>