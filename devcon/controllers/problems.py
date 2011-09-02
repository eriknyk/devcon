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

__all__ = ['ProblemsController']

#erik defs
from devcon.controllers.error import ErrorController
from tw.forms import DataGrid
from tw.forms.datagrid import Column
import genshi


problems_grid = DataGrid(fields=[
    ('Problem', 'code'),
    ('Title', 'title'),
    ('Date', 'date'),
    ('Topic', 'topic'),
    ('', lambda obj:genshi.Markup('<a href="%s">view</a>' % url('/problems/view', params=dict(uid=obj.uid))))
])

submits_grid = DataGrid(fields=[
    SortableColumn('User', 'user_name'),
    SortableColumn('Problem', 'problem_title'),
    SortableColumn('Date', 'datetime'),
    SortableColumn('Attempt', 'attempt'),
    SortableColumn('Result', 'result')
])

import datetime
from sqlalchemy import asc, desc
from tg import tmpl_context
from devcon.widgets.movie_form import create_movie_form
from devcon.widgets.problem_submit import create_submit_form


class ProblemsController(BaseController):
    secc = SecureController()

    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    @expose('devcon.templates.index')
    def index(self):
        """Handle the front-page."""
        problem = DBSession.query(Problems).filter_by(uid=uid).one()
        return dict(page='view', problem=problem)
        

    @expose('devcon.templates.problems.list')
    def list(self):
        data = DBSession.query(Problems).order_by(Problems.uid)
        return dict(page='list', grid=problems_grid, data=data, request=request)

        
    @expose('devcon.templates.problems.submits_list')
    @paginate("data", items_per_page=10)
    def submits_list(self, **kw):   
        data = DBSession.query(Submits) #.order_by(desc(Submits.datetime))
        
        ordering = kw.get('ordercol')
        if ordering and ordering[0] == '+':
            data = data.order_by(asc(ordering[1:]))
        elif ordering and ordering[0] == '-':
            data = data.order_by(desc(ordering[1:]))
        else:
            data = data.order_by(desc(Submits.datetime))
        
        return dict(page='submits_list', grid=submits_grid, data=data, request=request)


    @expose('devcon.templates.problems.view')
    def view(self, uid):
        problem = DBSession.query(Problems).filter_by(uid=uid).one()
        return dict(page='view', problem=problem)

        
    @expose('devcon.templates.problems.submit_form')
    def submit(self, **kw):
        tmpl_context.form = create_submit_form
        problem = DBSession.query(Problems).filter_by(uid=kw['uid']).one()
        return dict(problem=problem.title, value=kw)

        
    @expose('devcon.templates.problems.save')
    #@validate(create_submit_form, error_handler=submit)
    def save(self, **kw):
        if kw['file_source'] != '':
            """ saving the file """
            file = request.POST['file_source']
            asset_dirname = os.path.join(os.getcwd(), 'devcon/public/files')
            
            #real path to store the file by user
            path = os.path.join(asset_dirname, request.identity['user'].user_name)
            #is dir??
            if not os.path.isdir(path):
                os.mkdir(path)
            
            filepath = os.path.join(path, file.filename.lstrip(os.sep))
            
            permanent_file = open(filepath, 'w')
            shutil.copyfileobj(file.file, permanent_file)
            
            problem = DBSession.query(Problems).filter_by(uid=kw['uid']).one()
            
            filename = file.filename
            filesize = os.path.getsize(os.path.join(path, file.filename.lstrip(os.sep)))
            filesize = filesize / 1024      
            filesize = "%d Kb" % (filesize, )
            
            file.file.close()
            #this_file = self.request.params["file"].filename 
            permanent_file.close()
            os.chmod(filepath, stat.S_IRWXU)

            """ saving on db """
            
            q =  DBSession.query(Submits).filter(Submits.user_id==request.identity['user'].user_id).order_by(desc(Submits.attempt))
            
            if q.count() > 0:
                attempt_nro = q[0].attempt + 1
            else:
                attempt_nro = 1
            
            
            inputfile_path = os.path.join(os.getcwd(), 'devcon/public/files/inputs', problem.input_filename)
            output_filename = "%s_%d.out" % (problem.code.lower(), problem.serie) 
            gen_output_filename = "%s_%d_%d.out" % (problem.code.lower(), problem.serie, attempt_nro) 
            outputfile_path = os.path.join(os.getcwd(), 'devcon/public/files/outputs', output_filename)
            tmp_filepath = os.path.join(path, gen_output_filename)
            
            cmd = "%s < %s > %s" % (filepath, inputfile_path, tmp_filepath)

            os.system(cmd)
            os.chmod(tmp_filepath, stat.S_IRWXU)
            
            # verify if the file was generated
            if os.path.isfile(tmp_filepath):
                test_lines = open(tmp_filepath).readlines()
                correct_lines = open(outputfile_path).readlines()
                
                ok = 1
                for test, correct in zip(test_lines, correct_lines):
                    if test != correct:
                        result = 'wrong answer'
                        ok = 0
                        break
                    else:
                        len_diff = len(test_lines) - len(correct_lines)
                        if len_diff <> 0:
                            result = 'wrong answer'
                            ok = 0
                            break
            else:
                ok = 0
                result = 'compilation failed'
                
            if ok == 1:
                result = 'accepted'

            
            _submit = Submits()
            _submit.user_id = request.identity['user'].user_id
            _submit.problem_id = problem.uid
            _submit.user_name = request.identity['user'].user_name
            _submit.problem_title = problem.title
            _submit.datetime = datetime.datetime.today().isoformat()
            _submit.filename = filename
            _submit.output_filename = gen_output_filename
            _submit.attempt = attempt_nro
            _submit.result = result
            _submit.accepted = ok
            DBSession.add(_submit)
            
            if ok == 1:
                flash('Congratulations, your solution was accepted')
            else:
                flash('Sorry, your solution was rejected', 'error')
            
            redirect('/problems/submits_list')
            #return dict(filename=filename, filesize=filesize, problem=problem)
        else:
            flash(_('The file is required'), 'warning')
            redirect('/problems/submit?uid=' + kw['uid'])
        

    @expose()
    def getInput(self, uid):
        problem = DBSession.query(Problems).filter_by(uid=uid).one()
        path = os.path.join(os.getcwd(), 'devcon/public/files/inputs')
        file = open(os.path.join(path, problem.input_filename), 'r')
        
        response.headers['Content-Type'] = "text/plain"
        response.headers['Content-Length'] = os.path.getsize(os.path.join(path, problem.input_filename)) # file size in bytes
        response.headers['Content-Disposition'] = 'attachment; filename="'+problem.input_filename+'"'

        data = file.readlines()
        file.close()
        
        return "".join(data[-500:])

        
    @expose('devcon.templates.problems.gs')
    def gStarted(self):
        scode = """#!/usr/bin/env php
<?php
list($a, $b) = explode(' ', trim(fgets(STDIN)));

while($a != 0) {
  echo ($a + $b) . "\\n";
  @list($a, $b) = explode(' ', trim(fgets(STDIN)));
}
"""
        return dict(page='gs', scode=scode)

