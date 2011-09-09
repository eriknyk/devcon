"""ProblemSubmitForm Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, TextField, TextArea, FileField, HiddenField

from tw.forms.validators import Int, NotEmpty, DateConverter

class ProblemUploadIoForm(TableForm):

    class fields(WidgetsList):
        uid = HiddenField()
        in_file = FileField(validator=NotEmpty, required=True)
        out_file = FileField(validator=NotEmpty, required=True)


create_upload_io_form = ProblemUploadIoForm("create_upload_io_form", action='/problems/upload_io_save')
