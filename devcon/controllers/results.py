# -*- coding: utf-8 -*

"""
 (c) Erik Amaru Ortiz <aortiz.erik at gmail dot com>
 
 For the full copyright and license information, please view the LICENSE
 file that was distributed with this source code.
"""

import os, sys, stat
import shutil


from tg import expose, flash, require, url, request, redirect, validate, response
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from repoze.what import predicates

from devcon.lib.base import BaseController
from devcon.model import DBSession, metadata, Problems, Submits
from devcon import model
from devcon.controllers.secure import SecureController
from tg.decorators import paginate

from devcon.lib.orderColumn import SortableColumn

__all__ = ['ResultsController']

#erik defs
from devcon.controllers.error import ErrorController
from tw.forms import DataGrid
from tw.forms.datagrid import Column
import genshi
import datetime
from sqlalchemy import asc, desc
from tg import tmpl_context
from devcon.widgets.movie_form import create_movie_form
from devcon.widgets.problem_submit import create_submit_form


class ResultsController(BaseController):
    secc = SecureController()

    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    @expose('devcon.templates.extjs')
    def index(self):
        rs = DBSession.execute("select * from tg_user")
        row = rs.fetchone()
        jsfilename = 'results.list'
        
        return dict(jsfilename=jsfilename, page='results_list')


    @expose('json')
    def getList(self):
        rs = DBSession.execute("select * from tg_user")

        row = rs.fetchall()
        
        return dict(rows=row)



