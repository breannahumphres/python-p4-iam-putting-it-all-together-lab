#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        errors = {}

        if 'username' not in data or 'password' not in data:
            return {"error": "Username and password are required."}, 422

        if errors:
            return errors, 422
        try:
            new_user = User(username=data["username"], image_url=data.get("image_url", ""), bio=data.get("bio", ""))
            new_user.password_hash = data["password"]
            db.session.add(new_user)
            db.session.commit()
            session["user_id"] = new_user.id
            return {
                "id": new_user.id,
                "username": new_user.username,
                "image_url": new_user.image_url,
                "bio": new_user.bio
                }, 201
       
        except IntegrityError:
            db.session.rollback()
            errors.setdefault("username", []).append("Username already exists.")
            return errors, 422
        except Exception as e:
            db.session.rollback()
            errors.setdefault("error", []).append(str(e))
            return errors, 422
#Handle sign up by implementing a POST /signup route. It should:
# Be handled in a Signup resource with a post() method.
# In the post() method, if the user is valid:
# Save a new user to the database with their username, encrypted password, image URL, and bio.
# Save the user's ID in the session object as user_id.
# Return a JSON response with the user's ID, username, image URL, and bio; and an HTTP status code of 201 (Created).
# If the user is not valid:
# Return a JSON response with the error message, and an HTTP status code of 422 (Unprocessable Entity).
# Note: Recall that we need to format our error messages in a way that makes it easy to display the information in our frontend. For this lab, because we are setting up multiple validations on our User and Recipe models, our error responses need to be formatted in a way that accommodates multiple errors.


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = User.query.where(User.id ==user_id).first()
            if user:
                return {
                     "id": user.id,
                    "username": user.username,
                     "image_url": user.image_url,
                     "bio": user.bio
                }, 200
            else:
                session.pop("user_id", None)
                return {}, 401
        else:
            return {}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()

        user = User.query.where(User.username == data["username"]).first()
        if user and user.authenticate(data["password"]):
            session["user_id"] = user.id
            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
                }, 201
        else: 
            return {"Error": "invalid username"}, 401

class Logout(Resource):
    def delete(self):
        if 'user_id' not in session or session.get('user_id') is None:
            return {"error": "Not logged in"}, 401
        session.pop("user_id")
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "not logged in"}, 401
        recipes = Recipe.query.filter_by(user_id=user_id).all()
        return [
            {
                "title": recipe.title,
                "instructions":recipe.instructions,
                "minutes_to_complete":recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username,
                    "image_url": recipe.user.image_url,
                    "bio":recipe.user.bio
                }
            }
            for recipe in recipes
        ], 200
    
    def post(self):
        user_id = session.get("user_id")
        
        if not user_id:
            return {"error": "Not logged in"}, 401
        data = request.get_json()

        if not all(key in data for key in ["title", "instructions", "minutes_to_complete"]):
            return {"error": "missing required fields: title, instructions, and minutes_to_complete."}, 422
        if len(data["instructions"]) <50:
            return {"error": "Instructions must be at least 50 characters long."},422
        try:
            new_recipe = Recipe(
                title =data["title"],
                instructions= data["instructions"],
                minutes_to_complete = data["minutes_to_complete"],
                user_id = user_id
            )
            db.session.add(new_recipe)
            db.session.commit()
            user = new_recipe.user

            return {
                "title": new_recipe.title,
                "instructions":new_recipe.instructions,
                "minutes_to_complete":new_recipe.minutes_to_complete,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio":user.bio
                }
            }, 201
        except IntegrityError:
            db.session.rollback()
            return {"error":"There was an issue with the data provided"}, 422
        except Exception as e:
            return {"error": str(e)}, 500



#     Users should only be able to view recipes on our site after logging in.

# Handle recipe viewing by implementing a GET /recipes route. It should:

# Be handled in a RecipeIndex resource with a get() method
# In the get() method, if the user is logged in (if their user_id is in the session object):
# Return a JSON response with an array of all recipes with their title, instructions, and minutes to complete data along with a nested user object; and an HTTP status code of 200 (Success).
# If the user is not logged in when they make the request:
# Return a JSON response with an error message, and a status of 401 (Unauthorized).
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)