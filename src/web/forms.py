from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    SelectField, IntegerField, FileField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange,
    ValidationError
)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        'Repeat Password', 
        validators=[DataRequired(), EqualTo('password')]
    )
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('Register')

class ResumeUploadForm(FlaskForm):
    resume = FileField('Upload Resume (PDF/DOCX)', validators=[DataRequired()])
    submit = SubmitField('Upload')

class JobPreferencesForm(FlaskForm):
    job_role = StringField('Job Role', validators=[DataRequired()])
    experience_level = SelectField(
        'Experience Level',
        choices=[
            ('entry', 'Entry Level'),
            ('mid', 'Mid Level'),
            ('senior', 'Senior'),
            ('lead', 'Lead/Principal')
        ],
        validators=[DataRequired()]
    )
    min_salary = IntegerField(
        'Minimum Salary (LPA)',
        validators=[NumberRange(min=0)]
    )
    max_salary = IntegerField(
        'Maximum Salary (LPA)',
        validators=[NumberRange(min=0)]
    )
    locations = StringField('Preferred Locations (comma-separated)')
    daily_limit = IntegerField(
        'Daily Application Limit',
        validators=[NumberRange(min=1, max=50)],
        default=20
    )
    submit = SubmitField('Save Preferences')

    def validate_max_salary(self, field):
        if field.data < self.min_salary.data:
            raise ValidationError('Maximum salary must be greater than minimum salary')

class BotControlForm(FlaskForm):
    active = BooleanField('Enable Bot')
    submit = SubmitField('Update')
