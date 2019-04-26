select 'product_product' as name ,count(8),max(create_date) from product_product
union 
select 'product_template' as name ,count(8),max(create_date) from product_template
union
select 'stock_picking' as name ,count(8),max(create_date) from stock_picking
union
select 'stock_move' as name ,count(8),max(create_date) from stock_move