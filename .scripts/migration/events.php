<?php
require 'conn.inc.php';

$sparkle->query('truncate events');
$sparkle->query('truncate user_events');


// Get all the old events
$old_events = $old->query('select * from events')->fetchAll();
foreach ($old_events as $old_event){

    echo 'Old event for guild: ' . $old_event['guild'] . '\n';

    // Insert into new db
    $sparkle->prepare("INSERT INTO events (guild, channel, title, description, img, startdate, enddate, started, ended)
        VALUES (:guild, :channel, :title, :desc, :img, :start, :end, :started, :ended)")->execute( array(
        'guild' => $old_event['guild'],
        'channel' => $old_event['channel'],
        'title' => $old_event['title'],
        'desc' => $old_event['description'],
        'img' => $old_event['img'],
        'start' => $old_event['startdate'],
        'end' => $old_event['enddate'],
        'started' => $old_event['started'],
        'ended' => $old_event['ended']
        ) );

    $st = $sparkle->prepare('select * from events where guild = ?');
    $st->execute([$old_event['guild']]);
    $get = $st->fetch();

    echo 'Inserted record into sparkle.events: ' . $get['id'] . '\n';

    // Get users and insert them as well
    $st = $old->prepare('select * from user_events where event = ?');
    $st->execute([$old_event['id']]);
    $old_users = $st->fetchAll();
    foreach ($old_users as $old_user){

        $sparkle->prepare('insert into user_events (event, user, words) VALUES (:event, :user, :words)')->execute([
        'event' => $get['id'],
        'user' => $old_user['user'],
        'words' => $old_user['words']
        ]);

        echo 'Inserted user ' . $old_user['user'] . ' onto new event ' . $get['id'] . '\n';

    }


}