import json
import os 
import logging
import re
import dataset
import psycopg2
from psycopg2 import IntegrityError

import time
class Stock:
      info='Stock Module'
     
      def __init__(self):
          self.connection = psycopg2.connect(user="felino",password="felino",host="localhost",port="5432",database="odoo12community")
          self.cursor = self.connection.cursor() 
          self.data = ['postgresql://felino:felino@localhost/nuansabaru12']
          self.db = dataset.connect()
      def inv2odoo(self):
          self.data = []
          product_attribute_value="""
          insert into product_attribute_value(id,name,attribute_id)
          select index as id ,ukuran as name,1 as attribute_id from "INV" 
          where index>0 
          GROUP BY 1,2 ORDER BY 1  
          ON CONFLICT DO NOTHING
          """
          mclass="""
          insert into product_category(id,name)
          select code::float,mclass
          from
          (
          select "MCLSCODE" as mclass,
          replace(replace(replace(replace(replace(replace(replace(replace(replace("MCLSCODE",'A','1'),'B','2'),'C','3'),'D','4'),'E','5'),'F','6'),'G','7'),'H','8'),'M','') as code
          from"INV" 
          WHERE LEFT("MCLSCODE",1)='M' 
          GROUP BY 1,2 ORDER BY 1 
          ) t where code!=''
          ON CONFLICT DO NOTHING
          """
          sql="""
          select replace(article,'''','') as article,(select "DESC" from "SUP" WHERE "CODE"=LEFT("INV"."CODE",3)) as vendor,LEFT("INV"."CODE",3)::int as vendorid,
          (select id from product_category where name="MCLSCODE")::int as mclscode,
          "SELLPRC" as list_price,"COSTPRC" as standard_price,
          cast(min("CODE") as integer) as id,count(*) as jm,json_agg(ukuran order by ukuran) as sizerange,sum("INV"."LQOH") as onhand,min("MCLSCODE") as mclass,
          case when sum("INV"."LQOH")<1 then False else True END AS active,
          case when count(*)>1 then True else False END AS isvariant,
          json_agg(json_build_object('barcode',"CODE",'attribut',ukuran,'desc1',"DESC1",'onhand',"LQOH",'attribute',index)) as product
          from "INV" group by 1,2,3,4,5,6
          """
          sqlinsert="""
          insert into product_template(id,name,list_price,purchase_ok,sale_ok,type,categ_id,uom_id,uom_po_id,responsible_id,tracking,active,description,sale_line_warn,available_in_pos,purchase_line_warn)
          values
          (%s,'%s',%s,True,True,'product',1,1,1,1,'none',%s,'%s','no-message',True,'no-message') 
          ON CONFLICT DO NOTHING
          """
          product_cat="""
          SELECT "MCLSCODE" FROM "INV"GROUP BY 1
          """
          attribut_line="""
          insert into product_template_attribute_line(id,product_tmpl_id,attribute_id) values(\
                  %s,%s,1) ON CONFLICT  DO  NOTHING RETURNING id
          """
          product_insert="""
          insert into product_product(id,product_tmpl_id,default_code,active,create_uid,write_uid)\
            values(%s,%s,'%s',TRUE,1,1) ON CONFLICT ON CONSTRAINT product_product_pkey DO UPDATE SET product_tmpl_id=%s
          """
          product_attribute="""
            insert into product_attribute_value_product_product_rel(attribute_id,product_tmpl_id)\
            values(%s,%s) ON CONFLICT DO NOTHING
            """
          produck_line_attr="""
          INSERT INTO public.product_template_attribute_exclusion
          (product_template_attribute_value_id, product_tmpl_id)
          VALUES (%s,%s)  ON CONFLICT DO NOTHING;
          """ 
          product_attr="""
          INSERT INTO public.product_attribute(
            id, name, sequence, create_variant, create_uid, create_date, 
            write_uid, write_date)
            VALUES (?, ?, ?, ?, ?, ?, 
            ?, ?);
          """
          attribut="""
          INSERT INTO public.product_attribute(
            id, name,create_variant,type) VALUES(1,'SIZE',True,'radio') ON CONFLICT DO NOTHING;
          """
          attribut_line_product_attribute_value="""
          INSERT INTO public.product_attribute_line_product_attribute_value_rel(
            product_attribute_line_id, product_attribute_value_id)
          VALUES (%s, %s) ON CONFLICT DO NOTHING;
          """
          product_attribute_value_product_product_rel="""
          INSERT INTO public.product_template_attribute_value(
          id,product_attribute_value_id,product_tmpl_id
          )
          VALUES (%s,%s,%s) ON CONFLICT DO NOTHING;
          """
          product_attribute_value_product_template_attribute_line_rel="""
          INSERT INTO public.product_attribute_value_product_template_attribute_line_rel(
          product_template_attribute_line_id, product_attribute_value_id)
          VALUES (%s,%s) ON CONFLICT DO NOTHING;
          """
          product_template_attribute_value="""
          INSERT INTO public.product_template_attribute_value(
          id, product_attribute_value_id, product_tmpl_id)
          VALUES (%s,%s,%s) ON CONFLICT DO NOTHING ;
          """
          #table pendukung mclass
          self.cursor.execute(attribut)
          self.cursor.execute(product_attribute_value)
          self.cursor.execute(mclass)
          self.connection.commit()
          print('SLQ->>>',sql,'<------------------------------')  
       
          results = self.db.query(sql)
          keterangan=''
          for rec in results:
              time.sleep( .1 )
              aktive="True"
              if (rec['onhand']<1):
                  aktive="False"
              keterangan=str(rec['mclscode'])    
              #isi product template    
              self.cursor.execute(sqlinsert %(rec['id'],rec['article'],rec['list_price'],aktive,keterangan)) 
              
              self.cursor.execute(attribut_line %(rec['id'],rec['id']))
              print(attribut_line %(rec['id'],rec['id']))
              self.connection.commit()
              #id=http.request.env['product.template'].browse(rec['id'])
             
              #http.request.cr.commit()
              #category=1 
              #vendor=rec['vendorid']
              #if not rec['mclscode'] is None:
              #   category=rec['mclscode']
              #id.write({'name':rec['article'],'active':True,'type':'product','list_price':rec['list_price'],'categ_id':category,'purchase_method':'receive','company_id':1,'purchase_ok':True,'rental':False,'standard_price':rec['standard_price'],'default_code':rec['id'],'vendor':vendor,'available_in_pos':True})
              #print('write--------------------------------------',attribut_line)
              #print(attribut_line %(rec['id'],rec['id']))
              self.cursor.execute(attribut_line %(rec['id'],rec['id']))
              product=rec['product']
              #http.request.cr.commit() 
              attr=''
            
              for pro in product:
                  sq=(product_insert %(pro['barcode'],rec['id'],pro['barcode'],rec['id']))
                  print('---------------------------',pro)
                  
                  self.cursor.execute(sq)
                  self.connection.commit()
                  if pro['attribute'] != None:
                     if pro['attribute'] != 0:
                        print(pro) 
                        attr=(produck_line_attr %(rec['id'],pro['attribute']))
                        print('>>>>>>>>>>>>>>>>>',pro['attribute'])
                        #kurang Attribute line value
                        #self.cursor.execute(product_template_attribute_value %(pro['barcode'],pro['attribute'],rec[id]))
                        #sq=product_template_attribute_value %(pro['barcode'],pro['attribute'],rec[id])
                        print('oooooooooooooooooooooooooooooooooooooooooooooooo')
                        print(product_template_attribute_value %(pro['barcode'],rec['id'],pro['attribute'])) 
                        self.cursor.execute(product_template_attribute_value %(pro['barcode'],pro['attribute'],rec['id']))
                        print('oooooooooooooooooooooooooooooooooooooooooooooooo')
                        self.connection.commit()
                        #rel=product_attribute_value_product_product_rel %(pro['barcode'],pro['attribute'],rec['id'])  
                        rel=product_attribute_value_product_template_attribute_line_rel %(rec['id'],pro['attribute'])
                        product_attribute_value_product_product_rel="""
                        INSERT INTO public.product_attribute_value_product_product_rel(
                        product_product_id, product_attribute_value_id)
                        VALUES (%s,%s) ON CONFLICT DO NOTHING;
                        """
                        self.cursor.execute(product_attribute_value_product_product_rel %(pro['barcode'],pro['attribute']))
                        self.connection.commit()
                        print('++++++++++++++',rel)
                        self.cursor.execute(rel)
                        self.connection.commit()
          return 1

     
st=Stock()
st.db = dataset.connect('postgresql://felino:felino@localhost/odoo12community')
#st.barangdatang()  
st.inv2odoo()        