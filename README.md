# Project 1 - The House of Books

Web Programming with Python and JavaScript

#LandingPage
This is the landing page users will be turned to whennot logged. you can either opt for login or register. The layout defers form the rest of the webpage, so it has also a separate styesheet.

It has also a invitational text for the users

#Register
Here a reader can register him/herself. Validations:
-username: max 16 char and should not exist
-password: - min 6 characters - both passwords should match

#Login
-User must exist
-password must match with stored password

#Search
user can search on (parts of) isbn, title, author. The results are presented as links so a user can link to the detailpage(title.htm)

#Title
Shows details of a book, including ratings as provided via GOODREAD.com. It also shows a list of local reviews and a user can add a review for this book (one review per book only)

#API
calling the API will result in a JSON-reply or a 404 in case not found








ToDO
====

search.html
-max record to be returned in search.html
-optime the query
-highlight searchresults (searched on 2222 then highlight in the data all text with 2222 - javascript?)
-make it responsive

error.html
-url does not change to error

search
-maximum of records to be returned
