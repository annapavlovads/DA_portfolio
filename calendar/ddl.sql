CREATE TABLE public.holidays (
id SERIAL PRIMARY KEY, -
name VARCHAR(128), 
dt TIMESTAMP 
);

CREATE TABLE events (
id SERIAL PRIMARY KEY,
name VARCHAR(64) NOT NULL,
importance VARCHAR(32) NOT NULL,
begin_date TIMESTAMP WITH TIME ZONE,
end_date TIMESTAMP WITH TIME ZONE,
owner VARCHAR(64) NOT NULL,
restaurant TEXT[], 
tag TEXT[], 
promotion_type TEXT[], 
brief VARCHAR(256),
picture VARCHAR(256),
instruction TEXT,
comment TEXT,
is_completed INTEGER,
summary TEXT
);

CREATE TABLE log (
id SERIAL PRIMARY KEY,
status VARCHAR(32),
dt TIMESTAMP WITH TIME ZONE,
user_name VARCHAR(64),
event_id INTEGER REFERENCES events(id)
);

CREATE TABLE users (
id SERIAL PRIMARY KEY,
user_name VARCHAR(32) UNIQUE NOT NULL,
user_password VARCHAR(64) NOT NULL,
rights SMALLINT,
user_department VARCHAR(64),
user_description VARCHAR(128)
);

CREATE INDEX idx_restaurant ON events USING GIN (restaurant);
CREATE INDEX idx_name ON events (name);
CREATE INDEX idx_begin_date ON events (begin_date);
CREATE INDEX idx_end_date ON events (end_date);