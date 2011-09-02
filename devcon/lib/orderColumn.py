from tg import expose, flash, require, url, request, redirect, validate, response
from sqlalchemy import asc, desc
from tw.forms.datagrid import Column
import genshi

class SortableColumn(Column):
    def __init__(self, title, name):
        super(SortableColumn, self).__init__(name)
        self._title_ = title

    def set_title(self, title):
        self._title_ = title

    def get_title(self):
        current_ordering = request.GET.get('ordercol')
        if current_ordering and current_ordering[1:] == self.name:
            current_ordering = '-' if current_ordering[0] == '+' else '+'
        else:
            current_ordering = '+'
        current_ordering += self.name

        new_params = dict(request.GET)
        new_params['ordercol'] = current_ordering

        new_url = url(request.path_url, params=new_params)
        return genshi.Markup('<a href="%(page_url)s">%(title)s</a>' % dict(page_url=new_url, title=self._title_))

    title = property(get_title, set_title)
