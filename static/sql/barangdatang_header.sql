select to_char(scheduled_date,'yymm'),
concat('<li><a href="nuansa/barangdatang">',to_char(scheduled_date,'Month'),'</a></li>'),json_agg(json_build_object('tanggal',
concat('<li><a href="barangdatang/">',to_char(scheduled_date,'dd-mm')
,'</li></a>'
),'tgl',scheduled_date 
) order by 2) 
from stock_picking
where location_id=8 and location_dest_id=13
/*order by scheduled_date desc*/
group by 1,2 ORDER by 1 DESC