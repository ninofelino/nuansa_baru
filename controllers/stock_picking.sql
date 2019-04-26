SELECT  
          to_char(scheduled_date,'dd/mm/yy'),
          (select c.name from res_partner c where id=a.partner_id) as partner,
          (select b.name from stock_location b where b.id=a.location_id) as dari,
          (select b.name from stock_location b where b.id=a.location_dest_id) as           tujuan,
          a.location_id
          ,a.id,a.name, 
          a.picking_type_id,a.partner_id, a.company_id, owner_id, sale_id,
          json_agg(json_build_object('id',b.product_id))
          FROM public.stock_picking a 
          left outer join stock_move b on a.id =b.picking_id
          where a.name like 'RET%'
          group by 1,2,3,4,5,6,7,8,9,10,11