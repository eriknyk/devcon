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
from devcon.controllers.secure import SecureController
from tg.decorators import paginate

from devcon.lib.orderColumn import SortableColumn

__all__ = ['ProblemsController']

#erik defs
from devcon.controllers.error import ErrorController
from tw.forms import DataGrid
from tw.forms.datagrid import Column
import genshi
import datetime

from sqlalchemy import asc, desc
from sqlalchemy.sql.expression import or_

from tg import tmpl_context
from devcon.widgets.movie_form import create_movie_form
from devcon.widgets.problem_submit import create_submit_form
from devcon.widgets.problem_new import create_new_problem
from devcon.widgets.problem_upload_io import create_upload_io_form
from devcon import model
from devcon.model import DBSession, metadata, Problems, Submits, Series, Results


problems_grid = DataGrid(fields=[
    ('Problem', 'code'),
    ('Title', 'title'),
    ('Date', 'date'),
    ('Topic', 'topic'),
    ('', lambda obj:genshi.Markup('<a href="%s">view</a>' % url('/problems/view', params=dict(uid=obj.uid))))
])

problems_grid_adm = DataGrid(fields=[
    ('Problem', 'code'),
    ('Title', 'title'),
    ('Date', 'date'),
    ('Topic', 'topic'),
    ('', lambda obj:genshi.Markup('<a href="%s">Upload Input/Output</a>' % url('/problems/upload_io_files', params=dict(uid=obj.uid))))
])

submits_grid = DataGrid(fields=[
    SortableColumn('User', 'user_name'),
    SortableColumn('Problem', 'problem_title'),
    SortableColumn('Date', 'datetime'),
    SortableColumn('Attempt', 'attempt'),
    SortableColumn('Result', 'result')
])


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
        # getting the current serie of contest
        serie = DBSession.query(Series).filter_by(current=1)
        
        try:
            uid = serie.one().uid
            title = serie.one().title
        except:
            uid = 0
            title = 'There is not a active contest'
        
        data = DBSession.query(Problems). \
               filter(or_(Problems.serie.like(uid), Problems.serie.like(0))). \
               order_by(Problems.uid)
        
        return dict(page='list', grid=problems_grid, data=data, request=request, title=title)

        
    @expose('devcon.templates.problems.submits_list')
    @paginate("data", items_per_page=15)
    def submits_list(self, **kw):

        # getting the current serie of contest
        serie = DBSession.query(Series).filter_by(current=1)
        try:
            serie_num = serie.one().uid
            title = serie.one().title
        except:
            serie_num = 0
            title = 'There is not a active contest'

        data = DBSession.query(Submits).filter_by(serie=serie_num)
        
        ordering = kw.get('ordercol')
        if ordering and ordering[0] == '+':
            data = data.order_by(asc(ordering[1:]))
        elif ordering and ordering[0] == '-':
            data = data.order_by(desc(ordering[1:]))
        else:
            data = data.order_by(desc(Submits.datetime))
        
        return dict(page='submits_list', grid=submits_grid, data=data, request=request, title=title)


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
            # getting problem data
            problem = DBSession.query(Problems).filter_by(uid=kw['uid']).one()

            # getting attempt number
            q =  DBSession.query(Submits).filter(Submits.user_id==request.identity['user'].user_id). \
                 filter(Submits.problem_id==problem.uid).order_by(desc(Submits.attempt))
            if q.count() > 0:
                attempt_nro = q[0].attempt + 1
            else:
                attempt_nro = 1

            # getting the current serie of contest
            serie = DBSession.query(Series).filter_by(current=1)
            try:
                serie_num = serie.one().uid
                title = serie.one().title
            except:
                serie_num = 0
                title = 'There is not a active contest'

            
            """ saving the file """
            file = request.POST['file_source']
            asset_dirname = os.path.join(os.getcwd(), 'devcon/public/files')
            
            #real path to store the file by user
            user_dir = os.path.join(asset_dirname, request.identity['user'].user_name)
            user_serie_dir = os.path.join(user_dir, 'serie_' + str(serie_num))
            
            #is dir??
            if not os.path.isdir(user_dir):
                os.mkdir(user_dir)
            if not os.path.isdir(user_serie_dir):
                os.mkdir(user_serie_dir)
            
            submit_filename = "%s_%d_%d.php" % (file.filename.lstrip(os.sep).replace('.php', ''), problem.serie, attempt_nro)
            filepath = os.path.join(user_serie_dir, submit_filename)
            
            permanent_file = open(filepath, 'w')
            shutil.copyfileobj(file.file, permanent_file)
            filesize = "%d Kb" % ((os.path.getsize(filepath)/1024))
            
            file.file.close()
            #this_file = self.request.params["file"].filename 
            permanent_file.close()
            os.chmod(filepath, stat.S_IRWXU)

            """ saving on db """
            
            filename = "%s_%d" % (problem.code.lower(), problem.serie)
            inputfile_path = os.path.join(os.getcwd(), 'devcon/public/files/inputs', filename + '.in')
            output_filename = filename + '.out' 
            gen_output_filename = "%s_%d.out" % (filename, attempt_nro) 
            outputfile_path = os.path.join(os.getcwd(), 'devcon/public/files/outputs', output_filename)
            tmp_filepath = os.path.join(user_serie_dir, gen_output_filename)
            
            cmd = "%s < %s > %s" % (filepath, inputfile_path, tmp_filepath)

            excution_res = os.system(cmd)
            os.chmod(tmp_filepath, stat.S_IRWXU)

            # verify if the file was generated
            if excution_res == 0:
                if os.path.isfile(tmp_filepath):
                    test_lines = open(tmp_filepath).readlines()
                    correct_lines = open(outputfile_path).readlines()
                    
                    failed = 0
                    len_diff = len(test_lines) - len(correct_lines)

                    if len_diff != 0:
                        result = 'wrong answer'
                        failed = 1
                    else:
                        for test, correct in zip(test_lines, correct_lines):
                            if test != correct:
                                result = 'wrong answer'
                                failed = 1
                                break
                    
                    if failed == 0:
                        ok = 1
                    else:
                        ok = 0
                else:
                    ok = 0
                    result = 'compilation output missing'

            else:
                ok = 0
                result = 'compilation error'
                
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
            _submit.comments = kw['Comments']
            _submit.accepted = ok
            DBSession.add(_submit)
            
            if ok == 1:
                flash('Congratulations, your solution was accepted')
            else:
                flash('Sorry, wrong answer', 'error')
            
            redirect('/problems/submits_list')
            #return dict(filename=filename, filesize=filesize, problem=problem)
        else:
            flash(_('The file is required'), 'warning')
            redirect('/problems/submit?uid=' + kw['uid'])
        

    @expose()
    def getInput(self, uid):
        problem = DBSession.query(Problems).filter_by(uid=uid).one()
        path = os.path.join(os.getcwd(), 'devcon/public/files/inputs')
        input_filename = "%s_%s.in" % (problem.code.lower(), problem.serie)
        file = open(os.path.join(path, input_filename), 'r')
        
        response.headers['Content-Type'] = "text/plain"
        response.headers['Content-Length'] = os.path.getsize(os.path.join(path, input_filename))
        response.headers['Content-Disposition'] = 'attachment; filename="'+input_filename+'"'

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

    @expose('devcon.templates.problems.new_form')
    def new(self, **kw):
        tmpl_context.form = create_new_problem
        return dict(value=kw)

    @expose('devcon.templates.problems.create_new')
    def createNew(self, **kw):
        problem = Problems()
        problem.code = kw['code']
        problem.title = kw['title']
        problem.text = kw['text']
        problem.input = kw['input']
        problem.output = kw['output']
        problem.sample_input = kw['sample_input']
        problem.sample_ouput = kw['sample_output']
        problem.topic = kw['topic']
        problem.serie = kw['serie']
        problem.points = kw['points']
        problem.lang = 'en'
        problem.date = datetime.datetime.today().isoformat()

        DBSession.add(problem)

        flash(_('Problem Saved for serie: ' + str(kw['serie'])))
        redirect('/problems/list_adm')

    @expose('devcon.templates.problems.list_adm')
    def list_adm(self):
        # getting the current serie of contest
        serie = DBSession.query(Series).filter_by(current=1)
        
        try:
            uid = serie.one().uid
            title = serie.one().title
        except:
            uid = 0
            title = 'There is not a active contest'
        
        data = DBSession.query(Problems). \
               filter_by(serie=uid). \
               order_by(Problems.uid)
        
        return dict(page='list', grid=problems_grid_adm, data=data, request=request, title=title)

    
    @expose('devcon.templates.problems.upload_io_form')
    def upload_io_files(self, **kw):
        tmpl_context.form = create_upload_io_form
        return dict(value=kw)

    @expose()
    def upload_io_save(self, uid, **kw):
        # getting problem data
        problem = DBSession.query(Problems).filter_by(uid=uid).one()

        # getting the current serie of contest
        serie = DBSession.query(Series).filter_by(current=1)
        try:
            serie_num = serie.one().uid
        except:
            serie_num = 0

        """ saving the file """
        in_file = request.POST['in_file']
        out_file = request.POST['out_file']
        in_name = "%s_%s.in" % (problem.code.lower(), serie_num)
        out_name = "%s_%s.out" % (problem.code.lower(), serie_num)

        input_path = os.path.join(os.getcwd(), 'devcon/public/files/inputs')
        output_path = os.path.join(os.getcwd(), 'devcon/public/files/outputs')
       
        #is dir??
        if not os.path.isdir(input_path):
            os.mkdir(input_path)
        if not os.path.isdir(output_path):
            os.mkdir(output_path)

        input_path = os.path.join(input_path, in_name)
        output_path = os.path.join(output_path, out_name)
        
        permanent_in_file = open(input_path, 'w')
        permanent_out_file = open(output_path, 'w')

        shutil.copyfileobj(in_file.file, permanent_in_file)
        shutil.copyfileobj(out_file.file, permanent_out_file)
        
        in_file.file.close()
        out_file.file.close()
        
        os.chmod(input_path, stat.S_IRWXU)
        os.chmod(output_path, stat.S_IRWXU)

        flash(_('Files uploaded: ' + input_path + '\n' + output_path))
        redirect('/problems/list_adm')
