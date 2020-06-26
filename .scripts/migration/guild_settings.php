<?php
require 'conn.inc.php';

$sparkle->query('truncate guild_settings');

$old_guild_settings = $old->query('select * from guild_settings')->fetchAll();
foreach($old_guild_settings as $setting) {

  // Insert into new db
  $sparkle->prepare("INSERT INTO guild_settings (guild, setting, value) VALUES (:guild, :setting, :value)")->execute( array(
    'guild' => $setting['guild'],
    'setting' => $setting['setting'],
    'value' => $setting['value']
  ) );

}

// Then the ones stored in settings table, such as prefixes.
$old_settings = $old->query('select * from settings')->fetchAll();
foreach ($old_settings as $setting) {

  $value = json_decode($setting['settings']);
  if (isset($value->prefix)) {
    $value = $value->prefix;

    // Insert into new db
    $sparkle->prepare("INSERT INTO guild_settings (guild, setting, value) VALUES (:guild, :setting, :value)")->execute( array(
      'guild' => $setting['guild'],
      'setting' => 'prefix',
      'value' => $value
    ) );

  }

}


