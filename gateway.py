from dbfread import DBF
import sqlite3
from sqlite3 import Error
import dataset
#from odoo import http,exceptions
import json
import os 
import logging
import re
import psycopg2
from psycopg2 import IntegrityError
#import thread6
import urllib
import time

def getfromtxt(filename):
    baca=''
    try:
       f = open("static/sql/gateway/"+filename,"r")
       baca=f.read()
       f.close()
    except:
           try:  
              menus=urllib.request.urlopen("http://highland-center.com/sql/gateway"+filename)
              for  men in menus:
                   baca=baca+men.decode()
           except:
              baca='error'        
    return baca

class Stock:
      info='Stock Module'
     
      def __init__(self):
          self.connection = psycopg2.connect(user="felino",password="felino",host="localhost",port="5432",database="odoo12community")
          self.cursor = self.connection.cursor() 

          
          #self.dbame=
          self.data = ['postgresql://felino:felino@localhost/nuansabaru12']
          self.db = dataset.connect()
          #cr.dbname
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
                        #self.cursor.execute(attr)
                        #http.request.cr.commit()
                        #rel=product_attribute_value_product_product_rel %(pro['barcode'],pro['attribute'],rec['id'])  
                        rel=product_attribute_value_product_template_attribute_line_rel %(rec['id'],pro['attribute'])
                        print('++++++++++++++',rel)
                        self.cursor.execute(rel)
                        self.connection.commit()
          return 1

      def poserver(self):
          server='/mnt/poserver/ics/dat/'
          X=0
          #fileupload=['SUP','RETST1','RETST2','RTSU1','RTSU2','RETSU1','RETSU2','RDIS1','RDIS2','TRANS1','TRANS2','STORE','SUP','RCV1','RCV2','INV','TRANS2S1','TRANS2S2','CUS'] 
          fileupload=['SUP','RETST1','RETST2','RTSU1','RTSU2','RETSU1','RETSU2','RDIS1','RDIS2','TRANS1','TRANS2','SUP','RCV1','RCV2','INV','TRANS2S1','TRANS2S2','CUS'] 
          
          
          for fupload in fileupload:
              uk=['ALL','01','2','3','4','5','O','S','M','L','XL','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','43','44','45']
              namafile=server+fupload+'.DBF'
              if os.path.isfile(namafile):
                 self.db.query('DROP TABLE IF EXISTS '+fupload+';')
                 self.db[fupload].drop()
                 for record in DBF(server+fupload+'.DBF',encoding='iso-8859-1'):
                     print('insert record'+fupload) 
                     X=X+1 
                     time.sleep( .01 )
                     record['nomor']=X
                     if fupload=='INV':
                        ukuran=''   
                        print(X,'--------->>>>>>>>>>>>>>>>',X)
                        rex=r'\s\d{2}$|\s\d{2}\s|\s\D$|\sS$|\sS\s|\sXL$|\sXL\s|\sXXL$|\sXXL\s|\sXXXL$|\sXXXL\s|\sd$'
                        if re.search(rex,record['DESC1']):
                           record['ukuran']=re.search(rex,record['DESC1']).group(0)
                           record['ukuran']=record['ukuran'].strip()
                           record['article']=re.sub(record['ukuran'],'',record['DESC1'])
                        
                           if not record['ukuran'] in uk:
                                record['index']=0
                           else:
                                record['index']=uk.index(record['ukuran'])
                                print(uk.index(record['ukuran']))
                        else:
                           record['ukuran']=''   
                           record['article']=record['DESC1']
                        print("mclass->>>>>>>>>>>>>>>>>>>>>>>>>..") 
                        record['categ_id']=0
                        #record['MCLSCODE'].replace('A','1').replace('B','2').replace('C','3').replace('D','4').replace('E','5'),replace('F','6').replace('G','7').replace('H','8').replace('M','')
                              
                        print(record['article'],'!',record['ukuran'],'!',record['DESC1'])      
                     if fupload=="SUP":
                        #record['BALANCE']=0
                        record['VALDORD']=0 

                     self.db[fupload].insert(record)
              else:
                  print("Not Found")       

          return "posserver"
      def testinv(self):
          db = dataset.connect('sqlite:///poserverdb.db')
          results=db.query('select desc1 from inv limit 100')
          for rec in results:
              print('-------------------------------------')
              
              isi=rec['DESC1']
              if re.search(r'37|38',isi):
                 ukuran=re.search(r'37|38',isi).group(0)
                 article=re.sub(ukuran,'',isi)
              else:
                 ukuran=''   
                 article=isi
              
              print(rec['DESC1'],'!',article,'!',ukuran)  
          return "EEE"  
      def importVendor(self):
          # res_partner_id_seq
          # ALTER SEQUENCE res_partner_id_seq RESTART WITH 22000;
          vendorsql="""
          insert into res_partner(id,name,picking_warn,invoice_warn,purchase_warn,supplier,active,company_id,display_name)
          SELECT "CODE"::INT as id,"DESC" as name,
          'no-message' as picking_warn,
          'no-message' as invoice_warn,
          'no-message' as purchase_warn,
          True as supplier,
          True as active,
          1 as company_id,
          "DESC" as display_name
          FROM "SUP" 
          ON CONFLICT  ON CONSTRAINT res_partner_pkey DO update SET active=true,
          company_id=1,write_uid=1;
          """
          return 'vendor'    
      def importStock(self):
          #delete from stock_picking;
          #delete from stock_move;
          #DELETE FROM stock_move_line
          #DELETE FROM STOCK_QUANT
          vendor="""
          insert into res_partner(
              invoice_warn,invoice_warn_msg, picking_warn, picking_warn_msg, purchase_warn,supplier,active,company_id,id,name)
             
select 
'no-message' as invoice_warn,
'no-message' as invoice_warn_msg,
'no-message' as picking_warn,
'no-message' as picking_warn_msg,
'no-message' as purchase_warn,

true as supplier,
true as active,
1 as company_id,
"CODE"::int as id,"DESC" as name from "SUP"
 ON CONFLICT DO NOTHING;
          """
          sqlsyntax="""
          select a.ID,1 as location_id,11 as location_dest_id,a."SUPLIER"::int as "PARTNER_ID",a."PODATE",'WH/IN/'||a."PONUM" as "PONUM",json_agg(
          json_build_object(
          'name',a."PONUM",   
          'product_id',b."INVCODE",
          'date',a."PODATE",
          'date_expected',a."PODATE",
          'picking_id',1,
          'product_uom',1, 
          'location_id',1,
          'location_dest_id',1, 
          'quantity_done',b."QRCV" 
           
          )) as json
          from "RCV1" a 
          left outer join "RCV2" b on a."PONUM"=b."PONUM"
          group by 1,2,3 order by "PONUM"
          
           
          """
          sqlsales="""
          select * from
          (
           select NORCP as name,CUSCODE as partner_id
           ,DDATE as dateorder
           ,NORCP,FLAG,CODE from sales where FLAG in('PLU','RTN','D%1')
           ) 
          """
          results=self.db.query(sqlsyntax)
          for row in results: 
              bpartner="""
              insert into res_partner(
              invoice_warn,invoice_warn_msg, picking_warn, picking_warn_msg, supplier,active,company_id,id,name)
              values
              ('no-message','no-message','no-message','no-message',TRUE,True,1,%s,'%s')   
                ON CONFLICT ON CONSTRAINT  res_partner_pkey DO UPDATE SET supplier=True,active=true,company_id=1;
              """  %(row['PARTNER_ID'],'nama'+str(row['PARTNER_ID']))
              print(bpartner)
              self.db.query(bpartner)
              self.db.commit()

              #sup=http.request.env['res.partner'].browse(row['PARTNER_ID'])
              #move_lines=[(0,0,{})]
              data={'state':'assigned','name':row['PONUM'],'location_id':1,'location_dest_id':1,'picking_type_id':1,'partner_id':row['PARTNER_ID'],'scheduled_date':str(row['PODATE'])}
              udata={'location_id':1,'location_dest_id':1,'picking_type_id':1,'partner_id':row['PARTNER_ID'],'state':'assigned','scheduled_date':row['PODATE']}
              #cari=http.request.env['stock.picking'].search([('name','=',row['PONUM'])])
              #if not cari.exists():
              #   id=http.request.env['stock.picking'].create(data)
              #cari=http.request.env['stock.picking'].search([('name','=',row['PONUM'])])
              #cari.write({'partner_id':row['PARTNER_ID']})
              #self.db.query('delete from stock_move where picking_id='+str(cari.id))
              #self.db.commit()
              for j in row['json']:
                  pass
                  #print("--------------------->>>",cari.id,j['product_id'],j)
                  #smove={'picking_id':cari.id,
                  #'name':'test','date':row['PODATE'],'date_expected':row['PODATE']
                  #,'product_id':j['product_id'],'location_id':row['location_id'],
                 # 'location_dest_id':row['location_dest_id'],
                 # 'product_uom':1,'quantity_done':j['quantity_done']
                 # }
                  #try: 
                  #    with http.request.env.cr.savepoint():
                  #         http.request.env['stock.move'].create(smove)
                           
                  #except IntegrityError:
                  #       return "error"

                  #http.request.cr.commit()
                  #print("Error",cari.id,j)
                  #,'product_qty':j['quantity_done']
                  #http.request.cr.commit()
                  #http.request.env['stock.quant'].create({'product_id':j['product_id'],'location_id':j['location_id'],'quantity':j['quantity_done'],'reserved_qty':0})
                  #mlines=http.request.env['stock.move'].create(j)
              #cari.state='assigned'
               #stock_quant    
                     
                       
          return "Import Stock"
     # @thread6.threaded()    
      def gateway(self):
          inv2odoo()
          importStock()
          return 1    
      def carigambar(id):
          gb=http.request.env['product.template'].browse(id)
          x=0
          lokasi=glob.glob('/mnt/poserver/images/**/'+str(id)+'.jpg', recursive=True)
          for nfile in lokasi:
              x=x+1
              if x==1: 
                 encoded = base64.b64encode(open(nfile, "rb").read())
                 gb.write({'image':encoded,'image_medium':encoded}) 
          return 1    
      def loadimage(self,id=None, **kw):
          gb=http.request.env['product.template'].sudo().search([('categ_id','=',7103)])
          for g in gb:
              print(g)
              carigambar(g.id)
          return 1
      def stock_inventory_addjusment(self):
          adjustment="""
          select "CODE" as id,"QOH" as qty from "INV" Where "QOH">0
          """
          return 0  
      def gudang(self):
          gd="""
          INSERT INTO public.stock_location(
          id, parent_path, name, complete_name, active,usage)
          VALUES (%s,'%s','%s','%s',True,'internal')
          ON CONFLICT ON CONSTRAINT stock_location_pkey
          DO update set name='%s',complete_name='%s';
          """
          gds=gd %(13,'','HEAD OFFICE','HO','HO','HO')
          gds=gds+gd %(12,'1/11/12/','ABC DEPAN','ABC DEPAN','ABC DEPAN','ABC DEPAN')
          gds=gds+gd %(11,'1/11/13/','ABC BELAKANG','ABC BELAKANG','ABC BELAKANG','ABC BELAKANG')
          gds=gds+gd %(14,'1/11/14/','ABC DRAMAGA','ABC DRAMAGA','ABC DRAMAGA','DRAMAGA')
          
          self.cursor.execute(gds)

          self.connection.commit()
          return 1    
      def supplier(self):
          bpartner="""
          select "CODE"::int as id,replace("DESC",'''','') as name,REPLACE("DESC",'''','') as display_name from "SUP"
          """    
          insertbpartner="""
          INSERT INTO public.res_partner(id, name, company_id, create_date, display_name)
          VALUES (%s,'%s',1,now(),'%s') 
          ON CONFLICT ON CONSTRAINT res_partner_pkey
          DO UPDATE SET name='%s',display_name='%s'
          """
          data=self.db.query(bpartner)
          for rec in data:
              SQL=insertbpartner %(rec['id'],rec['name'],rec['display_name'],rec['display_name'],rec['display_name'])
              self.cursor.execute(SQL)
              self.connection.commit()
          return 0
      def retur(self):
          ganti="""
          insert into stock_picking(company_id,id,name,move_type,picking_type_id,location_id,location_dest_id,scheduled_date) 
          values(1,%s,'%s','direct',5,13,%s,'%s')
          ON CONFLICT ON CONSTRAINT stock_picking_pkey 
          DO NOTHING
          """
          sqlretur="""
          select a."RTNUM"::INT+100000 as id,concat('RET/',a."RTNUM") as name,a."STORE"::int+10 as location_id,a."RTDATE" as date
          ,json_agg(json_build_object('product_id',b."INVCODE",'qty',b."QTY")) as detail
          from "RETST1" a left outer join "RETST2" b on a."RTNUM"=b."RTNUM"
          GROUP BY 1,2,3,4
          """   
          self.cursor.execute("delete from stock_picking where left(name,3)='RET'")
          self.connection.commit()
          data=self.db.query(sqlretur)
          for rec in data:
              id=rec['id']
              sqre=ganti %(rec['id'],'RET/'+str(rec['id']),rec['location_id'],rec['date'])
              #print(sqre)
              if rec['location_id']<15: 
                 self.cursor.execute(sqre)
                 self.connection.commit()
                 for baris in rec['detail']:
                     print(baris)   
                     sqq="insert into stock_move(procure_method,product_uom,company_id,id,name,date,date_expected,product_id,product_uom_qty,location_id,location_dest_id,picking_id) values('make_to_stock',1,1,nextval('stock_move_id_seq'),'%s','%s','%s',%s,%s,8,12,%s)" %(rec['name'],rec['date'],rec['date'],baris['product_id'],baris['qty'],id)
                     print(sqq)
                     self.cursor.execute(sqq)
                     self.connection.commit()
                
                 

          return 0     
      def barangdatang(self):
          stock_picking="""
          select a."PONUM"::int as id,concat('WH/IN/',a."PONUM") as name,"SUPLIER"::int as partner_id,
          'direct' as move_type,'draft' as state,1 as priority,
          a."PODATE" as scheduled_date,a."PODATE" as date,8 as location_id,
          12 as location_dest_id,1 as picking_type_id,
          1 as company_id,json_agg(json_build_object('ponum',b."PONUM",'product_id',b."INVCODE",'id',b.nomor,'qty',b."QTY")) as detail 
          from "RCV1" a left outer join "RCV2" b on a."PONUM"=b."PONUM"
          group by 1,2,3,4,5,6,7,8,9,10,11,12 
          """
          stock_picking_insert="""
          INSERT INTO public.stock_picking(
            id, name, origin, note, backorder_id, move_type, state, group_id, 
            priority, scheduled_date, date, date_done, location_id, location_dest_id, 
            picking_type_id, partner_id, company_id, owner_id, printed, is_locked, 
            immediate_transfer, message_main_attachment_id, create_uid, create_date, 
            write_uid, write_date, sale_id)
            VALUES (%s,'%s', null,null,null,'direct','draft',null, 
            1,'%s',now(),null,8,13, 
            1, %s, 1,null,False,True, 
            False,null,1,now(), 
            1,now(),null) 
            ON CONFLICT ON CONSTRAINT stock_picking_pkey 
            DO NOTHING
            ;

          """ 
          stock_move="""
          INSERT INTO public.stock_move(
            id, name, sequence, priority, create_date, date, company_id, 
            date_expected, product_id, product_qty, product_uom_qty, product_uom, 
            product_packaging, location_id, location_dest_id, partner_id, 
            picking_id, note, state, price_unit, origin, procure_method, 
            scrapped, group_id, rule_id, propagate, picking_type_id, inventory_id, 
            origin_returned_move_id, restrict_partner_id, warehouse_id, additional, 
            reference, package_level_id, create_uid, write_uid, write_date, 
            to_refund, value, remaining_qty, remaining_value, purchase_line_id, 
            created_purchase_line_id, sale_line_id)
            VALUES (%s,'%s',10,null,now(),now(),1, 
            now(),%s,%s,%s,1, 
            null,8,12,null,%s 
            ,null,'draft',0,null,'make to stock', 
            False,null,null,True,1,null, 
            null,null,null,false, 
            'ref',null,1,1,now(), 
            False,null,null,null,null, 
            null,null)
            ON CONFLICT ON CONSTRAINT stock_move_pkey
            DO NOTHING
            ;

          """
          self.cursor.execute('delete from stock_picking')
          self.cursor.execute('delete from stock_move')
          self.connection.commit()
          data=self.db.query(stock_picking)
          for rec in data:
              print('---------------------------------------------------')
              #print(stock_picking_insert %(rec['id'],rec['name']))
              self.cursor.execute(stock_picking_insert %(rec['id'],rec['name'],rec['date'],rec['partner_id']))
              for baris in rec['detail']:
                  print(baris)
                  sqi=stock_move %(baris['id'],rec['name'],baris['product_id'],baris['qty'],2,rec['id'])
                  print(sqi)
                  try: 
                     self.cursor.execute(sqi)
                     self.connection.commit()
                  except:
                      print('error')   
              self.connection.commit()
              #stock_picking_id_seq
          data=self.db.query("select concat('ALTER SEQUENCE stock_picking_id_seq RESTART WITH ',max(id)+10) as syntax  from stock_picking ")
          for baris in data:
              self.cursor.execute(baris['syntax'])
              self.connection.commit()
          return 1 
      def importWh(self):
          namastore="""
          select "CODE"::int+1 as id,"DESC" as name,"NICKNAME" as code from "STORE"
          """
          data=self.db.query(namastore)
          #gudang.write({'name':rec[1],'active':True,'loc_stock_id':rec[0]})
          for rec in data:
              #id=rec[0]
              print(rec)
              self.cursor.execute("insert into stock_warehouse(delivery_steps,reception_steps,lot_stock_id,company_id,view_location_id,id,name,code) values('ship_only','one_step',1,1,11,%s,'%s','%s') ON CONFLICT DO NOTHING" %(rec['id'],rec['name'],rec['code'][1:5]))
              self.connection.commit()
              #print(gudang)
          return 1 
st=Stock()
st.db = dataset.connect('postgresql://felino:felino@localhost/odoo12community')
#st.barangdatang()  
st.inv2odoo()        