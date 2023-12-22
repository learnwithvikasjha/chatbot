from django import forms
from django.core.exceptions import ValidationError

class ChatbotForm(forms.Form):
    bot_token = forms.CharField(label='Telegram Bot Token', max_length=100)
    excel_file = forms.FileField(label='Upload Excel File', help_text='Only Excel files allowed')

    def clean_excel_file(self):
        file = self.cleaned_data['excel_file']
        if not file.name.endswith('.xlsx') and not file.name.endswith('.xls'):
            raise ValidationError("Invalid file format. Only Excel files (.xlsx/.xls) are allowed.")
        return file
