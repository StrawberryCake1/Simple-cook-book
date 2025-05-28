from flask import Flask, redirect, url_for, render_template, request, jsonify, send_file
import requests #Api request python #request just for user flask
from database import RecipeDatabase, UserDatabase, dbFunctions
import matplotlib.pyplot as plt
import os
app = Flask(__name__)
app.secret_key = "your_secret_key"
@app.route("/")
def home():
    return render_template("base.html")
# Login
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        #Requsting data from user
        user = request.form["un"]
        password = request.form["psw"]
        #Login user and redirect him to secret after login page
        if dbFunctions.loginChercker(user, password):
            return render_template("afterLogin.html")
        else:
            return render_template("login.html")
    return render_template("login.html")

# Register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        #Requsting data from user
        username = request.form["un"]
        password = request.form["psw"]
        repeat_password = request.form["repeat_psw"]

        if password != repeat_password:
            return redirect(url_for("register"))
        try:
            #Insert user to user database
            UserDatabase.insert_user(username, password)
            return redirect(url_for("login"))
        except Exception as e:
            return redirect(url_for("register"))
    return render_template("register.html")

#Find recipe by ingridients
@app.route("/findRecipeByIngridient")
def findRecipeByIngridient():
    return render_template("findRecipeByIngridient.html")
#Find recipe by name
@app.route("/findRecipeByName")
def findRecipeByName():
    return render_template("findRecipeByName.html", content="Testing")
#Find recipe by area
@app.route("/findRecipeByArea")
def findRecipeByArea():
    return render_template("findRecipeByArea.html", content="Testing")

# Create Recipe
@app.route("/createRecipe", methods=["POST", "GET"])
def createRecipe():
    if request.method == "POST":
        #Requsting recipe data
        title = request.form["title"]
        ingredients = request.form["ingredients"]
        instructions = request.form["instructions"]
        area = request.form["area"]

        if all([title, ingredients, instructions, area]):
            RecipeDatabase.insert_recipe("recipes", title, ingredients, instructions, area)
    return render_template("createRecipe.html")
#Send api request and returns it in json format
def fetch_mealdb_data(endpoint, params):
    base_url = "https://www.themealdb.com/api/json/v1/1/"
    response = requests.get(f"{base_url}{endpoint}", params=params)
    if response.status_code == 200:
        return response.json()
    return {"error": f"Request failed with status code {response.status_code}"}
#api request method that returns data
@app.route("/api/search")
def search():   
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "search param is empty"}), 400
    data = fetch_mealdb_data("search.php", {"s": query})
    return jsonify(data)
#api request method that returns data
@app.route("/api/filter")
def filter_by_ingredient():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "search param is empty"}), 400
    data = fetch_mealdb_data("filter.php", {"i": query})
    return jsonify(data)
#api request method that returns data
@app.route("/api/nwm")
def filter_by_area():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "search param is empty"}), 400
    data = fetch_mealdb_data("filter.php", {"a": query})
    return jsonify(data)
#Generating graph of recipe locations
def generate_statistics_plot(force_update=False):
    output_path = os.path.join("static", "statistics_plot.png")
    # Remove the existing file if force_update is True
    if force_update and os.path.exists(output_path):
        os.remove(output_path)

    # Generate the plot if it doesn't exist
    if not os.path.exists(output_path):  
        data = dbFunctions.count_by_location("recipes")
        locations = list(data.keys())
        counts = list(data.values())

        plt.figure(figsize=(10, 6))
        plt.bar(locations, counts, color="blue")
        plt.xlabel("Countries")
        plt.ylabel("Number of Recipes")
        plt.title("Recipes by Country")
        plt.xticks(rotation=45)
        plt.savefig(output_path)
        plt.close()

# Call the function with force_update=True to regenerate the graph
generate_statistics_plot(force_update=True)
#Statistics site
@app.route("/statistics")
def statistics():
    generate_statistics_plot()
    return render_template("statistics.html", image_url="/static/statistics_plot.png")
#Site for downloading the statistics image
@app.route("/download-statistics")
def download_statistics():
    file_path = os.path.join("static", "statistics_plot.png")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return redirect(url_for("statistics"))

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")  
    UserDatabase.create_table()
    app.run(debug=True)
