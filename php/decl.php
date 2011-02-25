<?php
/* -*- coding: utf-8 -*- */
header("Content-Type:  application/json");

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
echo json_encode(array("result"=>true,"file"=>"$pref"));
/*header('Location: index.html');*/
?>