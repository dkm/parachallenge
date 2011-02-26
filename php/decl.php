<?php
/* -*- coding: utf-8 -*- */
header("Content-Type:  application/json");

$login = $_POST['login'];
$password = $_POST['password'];
$cross = $_POST['cross'];
$lastb = $_POST['lastwpt'];
$date = $_POST['date'];

$valid = true;

/*
 * check login/pass
 */
/* if ($login == "failure"){ */
/*   echo json_encode(array("result"=>false, "reason"=>"bad login")); */
/*   return; */
/*  } */

/*
 * check valid data
 */

if (! $valid){
  echo json_encode(array("result"=>false, "reason"=>"bad data"));
  return;
}

$str = "[declaration] \n" .
       "pilot : " . $login . "\n" .
       "date : " . $date . "\n" .
       "cross : " . $cross . "\n" .
       "last_balise : " . $lastb . "\n";

//echo $str;

$pref = strftime("%d-%m-%Y") . "--" . $login . "--" . $cross . "--";

$fname = tempnam("declarations", $pref);
$handle = fopen($fname, "w");
fwrite($handle, $str);
fclose($handle);

chmod($fname, 0644);
echo json_encode(array("result"=>true,"file"=>"$fname"));
/*header('Location: index.html');*/
?>