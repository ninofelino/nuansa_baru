select replace(article,'''','') as article,(select "DESC" from "SUP" WHERE "CODE"=LEFT("INV"."CODE",3)) as vendor,LEFT("INV"."CODE",3)::int as vendorid,
          (select id from product_category where name="MCLSCODE")::int as mclscode,
          "SELLPRC" as list_price,"COSTPRC" as standard_price,
          cast(min("CODE") as integer) as id,count(*) as jm,json_agg(ukuran order by ukuran) as sizerange,sum("INV"."LQOH") as onhand,min("MCLSCODE") as mclass,
          case when sum("INV"."LQOH")<1 then False else True END AS active,
          case when count(*)>1 then True else False END AS isvariant,
          json_agg(json_build_object('barcode',"CODE",'attribut',ukuran,'desc1',"DESC1",'onhand',"LQOH",'attribute',index)) as product
          from "INV" group by 1,2,3,4,5,6