<?php
require 'conn.inc.php';

$sparkle->query('truncate user_records');

$sql = "select user, record, MAX(value) as value
from user_records
group by user";

// select all user goals, selecting the latest added if a user has more than 1
$old_records = $old->query($sql)->fetchAll();
foreach ($old_records as $old_record) {

  // Insert into new db
  $sparkle->prepare("INSERT INTO user_records (user, record, value) VALUES (:user, :record, :value)")->execute( array(
    'user' => $old_record['user'],
    'record' => $old_record['record'],
    'value' => $old_record['value']
  ) );

}
