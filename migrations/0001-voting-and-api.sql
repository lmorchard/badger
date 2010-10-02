DROP TABLE IF EXISTS `votes`;
CREATE TABLE `votes` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `content_type_id` integer NOT NULL,
    `object_id` integer UNSIGNED NOT NULL,
    `vote` smallint NOT NULL,
    UNIQUE (`user_id`, `content_type_id`, `object_id`)
)
;
DROP TABLE IF EXISTS `piston_nonce`;
CREATE TABLE `piston_nonce` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `token_key` varchar(18) NOT NULL,
    `consumer_key` varchar(18) NOT NULL,
    `key` varchar(255) NOT NULL
)
;
DROP TABLE IF EXISTS `piston_consumer`;
CREATE TABLE `piston_consumer` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(255) NOT NULL,
    `description` longtext NOT NULL,
    `key` varchar(18) NOT NULL,
    `secret` varchar(32) NOT NULL,
    `status` varchar(16) NOT NULL,
    `user_id` integer
)
;
ALTER TABLE `piston_consumer` ADD CONSTRAINT `user_id_refs_id_aad30107` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
DROP TABLE IF EXISTS `piston_token`;
CREATE TABLE `piston_token` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `key` varchar(18) NOT NULL,
    `secret` varchar(32) NOT NULL,
    `verifier` varchar(10) NOT NULL,
    `token_type` integer NOT NULL,
    `timestamp` integer NOT NULL,
    `is_approved` bool NOT NULL,
    `user_id` integer,
    `consumer_id` integer NOT NULL,
    `callback` varchar(255),
    `callback_confirmed` bool NOT NULL
)
;
ALTER TABLE `piston_token` ADD CONSTRAINT `user_id_refs_id_efc02d17` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `piston_token` ADD CONSTRAINT `consumer_id_refs_id_85f42355` FOREIGN KEY (`consumer_id`) REFERENCES `piston_consumer` (`id`);

