-- schema.sql

drop database if exists dvplatform;

create database dvplatform;

use dvplatform;

grant select, insert, update, delete on dvplatform.* to 'www-data'@'localhost' identified by 'www-data';

create table users (
    `id` varchar(50) not null,
    `email` varchar(50) not null,
    `passwd` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `image` varchar(500) not null,
    `created_at` real not null,
    unique key `idx_email` (`email`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table projects (
    `id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `title` varchar(50) not null,
    `summary` mediumtext not null,
    `created_at` real not null,
    `status` bool not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table charts (
    `id` varchar(50) not null,
    `project_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `index` integer not null,
    `status` bool not null,
    `created_at` real not null,
    `type` varchar(50) not null,
    `option` mediumtext not null,
    `description` mediumtext not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;