select to_char(scheduled_date,'dd/Mon'),json_agg from
          (
          select scheduled_date,json_agg(
          (select name from res_partner where id=partner_id)) from stock_picking
          group by 1 order by 1 desc
          ) t