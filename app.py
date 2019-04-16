from flask import Flask, render_template, redirect

# Import our pymongo library, which lets us connect our Flask app to our Mongo database.
import pymongo
import mission_to_mars
from flask_pymongo import PyMongo

# Create an instance of our Flask app.
app = Flask(__name__)

# Create connection variable
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)

# Set route
@app.route('/')
def index(name = None):
    # Store the entire team collection in a list
    news_instance = mongo.db.request_instances.find_one()
    return render_template('index.html', news = news_instance)


@app.route("/scrape")
def scraper():
    news = mongo.db.request_instances
    news_update = mission_to_mars.scrape()
    news.update({}, news_update, upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
