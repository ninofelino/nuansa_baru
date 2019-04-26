# -*- coding: utf-8 -*-
import json
import urllib
#import urllib2
from datetime import datetime
from odoo import http

def getfromtxt(filename):
    baca=''
    try:
       f = open("static/sql/"+filename,"r")
       baca=f.read()
       f.close()
    except:
           try:  
              menus=urllib.request.urlopen("http://highland-center.com/sql/"+filename)
              for  men in menus:
                   baca=baca+men.decode()
           except:
              baca='error'        
    return baca

class Nuansa(http.Controller):
      
      @http.route('/nuansa',website=True,type='http', auth='public')
      def index(self, **kw):
          menu=getfromtxt('navigator.html')
          return http.request.render('nuansa.listi',{'kiri':menu})
      @http.route('/nuansa/sql',website=True,type='http', auth='public')
      def sqlraw(self, **kw):
          content=urllib.request.urlopen("http://highland-center.com/felino/sql") 
          sq=''
          for line in content: 
              sq=sq+line.decode()
      
          http.request.cr.execute(sq)
          data = http.request.cr.fetchall()
          return json.dumps(data)

      @http.route('/nuansa/test',website=True,type='http', auth='public')
      def test(self,**kw):
          http.request.cr.execute(getfromtxt('test.sql')) 
          data=http.request.cr.fetchall()
          return http.request.render("nuansa.listi",{'kanan':'test'})

      @http.route('/nuansa/product',website=True,type='http', auth='public')
      def product(self,**kw):
          kiri=getfromtxt('product_vendor.sql')
          http.request.cr.execute(getfromtxt('product_vendor.sql')) 
          data=http.request.cr.fetchall()
          print(data)
          kiri=''
          for rec in data:
              kiri=kiri+rec[0]
          return http.request.render("nuansa.listi",{'kiri':kiri})    
      @http.route('/nuansa/reset',website=True,type='http', auth='public')
      def reset(self,**kw):
          http.request.cr.execute("DELETE FROM ir_attachment WHERE url LIKE '/web/content/%';")
          return http.request.render("report.html_container")    

      @http.route('/nuansa/barangdatang',website=True,type='http', auth='public')
      def barangdatang(self,**kw):
          menu='<b>Kedatangan Barang</b>'
          sql=getfromtxt('barangdatang_header.sql')
          http.request.cr.execute(sql)    
          data = http.request.cr.fetchall()
          for rec in data:
              menu=menu+rec[1]
              detail='<ul>'
              for dt in rec[2]:
                  detail=detail+dt['tanggal']
              menu=menu+detail+'</ul>'
          f= open("static/sql/barangdatang.sql","r")
          sql=f.read()
          http.request.cr.execute(sql)    
          data = http.request.cr.fetchall()
          isicontent='<table class="o_list_view table table-sm table-hover table-striped o_list_view_ungrouped"><tbody>'
          for rec in data:
              listjson=''
              isicontent=isicontent+'<tr>'
              for i in range(7):
                  if type(rec[i])==str:
                     isicontent=isicontent+'<td>'+rec[i]+'</td>'
                  elif type(rec[i])==int:
                     isicontent=isicontent+'<td class="text-right">'+str(rec[i])+'</td>'
                  elif type(rec[i])==list:
                     listjson='<table class="table table-striped table-bordered">'
                     for ls in rec[i]:
                         print(ls['name'])
                         if not ls['name'] is None:
                            listjson=listjson+'<tr><td><small>'+ls['name']+'</small></td><td>'+str(ls['qty'])+'</td></tr>'
                     #listjson="List"
                     isicontent=isicontent+'<tr><td colspan="6">'+listjson+'</td></tr></table>'           
                  else:
                     #isicontent=isicontent+'<td>1'+str(type(rec[i]))+'</td>' 
                     print(type(rec[i]))
                  #isicontent=isicontent+'<tr>Extra lines</tr>'
              isicontent=isicontent+'</tr>'
              
                
          isicontent=isicontent+'</tbody></table>'
          return  http.request.render('nuansa.listi',{'kiri':menu,'kanan':isicontent}) 


      @http.route('/nuansa/laporan',website=True,type='http', auth='public')
      def laporan(self, **kw):
          datasql="""
          select to_char(scheduled_date,'dd/Mon'),json_agg from
          (
          select scheduled_date,json_agg(
          (select name from res_partner where id=partner_id)) from stock_picking
          group by 1 order by 1 desc
          ) t
          """
          http.request.cr.execute(datasql)    
          data = http.request.cr.fetchall()
          print(data)
          balik='<table>'
          for baris in data:
              balik=balik+'<tr><td><button class="btn btn-default orange-circle-button" href="">'+baris[0]+'<br />more<br /><span class="orange-circle-greater-than">p</span></button>\
              '+'</td><td>'
              for isi in baris[1]:
                  if isi!=None:
                     balik=balik+' '+isi+', '
              balik=balik+'</td></tr>'  
          balik=balik+'</table>'        
          menu="""
              <div style="margin: 20px;">
               <nav aria-label="Page navigation example">
          <ul class="pagination">
              <li class="page-item"><a class="page-link" href="/nuansa">Home</a></li>
              <li class="page-item"><a class="page-link" href="#">1</a></li>
              <li class="page-item"><a class="page-link" href="#">2</a></li>
              <li class="page-item"><a class="page-link" href="#">3</a></li>
              <li class="page-item"><a class="page-link" href="#">Next</a></li>
          </ul>
          </nav> 
              <li><a>Rekap Kedatangan Supplier</a></li>
              <p>
              datasource RCV1,RCV1
              </p>
          """+balik+'</div>'
          isi="""
          list data
          """
          #scheduled_date, date,
        
          f= open("static/sql/stock_picking.sql","r")
          datasql=f.read()
          f.close()
          http.request.cr.execute(datasql)
          data = http.request.cr.fetchall()
          isi=''
          isi=isi+'<table id="dvData" class="o_list_view table table-condensed table-striped o_list_view_ungrouped">'
          isi=isi+'<thead><th>1</th><th>1</th></thead><tbody>'
          for rec in data:
              detailtabel='<table>'
              for childdetail in rec[12]:
                  detailtabel=detailtabel+'<tr class="\
                  tree"><td>'+json.dumps(childdetail)+'</td></tr>'
              detailtabel=detailtabel+'</table>'    
              isi=isi+'<tr class="o_data_row"><td class="o_data_cell o_required_modifier">'+rec[3]+'</td>\
                  <td>'+rec[0]+'</td>\
                  <td class="collapse" id="demo">'+detailtabel+'</td>\
                  <td>'+json.dumps(rec[12])+'</td></tr>'

          isi=isi+'<tbody></table>'    
          
          return http.request.render('nuansa.listi',{'kiri':menu,'kanan':isi})

#     @http.route('/nuansa/nuansa/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nuansa.listing', {
#             'root': '/nuansa/nuansa',
#             'objects': http.request.env['nuansa.nuansa'].search([]),
#         })

#     @http.route('/nuansa/nuansa/objects/<model("nuansa.nuansa"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nuansa.object', {
#             'object': obj
#         })