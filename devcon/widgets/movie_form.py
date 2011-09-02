"""Movie Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea, FileField


class MovieForm(TableForm):

    class fields(WidgetsList):
        title = TextField()
        year = TextField()
        release_date = CalendarDatePicker()
        languageList = [x for x in enumerate((
            'PHP', ''))]
        #language = SingleSelectField(options=languageList)
        language = TextField(disabled="true")
        code = TextArea()
        file = FileField()


create_movie_form = MovieForm("create_movie_form", action='save_movie')
