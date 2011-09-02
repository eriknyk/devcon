"""ProblemSubmitForm Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea, FileField, HiddenField

from tw.forms.validators import Int, NotEmpty, DateConverter

class ProblemSubmitForm(TableForm):

    class fields(WidgetsList):
        uid = HiddenField()
        Comment = TextField()
        file_source = FileField(validator=NotEmpty, required=True)


create_submit_form = ProblemSubmitForm("create_submit_form", action='/problems/save')
