import os
import sys
import io
import sqlalchemy
import requests
import json

from flask import Flask, flash, redirect, render_template, request, session, jsonify
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

# APIKEY GOODREADS
goodreadsKey = os.environ.get("GOODREADS_KEY")


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
				return render_template("errorPage.html", message="DB-error while storing user")
		else:
			return redirect("/register")

		return render_template("search.html")
	else:
		return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
	print(">>>>> SEARCH <<<<<")
	
	if request.method == "POST":
		if validateEmptySearch() == False:
			return render_template("search.html")
		books = searchISBN()
		if books == []:
			flash('Could not find any titles', 'info')

		return render_template("search.html", books=books)
	else:
		return render_template("search.html")


@app.route("/title/<int:id>", methods=["GET", "POST"])
@login_required
def title(id):
	print(">>>>> TITLEID <<<<<")
	# Lists details about a single book.
	bookID = id  #see below---- is hidden ID needed or only for routing?
	# Make sure book exists.
	title = db.execute("SELECT * FROM books WHERE id = :id", {"id": id}).fetchone()
	if title is None:
		flash('Their is no such book', 'warning')
		return render_template("errorPage.html")

	y = getGoodreadsRating(title[4])

	reviews = loadReviews(id)

	if request.method == "POST":

		userID = session["user_id"]
		bookID = int(request.form.get("title_id"), 0) #make the ID een integer
		review = request.form.get("review")
		rating = request.form.get("rating")

		if validateRating() == False:
			return render_template("title.html", title=title, res=y, reviews=reviews)

		if checkReviewUser(userID, bookID) == False:
			flash('You already posted a review', 'warning')
			return render_template("title.html", title=title, res=y, reviews=reviews)

		try:
			db.execute("INSERT INTO reviews(id_book, id_user, review, rating) VALUES (:id_book, :id_user, :review, :rating)",
						{"id_book": bookID, "id_user": userID, "review": review, "rating": rating})
			db.commit()
			reviews = loadReviews(id) # Need to see my new review too ;)
		except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
			print(">>>>>>>>>>>>>> ERROR START <<<<<<<<<<<<<<<<")
			print(e)
			print(">>>>>>>>>>>>>> ERROR END <<<<<<<<<<<<<<<<")
			flash('An error occured, please retry', 'error')
			return render_template("errorPage.html", message=e)

	return render_template("title.html", title=title, res=y, reviews=reviews)


@app.route("/logout")
def logout():
	print(">>>>> Logout User <<<<<")

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


@app.route("/api/<isbn>")
def isbn_api(isbn):
	print(">>>>> API <<<<<")
	try:
		title = db.execute("SELECT * FROM books WHERE isbn = :isbn",
							{"isbn": isbn}).fetchone()

		if title == None:
			return jsonify({"error": "Invalid isbn"}), 404
		else:
			y = getGoodreadsRating(isbn)

	except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
		print(">>>>>>>>>>>>>> ERR(R)RROR START <<<<<<<<<<<<<<<<")
		print(e)
		print(">>>>>>>>>>>>>> ERR(R)RROR END <<<<<<<<<<<<<<<<")
		return jsonify({"error": "Invalid isbn"}), 500
	return jsonify ({
			"title": title[2].rstrip(),
    		"author": title[0].rstrip(),
    		"year": title[3],
    		"isbn": isbn,
    		"review_count": y[0],
    		"average_score": y[1]
		})


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

		if len(username) > 16:
			flash('The username should contain a maximum of 16 characters', 'warning')
			return False

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

		except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
			print(e)
			flash('An error occured, please retry', 'error')
			return render_template("errorPage.html")


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
		flash('Please provide a username', 'warning')
		return False
	else:
		return True


def validateEmptyPassword():
	if not request.form.get("password"):
		flash('Please, provide a password', 'warning')
		return False
	else:
		return True 		


def validateEmptySearch():
	if not request.form.get("key"):
		flash('Please, provide a search keyword', 'warning')
		return False
	else:
		return True


def validateRating():
	if int(request.form.get("rating")) > 0 and int(request.form.get("rating")) < 6:
		return True
	else:
		flash('Rating shoulde be numeric (1-5)', 'warning')
		return False


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

		# Create and save uses session
		result = db.execute("SELECT id FROM users WHERE username = :username",
										{"username": username}).fetchone()
		session["user_id"] = result[0]
		if session["user_id"] == None:
			flash('An error occured, please retry', 'error')
			return False 
	except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
		print(e)
		flash('An error occured, please retry', 'error')
		return False 
	return True
	

def searchISBN():
	print(">>>>> searchISBN <<<<<")
	#Find results based on isbn
	key = request.form.get("key")

	# CustomerName LIKE '%or%'

	try:
		books = db.execute("SELECT * FROM books WHERE (isbn ILIKE '%' || :key || '%') \
									OR (title ILIKE '%'  || :key || '%') \
									OR author ILIKE '%'  || :key || '%'", 
	    							{"key": key}).fetchall()

	except ValueError:
		return False
	return books


def loadReviews(id):
	print(">>>>> loadReviews <<<<<")
	#load all reviews for title

	try:
		reviews = db.execute("SELECT * FROM reviews WHERE id_book = :id_book",
									{"id_book": id})
	except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
		print(e)
		flash('An error occured, please retry', 'error')
		return render_template("errorPage.html")
	return reviews


def checkReviewUser(userID, bookID):
	print(">>>>> checkReviewUser")

	try:
		if db.execute("SELECT * FROM reviews WHERE id_user = :id_user AND id_book = :id_book",
							{"id_user": userID, "id_book": bookID}).fetchone() == None:
			return True
		else:
			return False
	except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
		print(e)
		return render_template("errorPage.html")
	return True


def getGoodreadsRating(title):
	res = requests.get("https://www.goodreads.com/book/review_counts.json",
					params={"key":os.environ.get("GOODREADS_KEY"),"isbns":title})
	#proces error 404
	if res.status_code == 404:
		y = ["n.a.","n.a."]
		return y

	result = res.json()

	x = result["books"][0]
	y = [x["text_reviews_count"],x["average_rating"]]

	return y


