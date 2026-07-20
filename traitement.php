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
    // Vérification de l'image
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
                pathinfo($_FILES["cin_image"]["name"], PATHINFO_EXTENSION)
            );

            if($extension != "jpg" && $extension != "jpeg")
            {
                $erreurs[] = "L'image doit être au format JPG ou JPEG.";
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

        $image =  __DIR__ . "\\uploads\\cin.jpg";;

        move_uploaded_file(
            $_FILES["cin_image"]["tmp_name"],
            $image
        );

        //=====================================================
        // Exécution de Python
        //=====================================================

       

        $commande =
        'python ' .
        escapeshellarg("D:\\sujet_stageJM2\\main.py") . " " .
        escapeshellarg($image) . " " .
        escapeshellarg($nom_fr) . " " .
        escapeshellarg($prenom_fr) . " " .
        escapeshellarg($nom_ar) . " " .
        escapeshellarg($prenom_ar) . " " .
        escapeshellarg($date_naissance) . " " .
        escapeshellarg($cin) . " " .
        escapeshellarg($date_expiration);

// pclose(popen($commande, "r"));

// include("confirmation.php");
echo "<pre>";
echo $commande;
echo "</pre>";

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