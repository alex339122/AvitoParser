CREATE TABLE parse (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    title longtext NOT NULL,
    price longtext NOT NULL,
    time longtext NOT NULL,
    place longtext NOT NULL,
    phone longtext NOT NULL,
    url longtext NOT NULL
);

CREATE TABLE `users` (
    `id` INT(11) AUTO_INCREMENT PRIMARY KEY,
    `username` longtext NOT NULL,
    `password` longtext NOT NULL
);
-- drop from parse