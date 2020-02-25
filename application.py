import os
import sys
import io

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
	print("method", request.method)
	# Forget any user
	session.clear()

	# User reached route via POST (as by submitting a form via POST)
	if request.method == "POST":

		# Ensure username was submitted
		if not request.form.get("username"):
		    flash("Please, provide your username", 'warning')
		    return render_template("login.html")

		# Ensure password was submitted
		elif not request.form.get("password"):
		    flash("Please, provide your password", 'warning')
		    return render_template("login.html")

		# Query database for username
		print(">>>>> Query DB <<<<<") 

		# Get form information.
		username = request.form.get("username")
		try:
		    if username == db.execute("SELECT username FROM users WHERE username = :username", 
		    							{"username": username}).fetchone():
		    	print("username ", username)
		    else:
		    	flash("Your username or password is wrong", 'warning') # For security name both so risk of guessing is lower
		    	return render_template("login.html")
		except ValueError:
		    flash("Your username or password is wrong", 'warning') # For security name both so risk of guessing is lower
		    return render_template("login.html")

		# Ensure username exists and password is correct
		#for row in rows:
		if not check_password_hash(row[2], request.form.get("password")):
			flash("Your username or password is wrong", 'warning') # For security name both so rik of guessing is lower
			return render_template("login.html")
		
		# Remember which user has logged in
	    #session["user_id"] = row[0]

		print(">>>>> Redirect user to home page <<<<<")
		# Redirect user to home page
		flashMessage = "Welcome in the House of Books again, " + request.form.get("username")
		flash(flashMessage, 'info')

		return redirect("/search")

	    # User reached route via GET (as by clicking a link or via redirect)
	else:
		return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
	print(">>>>> Register User <<<<<")

	if request.method == "POST":
		
		if (validateUsername() and  validatePassword()) == True:
			print("# Do nothing")
		else:
			return redirect("/register")

		return render_template("landingPage.html")
	else:
		return render_template("register.html")


@app.route("/logout")
def logout():
	"""Log user out"""

	# Forget any user_id
	session.clear()

	# Redirect user to login form
	return redirect("/")


def validateUsername():
	# Check username
	if not request.form.get("username"):
		flash('Please provide a username', 'info')
		return False
	else:
		# Check if username exists in database
		username = request.form.get("username")
		
		try:
			if username == db.execute("SELECT username FROM users WHERE username = :username", 
										{"username": username}).fetchone():
				flash('The username already exists', 'info')
				return False
		except:
			flash('An error occured, please retry', 'error')
			return False
	
	return True


def validatePassword():
	print("Check if a password has been provided")
	if not request.form.get("password"):
		flash('Please, provide a password', 'info')
		return False 

	# Check if password not less than 6 characters
	if len(request.form.get("password")) < 6:
	    flash('Password should be a least 6 characters', 'info')
	    return False 

	print("Check is both password match (password & confirmation)")
	if request.form.get("password") != request.form.get("confirmation"):
	    flash('Password don\'t match', 'info')
	    return False 

	return True   

