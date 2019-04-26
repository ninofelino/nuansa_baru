select concat('<li><a href="nuansa/',id,'">',name,'</a><span>',jumlah,'</span></li>')
from
(
select 
left(a.id::char,3) as id,
(select name from res_partner where id=left(a.id::char,3)::int limit 1) as name
,count(*) as jumlah from product_template a 
group by 1,2

) t 