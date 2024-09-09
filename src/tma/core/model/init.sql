CREATE TABLE users
(
  user_id    SERIAL,
  session_id VARCHAR(255) NOT NULL,
  CONSTRAINT pk_users PRIMARY KEY (user_id),
  CONSTRAINT unique_session_id UNIQUE (session_id)
);

CREATE INDEX session_index ON users USING HASH (session_id);

CREATE TABLE samples
(
  sample_id           SERIAL,
  user_id             INTEGER      NOT NULL,
  x_column            varchar(255) NOT NULL DEFAULT 0,
  y_column            varchar(255) NOT NULL DEFAULT 0,
  selected_file_index int          NOT NULL DEFAULT 0,
  name                VARCHAR(255)          DEFAULT '',
  CONSTRAINT pk_samples PRIMARY KEY (sample_id)
);

CREATE INDEX user_index ON samples USING HASH (user_id);

CREATE TABLE specimenItems
(
  specimen_item_id SERIAL,
  sample_id        INTEGER NOT NULL,
  filename         VARCHAR(255),
  uploaded         BOOLEAN DEFAULT TRUE,
  file_extension   VARCHAR(255),
  is_empty_source  BOOLEAN DEFAULT FALSE,
  CONSTRAINT pk_specimenItems PRIMARY KEY (specimen_item_id),
  CONSTRAINT unique_sample_id_filename UNIQUE (sample_id, filename)
);

CREATE INDEX sample_index ON specimenItems USING HASH (sample_id);

CREATE TABLE measurements
(
  measurement_id   SERIAL,
  specimen_item_id INTEGER      NOT NULL,
  measurement_type VARCHAR(255) NOT NULL,
  columns          JSONB,
  CONSTRAINT pk_measurements PRIMARY KEY (measurement_id)
);

CREATE INDEX specimen_item_index ON measurements USING HASH (specimen_item_id);

CREATE TABLE measured_data
(
  measurement_data_id SERIAL,
  measurement_id      INTEGER      NOT NULL,
  specimen_item_id    INTEGER      NOT NULL,
  column_name         VARCHAR(255) NOT NULL,
  data                JSONB,
  CONSTRAINT pk_measured_data PRIMARY KEY (measurement_data_id),
  CONSTRAINT unique_measurement_id_column_name UNIQUE (measurement_id, column_name)
);

CREATE INDEX measurement_index ON measured_data USING HASH (measurement_id);
CREATE INDEX specimen_item_id_index ON measured_data USING HASH (specimen_item_id);


CREATE TABLE curie_points
(
  curie_point_id      SERIAL,
  specimen_item_id    INTEGER      NOT NULL,
  column_name         VARCHAR(255) NOT NULL,
  id_plot_selected    INTEGER      NOT NULL DEFAULT 0,
  temperature_value   FLOAT        NOT NULL DEFAULT 0.0,
  magnetization_value FLOAT        NOT NULL DEFAULT 0.0,
  CONSTRAINT pk_curie_point PRIMARY KEY (curie_point_id)
);
CREATE INDEX specimen_item_id_index ON curie_points USING HASH (specimen_item_id);
