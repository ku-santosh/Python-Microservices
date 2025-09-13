CREATE SCHEMA IF NOT EXISTS recsui;

CREATE TABLE IF NOT EXISTS recsui.users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(150) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recsui.products (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  price NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS recsui.orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES recsui.users(id),
  product_id INTEGER NOT NULL REFERENCES recsui.products(id),
  quantity INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'created'
);
