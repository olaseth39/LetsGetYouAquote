
from flask import Flask, request, render_template, flash, redirect, url_for, session, logging, request, send_from_directory
from flask import send_from_directory
from flask_mysqldb import MySQL, MySQLdb
from details import DetailsForm, SignUpForm, SelectFieldToEditForm, AdminQuotationForm, ResetRequestForm
from calculateDimensionForSteelGrp import SteelGRPDimension
from ComputeBestDimension import BestDimension
from passlib.hash import sha256_crypt
from functools import wraps
from figure_converter import convert_to_words
import os
import uuid
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from random import randint
from itsdangerous import URLSafeTimedSerializer


# werkzeug means work stuff in German. It is a library that comes with flask

# import mysql.connector

app = Flask(__name__)

app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'olaseth39@gmail.com'
app.config['MAIL_PASSWORD'] = 'tjmqvazoyuafpwrm'
app.config['MAIL_USE_TLS'] = False          # Transport Layer Security
app.config['MAIL_USE_SSL'] = True           # Secure Socket Layers

# make an instance of Mail
mail = Mail(app)

# make an instance of mysql
mysql = MySQL(app)


# connect to mysql
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "quotation_formulator"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# We will be using File-uploads for uploading logos, picture or any document
# File-uploads allow flexibility and efficiency for files handling by our application

# set the path or directory where uploaded files would be stored
# app.config["UPLOADED_PHOTOS_DEST"] = "uploads"
app.config["UPLOAD_DIRECTORY"] = "static/uploads/"

# set maximum logo size limit
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024  # 1mb

# set the allowed extension
app.config["ALLOWED_EXTENSION"] = ['.jpg', '.jpeg', '.png', '.svg', '.gif']

# serial = Serializer(app.secret_key, 60)
# IMAGES is the extension of image files
# represents a single set of uploaded files.
# photos = UploadSet('photos', IMAGES)

# go through all the upload sets, get their configuration, and store the configuration on the app
# configure_uploads(app, photos)

# make an instance of the serializer
s = URLSafeTimedSerializer('mysecretkey')


@app.route('/', methods=['POST', 'GET'])
def home():
    form = DetailsForm(request.form)
    if request.method == 'POST' and form.validate():
        # get the values of data
        name = form.name.data
        email = form.email.data
        volume = form.volume.data
        type_of_tank = form.type_of_tank.data

        # get the value of unit_length for steel and grp to be used dynamically
        # create a cursor
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM grp_tank_details grp, steel_tank_details stl, vat vt")

        result = cur.fetchone()

        # convert result to a dictionary
        all_tanks_details = dict(result)

        # get the unit_length for grp
        grp_unit_length = all_tanks_details['unit_length']

        # get the unit_length for steel
        steel_unit_length = all_tanks_details['stl.unit_length']

        # check if the type_of_tank selected is steel or grp
        if type_of_tank == "Steel":
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_steel(), steel_unit_length, 1)
            get_best_dimension = best_dimension.compute_best_dimension()

        else:
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_grp(), grp_unit_length, 2)
            get_best_dimension = best_dimension.compute_best_dimension()

        # create a cursor
        # cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, volume, type_of_tank) \
                    VALUES(%s, %s, %s, %s)", (name, email, volume, type_of_tank))

        # commit to db
        cur.connection.commit()

        # create a cursor to get date
        cur = mysql.connection.cursor()
        cur.execute("SELECT date from users")
        row = cur.fetchall()

        # data = []
        # if len(row) > 1:
        #     data = row[-1]  # select the last data
        #     data.append(data)

        data = row[-1]  # select the last data

        # commit to db
        cur.connection.commit()

        # close connection
        cur.close()

        # return redirect(url_for("quotation"))
        return render_template('quotation.html',
                               volume=volume,
                               get_best_dimension=get_best_dimension,
                               name=name,
                               email=email,
                               type_of_tank=type_of_tank,
                               data=data,
                               result=result,
                               converter=convert_to_words
                             )

    return render_template('home.html', form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignUpForm(request.form)

    if request.method == 'POST' and form.validate():
        # get the values of data
        try:
            file = request.files.get('logo')
            # file = form.data['logo']
            print(file)
            if file:
                # sanitize the filename
                filename = secure_filename(file.filename)
                # get the extension
                extension = os.path.splitext(filename)[1].lower()
                # check for the right extension
                if extension not in app.config['ALLOWED_EXTENSION']:
                    flash("Image not allowed. Image must be jpeg, png, gif or svg", "warning")
                    return redirect("/signup")
                # save the file with the right extension
                file.save(os.path.join(app.config["UPLOAD_DIRECTORY"], filename))
            else:
                flash("You need to upload your company's logo. This will show on the quotation.", "warning")
                return redirect("/signup")

        # exception error for file larger than 100kb
        except RequestEntityTooLarge:
            flash("File must not be larger than 100kb", "warning")
            return redirect("/signup")

        # get the remaining data
        admin_name = form.name.data
        email = form.email.data
        country = form.country.data
        telephone = form.telephone.data
        company = form.company.data
        company_address = form.company_address.data
        password = sha256_crypt.hash(str(form.password.data))
        print(file)

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO admins(admin_name, email, country, telephone, password, company, company_address, logo_path) \
                                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                        (admin_name, email, country, telephone, password, company, company_address, filename))

            # commit to db
            cur.connection.commit()

            cur.close()

        except (MySQLdb.Error, MySQLdb.Warning) as error:
            return render_template("signup.html", error=error, form=form)

        token = s.dumps(email, salt='email-confirmation-key')
        msg = Message('confirmation', sender='olaseth39@gmail.com', recipients=[email])
        link = url_for('confirm', token=token, _external=True)
        msg.body = "Your confirmation link is " + link
        mail.send(msg)

        #flash("Signed up successfully", "success")

        #return redirect(url_for("login"))

        return render_template("confirmation_msg", email=email)

    return render_template("signup.html", form=form)


@app.route('/confirm/<token>', methods=['POST', 'GET'])
def confirm(token):
    try:
        email = s.loads(token, salt='email-confirmation-key', max_age=60)
    except Exception:
        return "<h1> Link expired </h1>"
    return "<h1> confirmation done </h1>"


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password_candidate = request.form['password']

        # create a cursor
        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM admins WHERE email = %s ", [email])

        cur.connection.commit()

        # Check if the email has been used
        if result > 0:
            data = cur.fetchone()
            password = data['password']
            user_id = data['id']

            # compare passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['email'] = email
                session['user_id'] = user_id
                flash("You are Logged in successfully", "success")
                return redirect(url_for("admin_page"))
            else:
                error = "Invalid email or password"
                return render_template("login.html", error=error)

            # close connection
            cur.close()

        else:
            error = "Email or Password not found"
            return render_template("login.html", error=error)

    return render_template("login.html")


# This is to check if the user is logged in
def is_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized page, please login", "Danger")
            return redirect(url_for("login"))
    return decorated_function


@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out", "success")

    return redirect(url_for("home"))


@app.route("/admin_page", methods=['GET', 'POST'])
@is_logged_in
def admin_page():

    # get the form to edit
    form = SelectFieldToEditForm(request.form)

    # create mysql connection
    cur = mysql.connection.cursor()

    # get admins quotation details from the admin_quote table
    cur.execute("SELECT company, company_address,logo_path, country FROM admins WHERE email = %s", [session['email']])

    # data for the particular client
    data = cur.fetchall()

    if request.method == 'POST' and form.validate():
        field_to_edit = form.field_to_edit.data

        price_list = ['GRP prices', 'Steel prices', 'Vat']
        tables = ['grp_tank_details', 'steel_tank_details', 'vat']

        for val in enumerate(price_list):
            if field_to_edit == price_list[val[0]]:
                table = tables[val[0]]
                result = cur.execute("SELECT * FROM {}".format(tables[val[0]]))

                cur.connection.commit()

                if result > 0:
                    output = cur.fetchall()
                    return render_template("admin_page.html", results=output, table=table, form=form, data=data)

        cur.close()

    return render_template("admin_page.html", form=form, data=data)


@app.route("/serve_image/<file_name>", methods=['GET', 'POST'])
def serve_image(file_name):
    return send_from_directory(app.config["UPLOAD_DIRECTORY"], file_name)


@app.route('/my_client', methods=['GET', 'POST'])
@is_logged_in
def my_client():
    # create mysql connection
    cur = mysql.connection.cursor()

    # get admins quotation details from the admin_quote table
    row = cur.execute("SELECT q.* FROM admins adm, admin_quote q WHERE adm.email = %s AND adm.id = q.admin_id",
                      [session['email']])

    details = cur.fetchall()

    return render_template('clients.html', details=details)


@app.route("/edit_page/<string:table>", methods=['GET', 'POST'])
@is_logged_in
def edit_page(table):
    # create cursor to get id
    cur = mysql.connection.cursor()

    row = cur.execute("SELECT * FROM {}".format(table))

    if row > 0:
        details = cur.fetchone()

        cur.connection.commit()

        if request.method == "POST":
            height_1m = request.form.get('height_1m', None)
            height_2m = request.form.get('height_2m', None)
            height_3m = request.form.get('height_3m', None)
            height_4m = request.form.get('height_4m', None)
            installation_price = request.form.get('installation_price', None)
            unit_length = request.form.get('unit_length', None)
            unit_price = request.form.get('unit_price', None)
            vat = request.form.get('vat', None)

            if table == "grp_tank_details":
                cur.execute("UPDATE grp_tank_details SET height_1m=%s,"
                            "height_2m=%s, height_3m=%s, height_4m=%s, installation_price=%s, unit_length=%s",
                            (height_1m, height_2m, height_3m, height_4m, installation_price, unit_length))

            elif table == "steel_tank_details":
                cur.execute("UPDATE steel_tank_details SET unit_price=%s, installation_price=%s, unit_length=%s",
                            (unit_price, installation_price, unit_length))

            elif table == "vat":
                cur.execute("UPDATE vat SET vat=%s ", (vat,))

            else:
                msg = "You have made a wrong selection"
                return render_template("edit_page.html", msg=msg)

            cur.connection.commit()

            cur.close()

            # what to do if post request is successful
            flash("Details updated successfully", "success")

            return redirect(url_for("admin_page"))

    return render_template("edit_page.html", details=details)


@app.route('/admin_quotation', methods=['POST', 'GET'])
@is_logged_in
def admin_quotation():

    form = AdminQuotationForm(request.form)
    if request.method == 'POST' and form.validate():
        # get the values of data
        name = form.name.data
        company = form.company.data
        address = form.address.data
        mobile = form.mobile.data
        email = form.email.data
        volume = form.volume.data
        type_of_tank = form.type_of_tank.data
        transport = form.transport.data

        # get the value of unit_length for steel and grp to be used dynamically
        # create a cursor
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM grp_tank_details grp, steel_tank_details stl, vat vt")

        result = cur.fetchone()

        # convert result to a dictionary
        all_tanks_details = dict(result)

        # get the unit_length for grp
        grp_unit_length = all_tanks_details['unit_length']

        # get the unit_length for steel
        steel_unit_length = all_tanks_details['stl.unit_length']

        # check if the type_of_tank selected is steel or grp
        if type_of_tank == "Steel":
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_steel(), steel_unit_length, 1)
            get_best_dimension = best_dimension.compute_best_dimension()

        else:
            calculate_volume = SteelGRPDimension(volume)
            best_dimension = BestDimension(calculate_volume.calculate_dimension_grp(), grp_unit_length, 2)
            get_best_dimension = best_dimension.compute_best_dimension()

        # get admin id
        cur.execute("SELECT * FROM admins WHERE email= %s", [session['email']])

        output = cur.fetchall()  # result is a tuple of dictionary

        dict_row = output[0]  # get the first element containing the values we need

        id_admin = dict_row['id']  # get the id value

        logo = dict_row['logo_path']  # get the logo

        # create a cursor
        # cur = mysql.connection.cursor()
        cur.execute("INSERT INTO admin_quote(name,company,address,mobile,email,volume,type_of_tank,transport, admin_id) \
                            VALUES(%s,%s, %s, %s, %s, %s, %s, %s, %s)",
                            (name, company, address, mobile, email, volume, type_of_tank, transport, id_admin))

        # commit to db
        cur.connection.commit()

        # create a cursor to get date
        cur = mysql.connection.cursor()
        cur.execute("SELECT date from admin_quote where email=%s", [email])
        row = cur.fetchall()

        data = row[-1]  # select the last data

        # commit to db
        cur.connection.commit()

        # close connection
        cur.close()

        # return redirect(url_for("quotation"))
        return render_template('quotation.html',
                               volume=volume,
                               company=company,
                               address=address,
                               mobile=mobile,
                               get_best_dimension=get_best_dimension,
                               name=name,
                               email=email,
                               type_of_tank=type_of_tank,
                               transport=transport,
                               data=data,
                               result=result,
                               logo=logo
                               )

    return render_template("admin_quotation.html", form=form)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ResetRequestForm()
    if request.method == "POST" and form.validate_on_submit():
        user = form.email.data
        code = str(uuid.uuid4())
        cur = mysql.connection.cursor()
        data = cur.execute("SELECT * FROM admins WHERE email = %s", [user])
        if data > 0:
            data = cur.fetchone()
            cur.execute("UPDATE admins SET token = %s WHERE email=%s", [code, user])
            cur.connection.commit()
            cur.close()
            flash("Reset request sent. You can now change your password.", "success")
            return redirect(url_for("reset_password", token=code))
        flash("You will receive a password reset email if your email is found in our database ", "success")
    return render_template('forgot_password.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    if request.method == "POST":
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        new_token = str(uuid.uuid4())

        if password != confirm_password:
            flash("Passwords does not match", "danger")
            return redirect(request.url)

        new_password = sha256_crypt.hash(str(password))
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admins WHERE token=%s", [token])

        user = cur.fetchone()
        if user:
            cur.execute("UPDATE admins SET password=%s, token=%s WHERE token=%s", [new_password, new_token, token])
            flash("Password updated successfully.", "success")
            cur.connection.commit()
            cur.close()
            return redirect(url_for("login"))

    return render_template('password_reset.html')


if __name__ == "__main__":
    print("Starting Flask server for QuotationFormulator application")
    # print(dir(form))
    app.secret_key = "quotationsecrettanks"

    # calculate_volume = SteelGRPDimension(79)
    # best_dimension = calculate_volume.calculate_dimension_grp()
    # print(best_dimension)

    # calculate_volume = SteelGRPDimension(70)
    # print(calculate_volume.calculate_dimension())
    # get_best_dimension = BestDimension(calculate_volume.calculate_dimension())
    # print(get_best_dimension.compute_best_dimension())

    app.run(debug=True)

