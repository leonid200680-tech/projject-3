from django import forms


class HealthRecordForm(forms.Form):
    full_name = forms.CharField(label='ФИО', max_length=200)
    age = forms.IntegerField(label='Возраст', min_value=1, max_value=129)
    gender = forms.ChoiceField(
        label='Пол',
        choices=[('male', 'Мужской'), ('female', 'Женский')],
    )
    blood_pressure = forms.CharField(label='Давление (120/80)', max_length=20)
    heart_rate = forms.IntegerField(label='Пульс', min_value=30, max_value=220)
    temperature = forms.FloatField(label='Температура', min_value=30.0, max_value=45.0)
    diagnosis = forms.CharField(label='Диагноз', max_length=300, required=False)
    examination_date = forms.DateField(
        label='Дата',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def clean_full_name(self):
        name = self.cleaned_data['full_name'].strip()
        if len(name.split()) < 2:
            raise forms.ValidationError('Укажите имя и фамилию.')
        return name

    def clean_blood_pressure(self):
        bp = self.cleaned_data['blood_pressure'].strip()
        if '/' not in bp:
            raise forms.ValidationError('Формат: 120/80')
        try:
            s, d = map(int, bp.split('/'))
        except ValueError:
            raise forms.ValidationError('Только числа.')
        if not (60 <= s <= 260) or not (30 <= d <= 160) or s <= d:
            raise forms.ValidationError('Некорректные значения давления.')
        return bp


class UploadFileForm(forms.Form):
    file = forms.FileField(label='JSON-файл')

    def clean_file(self):
        f = self.cleaned_data['file']
        if not f.name.lower().endswith('.json'):
            raise forms.ValidationError('Только .json')
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Максимум 5 МБ.')
        return f