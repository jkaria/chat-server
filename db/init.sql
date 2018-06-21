USE chatserver;

CREATE TABLE users(id INT NOT NULL AUTO_INCREMENT, username VARCHAR(50), password VARCHAR(50) NOT NULL, PRIMARY KEY (id), UNIQUE INDEX(username));
INSERT INTO users(username, password) VALUES('user1', 'user1');
INSERT INTO users(username, password) VALUES('user2', 'user2');

CREATE TABLE messages(id INT NOT NULL AUTO_INCREMENT, from_user VARCHAR(50) NOT NULL, to_user VARCHAR(50) NOT NULL, content VARCHAR(256) NOT NULL, dt DATETIME DEFAULT NOW(), PRIMARY KEY (id), INDEX(from_user), INDEX(to_user));
INSERT INTO messages(from_user, to_user, content) VALUES('user1', 'user2', 'message 1');

