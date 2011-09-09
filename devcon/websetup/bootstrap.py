# -*- coding: utf-8 -*-
"""Setup the devcon application"""

import logging
from tg import config
from devcon import model

import transaction
import datetime


def bootstrap(command, conf, vars):
    """Place any commands to setup devcon here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
        u = model.User()
        u.user_name = u'manager'
        u.display_name = u'Example manager'
        u.email_address = u'manager@somedomain.com'
        u.password = u'sample'
    
        model.DBSession.add(u)
    
        g = model.Group()
        g.group_name = u'managers'
        g.display_name = u'Managers Group'
    
        g.users.append(u)
    
        model.DBSession.add(g)
    
        p = model.Permission()
        p.permission_name = u'manage'
        p.description = u'This permission give an administrative right to the bearer'
        p.groups.append(g)
    
        model.DBSession.add(p)
    
        u1 = model.User()
        u1.user_name = u'editor'
        u1.display_name = u'Example editor'
        u1.email_address = u'editor@somedomain.com'
        u1.password = u'editpass'
    
        model.DBSession.add(u1)                    
    
        pr1 = model.Problems()
        pr1.code = 'X'
        pr1.title = 'A + B Problem'
        pr1.text = 'Calculate a+b'
        pr1.input = """The input will consist of a set of pairs of values for a and b. (Two integer a,b (0<=a,b<=10))
Input is terminated with a case where a = 0. This case should not be processed."""
        pr1.sample_input = """1 2
5 20
21 10
0"""
        pr1.output = 'Output a+b '
        pr1.sample_output = """3
25
31"""
        pr1.topic = 'testing'
        pr1.serie = 0
        pr1.points = 0
        pr1.lang = 'en'
        pr1.date = datetime.datetime.today().isoformat()
        
        model.DBSession.add(pr1)                    
        
        
        model.DBSession.flush()
        transaction.commit()
    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        import traceback
        print traceback.format_exc()
        transaction.abort()
        print 'Continuing with bootstrapping...'
        

    # <websetup.bootstrap.after.auth>
