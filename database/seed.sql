-- First, clear existing demo data if any (optional)
DELETE FROM products WHERE sku IN ('INDO001', 'KASU001', 'COLA001', 'WATR001', 'DETT001');
DELETE FROM fuel_products WHERE pump_number IN (1, 2);
DELETE FROM branches WHERE id = 'bbbbbbbb-0000-0000-0000-000000000001'::uuid;
DELETE FROM tenants WHERE id = 'aaaaaaaa-0000-0000-0000-000000000001'::uuid;

-- Demo tenant for testing
INSERT INTO tenants (id, name, slug, plan, is_active)
VALUES (
  'aaaaaaaa-0000-0000-0000-000000000001'::uuid,
  'Demo Petrol Station',
  'demo-station',
  'growth',
  true
);

-- Demo branch
INSERT INTO branches (id, tenant_id, name, location, has_fuel_station)
VALUES (
  'bbbbbbbb-0000-0000-0000-000000000001'::uuid,
  'aaaaaaaa-0000-0000-0000-000000000001'::uuid,
  'Main Branch',
  'Thome, Nairobi',
  true
);

-- Demo fuel pumps
INSERT INTO fuel_products (tenant_id, branch_id, fuel_type, pump_number, price_per_litre, tank_capacity_litres, current_stock_litres, reorder_level_litres)
VALUES
  ('aaaaaaaa-0000-0000-0000-000000000001'::uuid, 'bbbbbbbb-0000-0000-0000-000000000001'::uuid, 'Petrol', 1, 208.00, 10000, 4500, 500),
  ('aaaaaaaa-0000-0000-0000-000000000001'::uuid, 'bbbbbbbb-0000-0000-0000-000000000001'::uuid, 'Diesel', 2, 195.00, 12000, 7200, 600);

-- Demo FMCG products
INSERT INTO products (tenant_id, branch_id, name, sku, category, buying_price, selling_price, current_stock, reorder_level)
VALUES
  ('aaaaaaaa-0000-0000-0000-000000000001'::uuid, 'bbbbbbbb-0000-0000-0000-000000000001'::uuid, 'Indomie Noodles', 'INDO001', 'Food', 18, 25, 80, 20),
  ('aaaaaaaa-0000-0000-0000-000000000001'::uuid, 'bbbbbbbb-0000-0000-0000-000000000001'::uuid, 'Kasuku 2kg Cooking Fat', 'KASU001', 'Food', 280, 350, 15, 5),
  ('aaaaaaaa-0000-0000-0000-000000000001'::uuid, 'bbbbbbbb-0000-0000-0000-000000000001'::uuid, 'Coca Cola 500ml', 'COLA001', 'Beverages', 55, 75, 40, 10),
  ('aaaaaaaa-0000-0000-0000-000000000001'::uuid, 'bbbbbbbb-0000-0000-0000-000000000001'::uuid, 'Maisha Magi 1L', 'WATR001', 'Beverages', 30, 45, 60, 15),
  ('aaaaaaaa-0000-0000-0000-000000000001'::uuid, 'bbbbbbbb-0000-0000-0000-000000000001'::uuid, 'Dettol 250ml', 'DETT001', 'Household', 180, 250, 8, 3);

-- Verify data was inserted
SELECT 
  (SELECT COUNT(*) FROM tenants) as tenants_count,
  (SELECT COUNT(*) FROM branches) as branches_count,
  (SELECT COUNT(*) FROM fuel_products) as fuel_count,
  (SELECT COUNT(*) FROM products) as products_count;