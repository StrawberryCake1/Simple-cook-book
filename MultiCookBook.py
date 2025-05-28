from flask import Flask, redirect, url_for, render_template, request, jsonify, flash, send_file
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from database import RecipeDatabase, UserDatabase, dbFunctions
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Home
@app.route("/")
def home():
    return render_template("base.html", content="Testing")

# Login
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["un"]
        password = request.form["psw"]

        if dbFunctions.loginChercker(user, password):
            flash("Login successful!", "success")
            return render_template("afterLogin.html")
        else:
            flash("Invalid username or password.", "danger")
            return render_template("login.html")
    return render_template("login.html")

# Register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["un"]
        password = request.form["psw"]
        repeat_password = request.form["repeat_psw"]

        if password != repeat_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register"))
        
        hashed_password = generate_password_hash(password)
        try:
            UserDatabase.insert_user(username, hashed_password)
            flash("Registration successful!", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash("Error registering user. User might already exist.", "danger")
            return redirect(url_for("register"))
    return render_template("register.html")

# Recipe search routes
@app.route("/findRecipeByIngridient")
def findRecipeByIngridient():
    return render_template("findRecipeByIngridient.html")

@app.route("/findRecipeByName")
def findRecipeByName():
    return render_template("findRecipeByName.html", content="Testing")

@app.route("/findRecipeByArea")
def findRecipeByArea():
    return render_template("findRecipeByArea.html", content="Testing")

# Create Recipe
@app.route("/createRecipe", methods=["POST", "GET"])
def createRecipe():
    if request.method == "POST":
        title = request.form["title"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]
        area = request.form["area"]

        if all([title, ingredients, instructions, area]):
            RecipeDatabase.insert_recipe("recipes", title, ingredients, instructions, area)
            flash("Recipe created successfully!", "success")
        else:
            flash("All fields are required!", "danger")
    return render_template("createRecipe.html")

# API for search
def fetch_mealdb_data(endpoint, params):
    """Helper function to fetch data from the MealDB API."""
    base_url = "https://www.themealdb.com/api/json/v1/1/"
    response = requests.get(f"{base_url}{endpoint}", params=params)
    if response.status_code == 200:
        return response.json()
    return {"error": f"Request failed with status code {response.status_code}"}

@app.route("/api/search")
def search():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "search param is empty"}), 400
    data = fetch_mealdb_data("search.php", {"s": query})
    return jsonify(data)

@app.route("/api/filter")
def filter_by_ingredient():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "search param is empty"}), 400
    data = fetch_mealdb_data("filter.php", {"i": query})
    return jsonify(data)

@app.route("/api/nwm")
def filter_by_area():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "search param is empty"}), 400
    data = fetch_mealdb_data("filter.php", {"a": query})
    return jsonify(data)

# Generate and cache statistics plot
def generate_statistics_plot():
    """Generates and saves a statistics plot if it doesn't exist."""
    output_path = os.path.join("static", "statistics_plot.png")
    if not os.path.exists(output_path):  # Generate only if it doesn't exist
        data = dbFunctions.count_by_location("recipes")
        locations = list(data.keys())
        counts = list(data.values())

        plt.figure(figsize=(10, 6))
        plt.bar(locations, counts, color="skyblue")
        plt.xlabel("Countries")
        plt.ylabel("Number of Recipes")
        plt.title("Recipes by Country")
        plt.xticks(rotation=45)
        plt.savefig(output_path)
        plt.close()

@app.route("/statistics")
def statistics():
    generate_statistics_plot()
    return render_template("statistics.html", image_url="/static/statistics_plot.png")

@app.route("/download-statistics")
def download_statistics():
    file_path = os.path.join("static", "statistics_plot.png")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    flash("Statistics plot not found.", "danger")
    return redirect(url_for("statistics"))

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")  # Ensure static directory exists
    UserDatabase.create_table()
    app.run(debug=True)
