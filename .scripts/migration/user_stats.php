<?php
require 'conn.inc.php';

$sparkle->query('truncate user_stats');

$sql = "select * from (
                  select user, name, SUM(value) as value
                  from user_stats
                  group by user, name
              ) x";

// select all user goals, selecting the latest added if a user has more than 1
$old_stats = $old->query($sql)->fetchAll();
foreach ($old_stats as $old_stat) {

  // Insert into new db
  $sparkle->prepare("INSERT INTO user_stats (user, name, value) VALUES (:user, :name, :value)")->execute( array(
    'user' => $old_stat['user'],
    'name' => $old_stat['name'],
    'value' => $old_stat['value']
  ) );

}





