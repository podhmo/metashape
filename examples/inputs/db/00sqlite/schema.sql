CREATE TABLE IF NOT EXISTS "Category" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "name" TEXT UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS "Customer" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "email" TEXT UNIQUE NOT NULL,
  "password" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "country" TEXT NOT NULL,
  "address" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "Order" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "state" TEXT NOT NULL,
  "date_created" DATETIME NOT NULL,
  "date_shipped" DATETIME,
  "date_delivered" DATETIME,
  "total_price" DECIMAL(12, 2) NOT NULL,
  "customer_id" INTEGER NOT NULL REFERENCES "Customer" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "Product" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "name" TEXT NOT NULL,
  "description" TEXT NOT NULL,
  "picture" BLOB,
  "price" DECIMAL(12, 2) NOT NULL,
  "quantity" INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS "CartItem" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "quantity" INTEGER NOT NULL,
  "customer_id" INTEGER NOT NULL REFERENCES "Customer" ("id") ON DELETE CASCADE,
  "product_id" INTEGER NOT NULL REFERENCES "Product" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "Category_Product" (
  "category_id" INTEGER NOT NULL REFERENCES "Category" ("id") ON DELETE CASCADE,
  "product_id" INTEGER NOT NULL REFERENCES "Product" ("id") ON DELETE CASCADE,
  PRIMARY KEY ("category_id", "product_id")
);
CREATE TABLE IF NOT EXISTS "OrderItem" (
  "quantity" INTEGER NOT NULL,
  "price" DECIMAL(12, 2) NOT NULL,
  "order_id" INTEGER NOT NULL REFERENCES "Order" ("id") ON DELETE CASCADE,
  "product_id" INTEGER NOT NULL REFERENCES "Product" ("id") ON DELETE CASCADE,
  PRIMARY KEY ("order_id", "product_id")
);
CREATE INDEX "idx_order__customer" ON "Order" ("customer_id");
CREATE INDEX "idx_cartitem__customer" ON "CartItem" ("customer_id");
CREATE INDEX "idx_cartitem__product" ON "CartItem" ("product_id");
CREATE INDEX "idx_category_product" ON "Category_Product" ("product_id");
CREATE INDEX "idx_orderitem__product" ON "OrderItem" ("product_id");
