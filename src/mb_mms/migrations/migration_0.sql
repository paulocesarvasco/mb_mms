DROP TABLE IF EXISTS moving_averages;

CREATE TABLE moving_averages (
  id INT NOT NULL AUTO_INCREMENT,
  pair VARCHAR(10) NOT NULL,
  timestamp BIGINT NOT NULL,
  mms_20 FLOAT NULL,
  mms_50 FLOAT NULL,
  mms_200 FLOAT NULL,
  PRIMARY KEY (id),
  INDEX idx_pair_timestamp (pair, timestamp)
);
