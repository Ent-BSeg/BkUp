from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, TimeField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class BackupProjectForm(FlaskForm):
    project_name = StringField('Project Name', validators=[DataRequired(), Length(max=100)],
                             render_kw={"placeholder": "Project Name"})
    folder_name = StringField('Folder Name', validators=[DataRequired(), Length(max=255)],
                            render_kw={"placeholder": "Folder Name"})
    container_names = TextAreaField('Container Names (comma separated)', validators=[DataRequired()],
                                  render_kw={"placeholder": "container1, container2, container3"})
    source_path = StringField('Source Path', validators=[DataRequired(), Length(max=255)],
                            render_kw={"placeholder": "/path/to/source"})
    destination_path = StringField('Destination Path (in Google Drive)', validators=[DataRequired(), Length(max=255)],
                                 render_kw={"placeholder": "backup/path"})
    run_time = StringField('Run Time (HH:MM)', validators=[DataRequired()],
                         render_kw={"placeholder": "23:00"})
    service_enabled = BooleanField('Enable Service')
    submit = SubmitField('Save Project')
