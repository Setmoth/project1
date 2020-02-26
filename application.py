import os
import sys
import io
import sqlalchemy

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
	print(">>>>> index <<<<<")
	return render_template("landingPage.html")
    # return "Project 1: TODO"


@app.route("/login", methods=["GET", "POST"])
def login():
	print(">>>>> Log user in <<<<<")
	# Forget any user
	session.clear()

	# User reached route via POST (as by submitting a form via POST)
	if request.method == "POST":

		if validateAuth() == False:
			flash("Your username or password is wrong", 'warning') # For security name both so rik of guessing is lower
			return render_template("login.html")
		else:
			print(">>>>> Redirect user to the search page <<<<<")
			# Redirect user to home page
			flashMessage = "Welcome in your House of Books again, " + request.form.get("username")
			flash(flashMessage, 'info')

			return redirect("/search")

		    # User reached route via GET (as by clicking a link or via redirect)
	else:
		return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
	print(">>>>> Register User <<<<<")

	if request.method == "POST":
		
		if (validateRegisterUsername() and validateRegisterPassword()) == True:
			if storeUser() == False:
				return render_template("errorPage.html")
		else:
			return redirect("/register")

		return render_template("landingPage.html")
	else:
		return render_template("register.html")


@app.route("/search")
@login_required
def search():
	print(">>>>> SEARCH <<<<<")
	return render_template("search.html")


@app.route("/logout")
def logout():
	print(">>>>> Log user out <<<<<")

	# Forget any user_id
	session.clear()

	# Redirect user to login form
	return redirect("/")


@app.route("/errorPage")
@login_required
def errorPage():
	# Forget any user_id
	print("errorPage")
	session.clear
	return render_template("errorPage.html")	


@app.errorhandler(HTTPException)
def errorhandler(e):
	print(">>>>> internal_server_error <<<<<")
	return render_template('errorPage.html')
	#return render_template('errorPage.html', error=e), error.code


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


def validateRegisterUsername():
	# Check username
	if validateEmptyUsername() == False:
		return False
	else:
		# Check if username exists in database
		username = request.form.get("username")

		try:
			if db.execute("SELECT username FROM users WHERE username = :username", 
										{"username": username}).fetchone() == None:
				print("Do Nothing")
			else:	
				flash('The username already exists', 'info')
				return False
		except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
			flash('An error occured, please retry', 'error')
			return False
	return True


def validateRegisterPassword():
	if validateEmptyPassword() == False:
		return False

	# Check if password not less than 6 characters
	if len(request.form.get("password")) < 6:
	    flash('Password should be a least 6 characters', 'info')
	    return False 

	# Check if both password match (password & confirmation)
	if request.form.get("password") != request.form.get("confirmation"):
	    flash('Password don\'t match', 'info')
	    return False 

	return True


def validateAuth():
	if (validateLoginUsername() or validateLoginPassword()) == False:
		return False
	else:
		print(">>>>> Query DB <<<<<") 

		# Get form information.
		username = request.form.get("username")

		try:
			foundUser = db.execute("SELECT * FROM users WHERE username = :username", 
		    							{"username": username}).fetchone()

			if foundUser == None:
				return False

			if not username == foundUser[1].rstrip():
				return False

		except ValueError:
			return False

		# Ensure username exists and password is correct
		if not check_password_hash(foundUser[2].rstrip(), request.form.get("password")):
			return False
		else:
			# Remember which user has logged in
			session["user_id"] = foundUser[0]
			return True


def validateLoginUsername():
	if validateEmptyUsername() == False:
		return False
	else:
		return True


def validateLoginPassword():
	if validateEmptyPassword() == False:
		return False
	else:
		return True


def validateEmptyUsername():
	if not request.form.get("username"):
		flash('Please provide a username', 'info')
		return False
	else:
		return True


def validateEmptyPassword():
	if not request.form.get("password"):
		flash('Please, provide a password', 'info')
		return False
	else:
		return True 		


def storeUser():
	# Store username & password in database
	# Hash password
	password = request.form.get("password")
	hashedPassword = generate_password_hash(password)
	username = request.form.get("username") 

	try:
		db.execute("INSERT INTO users(username, password) VALUES (:username, :password)",
				{"username": username, "password": hashedPassword})
		db.commit()
	except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
		flash('An error occured, please retry', 'error')
		return False 

	return True
	

