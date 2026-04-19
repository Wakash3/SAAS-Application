-- Demo tenant for testing
INSERT INTO tenants (id, name, slug, plan, is_active)
VALUES (
  'aaaaaaaa-0000-0000-0000-000000000001',
  'Demo Petrol Station',
  'demo-station',
  'growth',
  true
);

INSERT INTO branches (id, tenant_id, name, location, has_fuel_station)
VALUES (
  'bbbbbbbb-0000-0000-0000-000000000001',
  'aaaaaaaa-0000-0000-0000-000000000001',
  'Main Branch',
  'Thome, Nairobi',
  true
);

-- Demo fuel pumps
INSERT INTO fuel_products (tenant_id, branch_id, fuel_type, pump_number, price_per_litre, tank_capacity_litres, current_stock_litres, reorder_level_litres)
VALUES
  ('aaaaaaaa-0000-0000-0000-000000000001','bbbbbbbb-0000-0000-0000-000000000001','Petrol',1,208.00,10000,4500,500),
  ('aaaaaaaa-0000-0000-0000-000000000001','bbbbbbbb-0000-0000-0000-000000000001','Diesel',2,195.00,12000,7200,600);

-- Demo FMCG products
INSERT INTO products (tenant_id, branch_id, name, sku, category, buying_price, selling_price, current_stock, reorder_level)
VALUES
  ('aaaaaaaa-0000-0000-0000-000000000001','bbbbbbbb-0000-0000-0000-000000000001','Indomie Noodles','INDO001','Food',18,25,80,20),
  ('aaaaaaaa-0000-0000-0000-000000000001','bbbbbbbb-0000-0000-0000-000000000001','Kasuku 2kg Cooking Fat','KASU001','Food',280,350,15,5),
  ('aaaaaaaa-0000-0000-0000-000000000001','bbbbbbbb-0000-0000-0000-000000000001','Coca Cola 500ml','COLA001','Beverages',55,75,40,10),
  ('aaaaaaaa-0000-0000-0000-000000000001','bbbbbbbb-0000-0000-0000-000000000001','Maisha Magi 1L','WATR001','Beverages',30,45,60,15),
  ('aaaaaaaa-0000-0000-0000-000000000001','bbbbbbbb-0000-0000-0000-000000000001','Dettol 250ml','DETT001','Household',180,250,8,3);