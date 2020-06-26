<?php
try {
  $old = new PDO("mysql:host=localhost;dbname=old", 'root', '');
  $old->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  $old->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch(PDOException $e) {
  echo $e->getMessage();
  exit;
}

try {
  $sparkle = new PDO("mysql:host=localhost;dbname=sparkle", 'root', '');
  $sparkle->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  $sparkle->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch(PDOException $e) {
  echo $e->getMessage();
  exit;
}