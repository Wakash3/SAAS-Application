-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- TENANTS
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  plan VARCHAR(50) DEFAULT 'starter',
  stripe_customer_id VARCHAR(255),
  mpesa_shortcode VARCHAR(20),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- BRANCHES
CREATE TABLE branches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  location TEXT,
  has_fuel_station BOOLEAN DEFAULT false,
  mpesa_till VARCHAR(20),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- FMCG PRODUCTS
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL,
  branch_id UUID REFERENCES branches(id),
  name VARCHAR(255) NOT NULL,
  sku VARCHAR(100),
  barcode VARCHAR(100),
  category VARCHAR(100),
  buying_price DECIMAL(10,2),
  selling_price DECIMAL(10,2) NOT NULL,
  current_stock INT DEFAULT 0,
  reorder_level INT DEFAULT 10,
  unit VARCHAR(50) DEFAULT 'piece',
  is_active BOOLEAN DEFAULT true,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- FUEL PRODUCTS (metered inventory)
CREATE TABLE fuel_products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL,
  branch_id UUID REFERENCES branches(id),
  fuel_type VARCHAR(50) NOT NULL,
  pump_number INT,
  nozzle_number INT,
  price_per_litre DECIMAL(10,2) NOT NULL,
  current_meter DECIMAL(12,4) DEFAULT 0,
  tank_capacity_litres DECIMAL(10,2),
  current_stock_litres DECIMAL(10,2) DEFAULT 0,
  reorder_level_litres DECIMAL(10,2) DEFAULT 200,
  is_active BOOLEAN DEFAULT true,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SALES
CREATE TABLE sales (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL,
  branch_id UUID NOT NULL,
  sale_number VARCHAR(50) UNIQUE NOT NULL,
  cashier_id VARCHAR(255) NOT NULL,
  sale_type VARCHAR(20) DEFAULT 'mixed',
  subtotal DECIMAL(10,2),
  total_amount DECIMAL(10,2) NOT NULL,
  payment_method VARCHAR(50),
  payment_status VARCHAR(50) DEFAULT 'pending',
  mpesa_receipt VARCHAR(100),
  mpesa_phone VARCHAR(20),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SALE ITEMS
CREATE TABLE sale_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL,
  item_type VARCHAR(20) NOT NULL,
  product_id UUID,
  fuel_product_id UUID,
  description VARCHAR(255),
  quantity DECIMAL(10,4) NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  total_price DECIMAL(10,2) NOT NULL,
  meter_start DECIMAL(12,4),
  meter_end DECIMAL(12,4)
);

-- STOCK DELIVERIES
CREATE TABLE stock_deliveries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL,
  branch_id UUID NOT NULL,
  supplier_id UUID,
  delivery_type VARCHAR(20),
  invoice_number VARCHAR(100),
  total_cost DECIMAL(12,2),
  delivery_date DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AUTOMATED STOCKTAKE SNAPSHOTS
CREATE TABLE stocktake_snapshots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL,
  branch_id UUID NOT NULL,
  snapshot_date DATE NOT NULL,
  snapshot_type VARCHAR(20) DEFAULT 'auto',
  generated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE stocktake_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  snapshot_id UUID REFERENCES stocktake_snapshots(id),
  tenant_id UUID NOT NULL,
  item_type VARCHAR(20),
  product_id UUID,
  fuel_product_id UUID,
  product_name VARCHAR(255),
  system_qty DECIMAL(10,4),
  physical_qty DECIMAL(10,4),
  variance DECIMAL(10,4),
  variance_value_kes DECIMAL(10,2),
  status VARCHAR(20) DEFAULT 'ok'
);

-- M-PESA TRANSACTIONS
CREATE TABLE mpesa_transactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL,
  sale_id UUID REFERENCES sales(id),
  checkout_request_id VARCHAR(255) UNIQUE,
  mpesa_receipt_number VARCHAR(100),
  phone_number VARCHAR(20),
  amount DECIMAL(10,2),
  status VARCHAR(50) DEFAULT 'pending',
  raw_callback JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SUPPLIERS
CREATE TABLE suppliers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL,
  name VARCHAR(255) NOT NULL,
  contact_phone VARCHAR(20),
  contact_email VARCHAR(255),
  credit_limit DECIMAL(12,2) DEFAULT 0,
  outstanding_balance DECIMAL(12,2) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ENABLE ROW LEVEL SECURITY
-- NOTE: With Neon + SQLAlchemy we enforce tenant isolation at app level
-- and also at DB level via RLS for extra safety.
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE fuel_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE sale_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE stocktake_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE stocktake_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE mpesa_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;

-- RLS POLICIES (tenant isolation via session variable)
CREATE POLICY tenant_iso ON products
  USING (tenant_id::text = current_setting('app.current_tenant', true));
CREATE POLICY tenant_iso ON fuel_products
  USING (tenant_id::text = current_setting('app.current_tenant', true));
CREATE POLICY tenant_iso ON sales
  USING (tenant_id::text = current_setting('app.current_tenant', true));
CREATE POLICY tenant_iso ON sale_items
  USING (tenant_id::text = current_setting('app.current_tenant', true));
CREATE POLICY tenant_iso ON stocktake_snapshots
  USING (tenant_id::text = current_setting('app.current_tenant', true));
CREATE POLICY tenant_iso ON stocktake_items
  USING (tenant_id::text = current_setting('app.current_tenant', true));
CREATE POLICY tenant_iso ON mpesa_transactions
  USING (tenant_id::text = current_setting('app.current_tenant', true));
CREATE POLICY tenant_iso ON suppliers
  USING (tenant_id::text = current_setting('app.current_tenant', true));

-- INDEXES (critical for performance)
CREATE INDEX idx_sales_tenant_date ON sales(tenant_id, created_at DESC);
CREATE INDEX idx_products_tenant ON products(tenant_id, is_active);
CREATE INDEX idx_fuel_tenant ON fuel_products(tenant_id, branch_id);
CREATE INDEX idx_mpesa_checkout ON mpesa_transactions(checkout_request_id);
CREATE INDEX idx_stocktake_date ON stocktake_snapshots(tenant_id, snapshot_date);
CREATE INDEX idx_branches_tenant ON branches(tenant_id);
CREATE INDEX idx_suppliers_tenant ON suppliers(tenant_id);