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

$valid = true;
$reason = "Invalid - BUG";

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
} else {

/*
 * check login/pass
 */
/* if ($login == "failure"){ */
/*   echo json_encode(array("result"=>false, "reason"=>"bad login")); */
/*   return; */
/*  } */

/*
 * php bb stuff
 */
define('IN_PHPBB', true);
define('PHPBB_ROOT_PATH', "../forum/");

$phpEx = substr(strrchr(__FILE__, '.'), 1);
$phpbb_root_path = (defined('PHPBB_ROOT_PATH')) ? PHPBB_ROOT_PATH : './';

include($phpbb_root_path . 'common.' . $phpEx);

// because php include resets these vars.
$login = $_POST['login'];
$password = $_POST['password'];

$r = $auth->login($login, $password);

if ($r['status'] != LOGIN_SUCCESS) {
   $valid = false;
   $reason = "login/mot de passe incorrect:" . $r['error_msg'];
}
}

/*
 * check valid data
 */

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