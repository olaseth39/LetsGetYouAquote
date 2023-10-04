from wtforms import Form, FileField, StringField, SubmitField, validators, IntegerField, ValidationError, form, EmailField, SelectField, PasswordField, TextAreaField
# import wtforms
from flask import session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize, FileStorage
from flask_uploads import UploadSet, IMAGES, configure_uploads

# photos = UploadSet('photos', IMAGES)


class DetailsForm(Form):
    name = StringField('Name', validators=[validators.input_required(), validators.length(max=100)],
                       render_kw={"placeholder": "Enter the name you want on the quotation "})
    email = EmailField('Email', validators=[validators.input_required()],
                       render_kw={"placeholder": "Enter the email you want on the quotation "})
    volume = IntegerField('Volume', validators=[validators.input_required()],
                          render_kw={"placeholder": "Enter the volume in liters "})
    type_of_tank = SelectField('Click to select type of tank', choices=['Steel', 'GRP'],
                               validators=[validators.input_required()])

    def validate_volume(form, field):
        if field.data < 4:
            raise ValidationError("We are sorry, volume can't be less than 4")


class SignUpForm(Form):
    # def __init__(self, photo, *args, **kwargs):
    #     self.photos = photo
    #     # got the correction from the link below
    #     # https://stackoverflow.com/questions/61953652/modifying-flaskforms-class-object-has-no-attribute-fields
    #     super(SignUpForm, self).__init__(*args, **kwargs)

    name = StringField('Name', validators=[validators.input_required(), validators.length(min=1, max=100)],
                       render_kw={"placeholder": "Enter the name you want on the quotation "})
    email = EmailField('Email', validators=[validators.input_required()],
                       render_kw={"placeholder": "Enter the email you want on the quotation "})
    country = StringField('Country', validators=[validators.input_required()],
                          render_kw={"placeholder": "Enter your country where the quotation is to be used "})
    telephone = StringField('Telephone', validators=[validators.input_required()],
                        render_kw={"placeholder": "Enter your telephone number with your country code"})
    company = StringField('Your Company',
                            render_kw={"placeholder": "Enter the name of your company"})
    company_address = StringField('Company Address',
                            render_kw={"placeholder": "Enter the address of your company"})
    logo = FileField('Logo', render_kw={"placeholder": "Upload your logo"})
    password = PasswordField('Password', validators=[validators.input_required()],
                            render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign up')


# This is for editing prices by admins
class SelectFieldToEditForm(Form):
    field_to_edit = SelectField('Click to select what you want to edit', choices=['GRP prices', 'Steel prices', 'Vat'],
                                validators=[validators.input_required()])


# This is for admin_quotation
class AdminQuotationForm(Form):
    name = StringField('Name', validators=[validators.input_required(), validators.length(max=100)],
                       render_kw={"placeholder": "Enter the name you want on the quotation "})
    company = StringField('Company', validators=[validators.input_required(), validators.length(max=100)],
                       render_kw={"placeholder":"Enter the company you want on the quotation.Type residential for noncompany"})
    address = StringField('Address', validators=[validators.input_required(), validators.length(max=100)],
                       render_kw={"placeholder": "Enter the address you want on the quotation "})
    mobile = StringField('Mobile', validators=[validators.input_required(), validators.length(max=100)],
                       render_kw={"placeholder": "Enter the telephone number of your client"})
    email = EmailField('Email', validators=[validators.input_required()],
                       render_kw={"placeholder": "Enter the email you want on the quotation "})
    volume = IntegerField('Volume', validators=[validators.input_required()],
                          render_kw={"placeholder": "Enter the volume in liters "})
    type_of_tank = SelectField('Click to select type of tank', choices=['Steel', 'GRP'],
                               validators=[validators.input_required()])
    transport = IntegerField('Transport Fees', render_kw={"placeholder": "Enter the transport fee, if none put 0"})


class ResetRequestForm(FlaskForm):

    email = EmailField('Email', validators=[validators.input_required()],
                       render_kw={"placeholder": "Enter your email "})
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    new_password = PasswordField('New Passwrd',
                                 [validators.DataRequired(), validators.length(min=4, max=80)]
                                 )






