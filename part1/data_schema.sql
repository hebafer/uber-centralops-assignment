CREATE TABLE `cities` (
  `city_id` INT PRIMARY KEY NOT NULL,
  `city_name` varchar(255),
  `country_id` INT NOT NULL,
  `country_name` varchar(255),
  `distance_unit` varchar(255),
  `lat` float,
  `lng` float,
  `local_currency` varchar(255)
);

CREATE TABLE `vehicles` (
  `vehicle_id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `vehicle_trip_count` int AUTO_INCREMENT,
  `vehicle_type` varchar(255),
  `seat_count` int,
  `vehicle_color` varchar(255)
);

CREATE TABLE `trips` (
  `trip_id` varchar(255) PRIMARY KEY NOT NULL,
  `city_id` int NOT NULL,
  `completed_trip` boolean,
  `distance_to_pickup` int,
  `driver_id` varchar(255),
  `dropoff_geo` varchar(255),
  `dropoff_local_time` timestamp,
  `dropoff_utc_time` timestamp,
  `entered_destination` boolean,
  `esttime_to_pickup` int,
  `pickup_geo` varchar(255),
  `pickup_local_time` timestamp,
  `pickup_utc_time` timestamp,
  `request_geo` varchar(255),
  `request_local_time` timestamp,
  `request_type` varchar(255),
  `request_utc_time` timestamp,
  `rider_id` varchar(255),
  `surged_trip` boolean,
  `time_to_pickup` int,
  `trip_status` varchar(255),
  `vehicle_id` int
);

CREATE TABLE `riders` (
  `rider_id` varchar(255) PRIMARY KEY NOT NULL,
  `active_city_id` int,
  `first_trip_id` varchar(255),
  `preferred_language` varchar(255),
  `rider_app` varchar(255),
  `rider_device` varchar(255),
  `rider_email` varchar(255),
  `rider_trip_count` int,
  `signup_date` timestamp
);

CREATE TABLE `drivers` (
  `driver_id` varchar(255) PRIMARY KEY NOT NULL,
  `active_city_id` int,
  `driver_app` varchar(255),
  `driver_device` varchar(255),
  `driver_email` varchar(255),
  `driver_trip_count` int,
  `first_trip_id` varchar(255),
  `preferred_language` varchar(255),
  `signup_date` timestamp,
  `vehicle_ids` varchar(255)
);

CREATE TABLE `bills` (
  `bill_id` int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `cancel_fee_local` float,
  `cancel_fee_usd` float,
  `completed_trip` boolean,
  `driver_id` varchar(255) NOT NULL,
  `entered_destination` boolean,
  `exchange_rate` float,
  `local_currency` varchar(255),
  `paid_cash` boolean,
  `partner_id` varchar(255) NOT NULL,
  `payment_type` varchar(255),
  `product_category` varchar(255),
  `request_type` varchar(255),
  `rider_id` varchar(255) NOT NULL,
  `surged_trip` boolean,
  `trip_distance_miles` float,
  `trip_duration_seconds` int,
  `trip_fare_local` float,
  `trip_fare_usd` float,
  `trip_id` varchar(255) NOT NULL
);

ALTER TABLE `trips` ADD FOREIGN KEY (`city_id`) REFERENCES `cities` (`city_id`);

ALTER TABLE `trips` ADD FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`);

ALTER TABLE `trips` ADD FOREIGN KEY (`rider_id`) REFERENCES `riders` (`rider_id`);

ALTER TABLE `trips` ADD FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`driver_id`);

ALTER TABLE `riders` ADD FOREIGN KEY (`active_city_id`) REFERENCES `cities` (`city_id`);

ALTER TABLE `riders` ADD FOREIGN KEY (`first_trip_id`) REFERENCES `trips` (`trip_id`);

ALTER TABLE `drivers` ADD FOREIGN KEY (`active_city_id`) REFERENCES `cities` (`city_id`);

ALTER TABLE `drivers` ADD FOREIGN KEY (`first_trip_id`) REFERENCES `trips` (`trip_id`);

ALTER TABLE `bills` ADD FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`driver_id`);

ALTER TABLE `bills` ADD FOREIGN KEY (`rider_id`) REFERENCES `riders` (`rider_id`);

ALTER TABLE `bills` ADD FOREIGN KEY (`trip_id`) REFERENCES `trips` (`trip_id`);

ALTER TABLE `bills` ADD FOREIGN KEY (`partner_id`) REFERENCES `drivers` (`driver_id`);