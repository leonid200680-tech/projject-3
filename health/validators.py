from datetime import date


class ValidationError(Exception):
    pass


def validate_record(r):
    required = ['full_name', 'age', 'gender', 'blood_pressure',
                'heart_rate', 'temperature', 'examination_date']
    for field in required:
        if field not in r:
            raise ValidationError(f'Отсутствует поле "{field}".')

    if r['gender'] not in ('male', 'female'):
        raise ValidationError('gender должен быть male/female.')
    if not (0 < r['age'] < 130):
        raise ValidationError('age вне диапазона.')
    if '/' not in r['blood_pressure']:
        raise ValidationError('blood_pressure формат 120/80.')
    try:
        s, d = map(int, r['blood_pressure'].split('/'))
    except ValueError:
        raise ValidationError('blood_pressure: только числа.')
    if s <= d:
        raise ValidationError('systolic должен быть > diastolic.')
    if not (30 <= r['heart_rate'] <= 220):
        raise ValidationError('heart_rate вне диапазона.')
    if not (30.0 <= float(r['temperature']) <= 45.0):
        raise ValidationError('temperature вне диапазона.')
    try:
        date.fromisoformat(r['examination_date'])
    except (ValueError, TypeError):
        raise ValidationError('examination_date формат YYYY-MM-DD.')


def validate_payload(payload):
    if isinstance(payload, dict):
        records = payload.get('records')
        if records is None:
            raise ValidationError('Нет ключа "records".')
    elif isinstance(payload, list):
        records = payload
    else:
        raise ValidationError('Ожидается объект или массив.')

    if not isinstance(records, list) or not records:
        raise ValidationError('Список записей пуст.')

    for i, rec in enumerate(records, 1):
        if not isinstance(rec, dict):
            raise ValidationError(f'Запись #{i}: не объект.')
        try:
            validate_record(rec)
        except ValidationError as e:
            raise ValidationError(f'Запись #{i}: {e}')

    return records