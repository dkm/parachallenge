<?php
header("Content-Type: text/plain");

$login = $_POST['login'];
$cross = $_POST['cross'];
$lastb = $_POST['lastwpt'];

$str = "[declaration] \n" .
       "pilot : " . $login . "\n" .
       "date : " . "12/12/12 \n" .
       "cross : " . $cross . "\n" .
       "last_balise : " . $lastb . "\n";

//echo $str;

$pref = strftime("%d-%m-%Y") . "--" . $login . "--" . $cross . "--";

$fname = tempnam("declarations", $pref);
$handle = fopen($fname, "w");
fwrite($handle, $str);
fclose($handle);

echo "Pour l'instant, tu as que �a comme retour. Mais ton vol devrait �tre pris en compte.\n";
echo "Pour info, garde �a comme �preuve�, �a peut aider en cas de bug:\n$fname\n";
/*header('Location: index.html');*/
?>