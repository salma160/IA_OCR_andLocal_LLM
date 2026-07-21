<?php if(!empty($erreurs)): ?>

<div class="erreurs">

    <ul>

        <?php foreach($erreurs as $erreur): ?>

            <li><?= htmlspecialchars($erreur) ?></li>

        <?php endforeach; ?>

    </ul>

</div>

<?php endif; ?>

<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Formulaire</title>
</head>
<body>
   

   <form action="traitement.php" method="POST" enctype="multipart/form-data">

    <h2>Vérification de votre Carte Nationale d'Identité</h2>

    <label>Nom (français)</label><br>
    <input type="text" name="nom_fr" required><br><br>

    <label>Prénom (français)</label><br>
    <input type="text" name="prenom_fr" required><br><br>

    <label>Nom (arabe)</label><br>
    <input type="text" name="nom_ar" dir="rtl" required><br><br>

    <label>Prénom (arabe)</label><br>
    <input type="text" name="prenom_ar" dir="rtl" required><br><br>

    <label>Date de naissance</label><br>
    <input type="date" name="date_naissance" required><br><br>

    <label>Numéro de la CIN</label><br>
    <input type="text" name="cin" required><br><br>

    <label>Date d'expiration de la CIN</label><br>
    <input type="date" name="date_expiration" required><br><br>

    <label>Adresse e-mail</label><br>
    <input
        type="email"
        name="email"
        placeholder="exemple@domaine.com"
        required
    ><br><br>

    <label>Déposer le PDF de votre CIN (face avant)</label><br>
    <input
        type="file"
        name="cin_image"
        accept=".jpg,.jpeg"
        required
    ><br><br>

    <h6>

        Attention : le document déposé doit être au format <strong>PDF/JPEG/JPG</strong>  et contenir uniquement la face avant de votre Carte Nationale d'Identité.

        Pour garantir une extraction optimale des informations, assurez-vous que la carte est bien centrée, que l'image est nette, suffisamment éclairée, sur un fond uniforme et que les quatre coins de la carte sont visibles.
    </h6>

    <br>

    <button type="submit">
        Vérifier mon identité
    </button>

</form>
</body>
</html>