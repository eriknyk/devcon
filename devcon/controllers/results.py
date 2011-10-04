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
from devcon.model import DBSession, metadata, Problems, Submits, Series
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

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

class ResultsController(BaseController):
    secc = SecureController()

    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    @expose('devcon.templates.extjs')
    def index(self):
        # getting the current serie of contest
        serie = DBSession.query(Series).filter_by(current=1)
        try:
            serie = serie.one()
            serie_num = serie.uid
            title = serie.title
        except:
            serie_num = 0
            title = 'There is not a active contest'
        
        if serie_num == 0:
            flash(_('There is not a active contest serie'), 'warning')
            jsfilename = ''
        else:
            if serie.status == 'finished':
                jsfilename = 'results.list'
            else:
                flash(_('The content '+title+' is active yet'), 'warning')
                jsfilename = ''
       
        return dict(jsfilename=jsfilename, page='results_list', title=title)


    @expose('json')
    def getList(self, _dc, page, start, limit):
        serie = DBSession.query(Series).filter_by(current=1)
        try:
            serie = serie.one()
            serie_num = serie.uid
            title = serie.title
        except:
            serie_num = 0
            title = 'There is not a active contest'
            
        query = """select submits.*, problems.points as problem_points
from submits 
inner join tg_user on submits.user_id=tg_user.user_id
inner join problems on submits.problem_id=problems.uid
where submits.result='accepted'
and problems.serie=""" + serie_num +  """
order by submits.attempt desc"""

        return str(query);
        rs = DBSession.execute(query)
        rows = rs.fetchall()
        
        
        data = []
        for r in rows:
            data.append({'user_id':r.user_id, 'username':r.user_name, 'problem_id': r.problem_id, 'problem_title': r.problem_title, 'result': r.result, 'datetime': r.datetime, 'attempt': r.attempt})
        
        return dict(rows=data)

    @expose()
    def get_code(self, user_id, problem_id, attempt):
        
        submit = DBSession.query(Submits).filter(Submits.user_id==user_id). \
                 filter(Submits.problem_id==problem_id).filter(Submits.attempt==attempt).one()
        problem = DBSession.query(Problems).filter_by(uid=problem_id).one()

        
        localpath = "devcon/public/files/%s/serie_%d" % (submit.user_name, problem.serie)
        path = os.path.join(os.getcwd(), localpath)

        file = open(os.path.join(path, submit.submit_filename), 'r')
        
        response.headers['Content-Type'] = "text/html"
		
        data = file.readlines()
        data = "".join(data[-500:])
        
        phplexer = get_lexer_by_name("php", stripall=True)
        formatter = HtmlFormatter(linenos=True, cssclass="source")

        data = highlight(data, phplexer, formatter)
        file.close()
        
        data = '<style>'+ HtmlFormatter().get_style_defs('.highlight') +'</style>' + '<div class="highlight">'+data+'</div>'
        return data
      
    @expose('devcon.templates.results.codeview')
    def code(self, user_id, problem_id, attempt):
        return dict(user_id=user_id, problem_id=problem_id, attempt=attempt)
        

