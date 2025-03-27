from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import re


app = Flask(__name__)
app.config['SECRET_KEY'] = '1C0EF437811F8CCA2C532E7B'

class PhoneForm(FlaskForm):
    phone = StringField('Номер телефона', validators=[DataRequired()])
    submit = SubmitField('Проверить')

def validate_phone(phone):
    # Проверка на недопустимые символы
    if not all(c.isdigit() or c in ' ()-.+' for c in phone):
        return False, "Недопустимый ввод. В номере телефона встречаются недопустимые символы.", None
    
    # Удаляем все допустимые нецифровые символы
    digits_only = re.sub(r'[\s()\-\.+]', '', phone)
    
    # Определяем ожидаемую длину в зависимости от первых символов
    starts_with_plus7 = phone.startswith('+7')
    starts_with_8 = phone.startswith('8')
    
    if starts_with_plus7 or starts_with_8:
        expected_length = 11
        # Проверяем, что у номера с +7 первая цифра после + действительно 7
        if starts_with_plus7 and (len(digits_only) < 1 or digits_only[0] != '7'):
            return False, "Недопустимый ввод. Неверное количество цифр.", None
    else:
        expected_length = 10
    
    # Проверка количества цифр
    if len(digits_only) != expected_length:
        return False, "Недопустимый ввод. Неверное количество цифр.", None
    
    # Подготавливаем номер для форматирования
    if starts_with_plus7:
        formatted_digits = '8' + digits_only[1:]  # Заменяем 7 на 8
    elif starts_with_8:
        formatted_digits = digits_only  # Оставляем как есть
    else:
        formatted_digits = '8' + digits_only  # Добавляем 8 в начало
    
    # Форматирование номера в формате 8-***-***-**-**
    formatted = f"{formatted_digits[0]}-{formatted_digits[1:4]}-{formatted_digits[4:7]}-{formatted_digits[7:9]}-{formatted_digits[9:11]}"
    
    return True, None, formatted

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/request-info')
def request_info():
    url_params = dict(request.args)
    headers = dict(request.headers)
    cookies = dict(request.cookies)
    return render_template('request_info.html', url_params=url_params, headers=headers, cookies=cookies)

@app.route('/form-data', methods=['GET', 'POST'])
def form_data():
    if request.method == 'POST':
        form_params = dict(request.form)
        return render_template('form_data.html', form_params=form_params)
    return render_template('form_data.html', form_params={})

@app.route('/phone-validator', methods=['GET', 'POST'])
def phone_validator():
    form = PhoneForm()
    errors = {}
    formatted_phone = None
    
    if form.validate_on_submit():
        phone = form.phone.data
        valid, error_message, formatted = validate_phone(phone)
        
        if not valid:
            errors['phone'] = error_message
        else:
            formatted_phone = formatted
            
    return render_template('phone_validator.html', form=form, errors=errors, formatted_phone=formatted_phone)

if __name__ == '__main__':
    app.run(debug=True)
