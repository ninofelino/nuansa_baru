select concat('
<button icon="fa-print">P</button>
<td><b>',name,'</b></td>')
,tgl,dari,dest,vendor,jml,json_agg
from (
select a.name,to_char(a.scheduled_date,'dd/mm') as tgl
,(select name from stock_location where id=a.location_id) as dari
,(select name from stock_location where id=a.location_dest_id) as dest
,(select name from res_partner where id=a.partner_id) as vendor
,count(*) as jml
,json_agg(json_build_object(
'name',(select name from product_template where id=b.product_id)
,'id',(select id from product_template where id=b.product_id)
,'qty',b.product_qty))
from stock_picking a left outer join stock_move b on a.id=b.picking_id
group by 1,2,3,4,5
) t