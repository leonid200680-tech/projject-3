import json

from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import HealthRecordForm, UploadFileForm
from .utils import DATA_DIR, list_files, save_records, safe_name
from .validators import ValidationError, validate_payload


def index(request):
    files = list_files()
    files_data = []
    for path in files:
        try:
            with path.open('r', encoding='utf-8') as f:
                content = json.load(f)
        except (json.JSONDecodeError, OSError):
            content = {'error': 'Не удалось прочитать файл.'}
        files_data.append({'name': path.name, 'content': content})
    return render(request, 'health/index.html', {'files': files_data})


def add_record(request):
    if request.method == 'POST':
        form = HealthRecordForm(request.POST)
        if form.is_valid():
            data = dict(form.cleaned_data)
            data['examination_date'] = data['examination_date'].isoformat()
            try:
                validate_payload({'records': [data]})
            except ValidationError as e:
                messages.error(request, f'Ошибка валидации: {e}')
                return render(request, 'health/add.html', {'form': form})

            save_records([data])
            messages.success(request, 'Запись сохранена в JSON-файл.')
            return redirect('index')
    else:
        form = HealthRecordForm()
    return render(request, 'health/add.html', {'form': form})


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data['file']
            target = DATA_DIR / safe_name(uploaded.name)

            if not str(target.resolve()).startswith(str(DATA_DIR.resolve())):
                messages.error(request, 'Недопустимое имя файла.')
                return render(request, 'health/upload.html', {'form': form})

            with target.open('wb+') as dest:
                for chunk in uploaded.chunks():
                    dest.write(chunk)

            try:
                with target.open('r', encoding='utf-8') as f:
                    payload = json.load(f)
                validate_payload(payload)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                target.unlink(missing_ok=True)
                messages.error(request, f'Некорректный JSON: {e}. Файл удалён.')
                return render(request, 'health/upload.html', {'form': form})
            except ValidationError as e:
                target.unlink(missing_ok=True)
                messages.error(request, f'Ошибка валидации: {e}. Файл удалён.')
                return render(request, 'health/upload.html', {'form': form})

            messages.success(request, f'Файл "{target.name}" загружен.')
            return redirect('index')
    else:
        form = UploadFileForm()
    return render(request, 'health/upload.html', {'form': form})