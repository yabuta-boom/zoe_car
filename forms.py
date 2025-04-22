from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Optional

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    message = TextAreaField('Message', validators=[DataRequired()])
    interest = SelectField('Interest', choices=[
        ('general', 'General Inquiry'),
        ('test_drive', 'Test Drive'),
        ('financing', 'Financing'),
        ('trade_in', 'Trade-In'),
        ('service', 'Service')
    ])
