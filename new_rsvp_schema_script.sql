-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema rsvp_schema
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `rsvp_schema` ;

-- -----------------------------------------------------
-- Schema rsvp_schema
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `rsvp_schema` DEFAULT CHARACTER SET utf8 ;
USE `rsvp_schema` ;

-- -----------------------------------------------------
-- Table `rsvp_schema`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rsvp_schema`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL DEFAULT NULL,
  `last_name` VARCHAR(255) NULL DEFAULT NULL,
  `email` VARCHAR(255) NULL DEFAULT NULL,
  `password` VARCHAR(255) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `rsvp_schema`.`events`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rsvp_schema`.`events` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL DEFAULT NULL,
  `date` DATE NULL DEFAULT NULL,
  `time_start` TIME NULL DEFAULT NULL,
  `time_end` TIME NULL DEFAULT NULL,
  `address` VARCHAR(255) NULL DEFAULT NULL,
  `details` VARCHAR(500) NULL DEFAULT NULL,
  `options` VARCHAR(255) NULL DEFAULT NULL,
  `guests` VARCHAR(255) NULL DEFAULT NULL,
  `geodata` TEXT NULL,
  `public` TINYINT NULL,
  `user_id` INT NOT NULL,
  `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_events_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_events_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `rsvp_schema`.`users` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `rsvp_schema`.`comments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rsvp_schema`.`comments` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `text` VARCHAR(400) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_id` INT NOT NULL,
  `event_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_comments_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_comments_events1_idx` (`event_id` ASC) VISIBLE,
  CONSTRAINT `fk_comments_events1`
    FOREIGN KEY (`event_id`)
    REFERENCES `rsvp_schema`.`events` (`id`),
  CONSTRAINT `fk_comments_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `rsvp_schema`.`users` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `rsvp_schema`.`non_user_invitees`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rsvp_schema`.`non_user_invitees` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NULL DEFAULT NULL,
  `email` VARCHAR(255) NULL DEFAULT NULL,
  `attending` TINYINT NULL DEFAULT NULL,
  `guest_number` INT NULL,
  `token` VARCHAR(255) NULL,
  `event_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_non_user_invitees_events1_idx` (`event_id` ASC) VISIBLE,
  CONSTRAINT `fk_non_user_invitees_events1`
    FOREIGN KEY (`event_id`)
    REFERENCES `rsvp_schema`.`events` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `rsvp_schema`.`user_invitees`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rsvp_schema`.`user_invitees` (
  `user_id` INT NOT NULL,
  `event_id` INT NOT NULL,
  `attending` TINYINT NULL DEFAULT NULL,
  `guest_number` INT NULL,
  PRIMARY KEY (`user_id`, `event_id`),
  INDEX `fk_users_has_events_events1_idx` (`event_id` ASC) VISIBLE,
  INDEX `fk_users_has_events_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_users_has_events_events1`
    FOREIGN KEY (`event_id`)
    REFERENCES `rsvp_schema`.`events` (`id`),
  CONSTRAINT `fk_users_has_events_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `rsvp_schema`.`users` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;