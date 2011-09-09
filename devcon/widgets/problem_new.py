"""ProblemSubmitForm Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea, FileField, HiddenField

from tw.forms.validators import Int, NotEmpty, DateConverter

class newProblemForm(TableForm):

    class fields(WidgetsList):
        uid = HiddenField()
        code = TextField()
        title = TextField()
        text = TextArea(rows=3)
        input = TextArea(rows=3)
        output = TextArea(rows=3)
        sample_input = TextArea(rows=3)
        sample_output = TextArea(rows=3)
        topic = TextField()
        serie = TextField()
        points = TextField()


create_new_problem = newProblemForm("create_new_problem", action='/problems/createNew')
