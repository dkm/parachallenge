<?php
/* -*- coding: utf-8 -*- */
header("Content-Type:  application/json");

$login = $_POST['login'];
$password = $_POST['password'];
$cross = $_POST['cross'];
$lastb = $_POST['lastwpt'];
$date = $_POST['date'];

$group = $_POST['group'];
$cat = $_POST['cat'];

$bonus = $_POST['bonus'];
$comments = $_POST['comments'];

$valid = true;
 
$reason = "Invalid - BUG";

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

if (empty($login) || empty($password)) {
   $valid = false;
   $reason = "Manque login/password";
} else if (empty($cross) && $cross != 0){
   $valid = false;
   $reason = "Manque cross";
} else if (empty($group)) {
 $group = 1;
} else if (empty($cat)){
 $valid = false;
 $reason = "Manque cat du parapente";
} else if (empty($lastb) && $lastb != 0 ){
   $valid = false;
   $reason = "Manque balise de fin";
}

if (! $valid){
  echo json_encode(array("result"=>false, "reason"=>$reason));
  return;
}

$str = "[declaration] \n" .
       "pilot : " . $login . "\n" .
       "date : " . $date . "\n" .
       "cross : " . $cross . "\n" .
       "last_balise : " . $lastb . "\n" .
       "cat : " . $cat . "\n" .
       "group : " . $group . "\n";

if ( $comments) {
  $str .= "comments : " . $comments . "\n";
}

$str .= "bonus : ";

if (! empty($bonus)){
   $str .= implode(',', $bonus);
} 

$str .= "\n";

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