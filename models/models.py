# -*- coding: utf-8 -*-
from odoo import models, fields, api

class nuansa(models.Model):
      _name = 'nuansa.nuansa'
      name = fields.Char()
      value = fields.Integer()
      description = fields.Text()

   