<?php
require 'conn.inc.php';

$sparkle->query('truncate user_xp');

$sql = "select * from (
                  select user, SUM(xp) as xp
                  from user_xp
                  group by user
              ) x ";

// select all user goals, selecting the latest added if a user has more than 1
$old_xps = $old->query($sql)->fetchAll();
foreach ($old_xps as $old_xp) {

  // Insert into new db
  $sparkle->prepare("INSERT INTO user_xp (user, xp) VALUES (:user, :xp)")->execute( array(
    'user' => $old_xp['user'],
    'xp' => $old_xp['xp']
  ) );

}





