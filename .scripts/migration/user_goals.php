<?php
require 'conn.inc.php';

$sparkle->query('truncate user_goals');

$sql = "select * from user_goals where id in (
    select max(id) as id
    from user_goals
    group by user
) order by user desc";

// select all user goals, selecting the latest added if a user has more than 1
$old_goals = $old->query($sql)->fetchAll();
foreach ($old_goals as $old_goal) {

  // Insert into new db
  $sparkle->prepare("INSERT INTO user_goals (user, type, goal, current, completed, reset) VALUES (:user, :type, :goal, 0, 0, 0)")->execute( array(
    'user' => $old_goal['user'],
    'type' => $old_goal['type'],
    'goal' => $old_goal['goal']
  ) );

}
