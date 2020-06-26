<?php
require 'conn.inc.php';

$sparkle->query('truncate projects');

$sql = " select user, name, shortname, completed, MAX(words) as words
from projects
group by user, shortname";

$old_projects = $old->query($sql)->fetchAll();

foreach ($old_projects as $old_project) {

  // Are there any records for this user and shortname which are completed?
  $st = $old->prepare('select MAX(completed) as completed from projects where user = :user and shortname = :shortname and completed > 0');
  $st->execute([
    'user' => $old_project['user'],
    'shortname' => $old_project['shortname']
    ]);
  $check = $st->fetch();

  $completed = ($check['completed']) ? $check['completed'] : 0;

  // Insert into new db
  $sparkle->prepare("INSERT INTO projects (user, name, shortname, words, completed) VALUES (:user, :name, :shortname, :words, :completed)")->execute( array(
    'user' => $old_project['user'],
    'name' => $old_project['name'],
    'shortname' => $old_project['shortname'],
    'words' => $old_project['words'],
    'completed' => $completed
  ) );

}
