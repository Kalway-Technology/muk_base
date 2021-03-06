# -*- coding: utf-8 -*-

###################################################################################
# 
#    MuK Document Management System
#
#    Copyright (C) 2018 MuK IT GmbH
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import os
import json
import base64
import logging
import unittest
import requests

from urllib.parse import urlunparse
from urllib.parse import urlparse
from urllib.parse import parse_qsl
from urllib.parse import urlencode
from contextlib import closing

import odoo
from odoo import _
from odoo.tests import common

_logger = logging.getLogger(__name__)

class AttachmentTestCase(common.HttpCase):
    
    at_install = False
    post_install = True
    
    def setUp(self):
        super(AttachmentTestCase, self).setUp()
        self.attachment = self.env['ir.attachment'].sudo()
        self.param = self.env['ir.config_parameter'].sudo()
        
    def tearDown(self):
        super(AttachmentTestCase, self).tearDown()
    
    def test_attachment(self):
        self.param.set_param('ir_attachment.location', 'lobject')
        attach = self.attachment.create({
            'name': "Test",
            'datas': base64.b64encode(b"\xff data")})
        self.assertTrue(attach.datas)
        self.assertTrue(attach.with_context({'bin_size': True}).datas)
        oid = attach.with_context({'oid': True}).store_lobject
        self.assertTrue(oid)
        attach.write({'datas': base64.b64encode(b"\xff data")})
        self.assertTrue(oid != attach.with_context({'oid': True}).store_lobject)
        self.assertTrue(attach.export_data(['datas']))
        self.assertTrue(attach.export_data(['datas'], raw_data=True))
        attach.unlink()
        
    def test_lobject(self):
        self.param.set_param('ir_attachment.location', 'lobject')
        attach = self.attachment.create({
            'name': "Test",
            'datas': base64.b64encode(b"\xff data")})
        human_size = attach.with_context({'human_size': True}).store_lobject
        self.assertTrue(human_size)
        stream = attach.with_context({'stream': True}).store_lobject
        self.assertTrue(stream.read())
    
    def test_download(self): 
        self.param.set_param('ir_attachment.location', 'lobject')
        attach = self.attachment.create({
            'name': "Test",
            'datas': base64.b64encode(b"\xff data")})
        attach._cr.commit()
        self.authenticate('admin', 'admin')
        url = "/web/lobject/{}/{}/{}".format(
            'ir.attachment',
            attach.id,
            'store_lobject'
        )
        self.assertTrue(self.url_open(url))
        attach.unlink()
        attach._cr.commit()
