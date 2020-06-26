<?php
require 'conn.inc.php';

$sparkle->query('truncate user_settings');

// No duplicates in the data, so simple insert.

// select all user goals, selecting the latest added if a user has more than 1
$old_settings = $old->query('select * from user_settings')->fetchAll();
foreach ($old_settings as $old_setting) {

  // Only if it's a valid timezone.
  if ($old_setting['setting'] == 'timezone' && !preg_match('/^[a-z]+\/[a-z]+$/i', $old_setting['value'])) {
    continue;
  }

  // Insert into new db
  $sparkle->prepare("INSERT INTO user_settings (user, guild, setting, value) VALUES (:user, NULL, :setting, :value)")->execute( array(
    'user' => $old_setting['user'],
    'setting' => $old_setting['setting'],
    'value' => $old_setting['value']
  ) );

}
