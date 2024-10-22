import heapq  # For priority queue
from flask import Flask, render_template, request, jsonify
import requests
import openai

app = Flask(__name__)

# Spoonacular API key and URL for finding recipes
SPOONACULAR_API_KEY = '29e60da263a4461ab634da401a267260'
SPOONACULAR_API_URL = 'https://api.spoonacular.com/recipes/findByNutrients'

# Stack to store meal history
meal_history = []

# Priority queue to store recipes by protein content
recipe_queue = []

# OpenAI API key to allow user to chat with the chatbot
OPENAI_API_KEY = 'your_openai_api_key'
openai.api_key = OPENAI_API_KEY

@app.route('/')
def index():
    return render_template('index.html', meal_history=meal_history)

@app.route('/get_recipes', methods=['POST'])
def get_recipes():
    calories = request.form['calories']
    headers = {'Content-Type': 'application/json'}
    params = {
        'maxCalories': calories,
        'number': 10,
        'apiKey': '29e60da263a4461ab634da401a267260'
    }
    response = requests.get('https://api.spoonacular.com/recipes/findByNutrients', headers=headers, params=params)
    if response.status_code == 200:
        recipes = response.json()

        return render_template('recipes.html', recipes=recipes, meal_history=meal_history)
    else:
        return f"Error: {response.status_code}, {response.content.decode()}"

# Function to push recipes into the priority queue based on protein content
def add_recipe_to_queue(recipe):
    # Ensure the protein value is a number (float or int)
    if 'protein' in recipe and recipe['protein']:
        try:
            protein = float(recipe['protein'])  # Convert protein to a float
            heapq.heappush(recipe_queue, (-protein, recipe))  # Use negative to prioritize higher protein
        except ValueError:
            print(f"Error converting protein value for recipe: {recipe['title']}")


# Route to fetch and suggest recipes based on protein content
@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    calories = request.form['calories']
    headers = {'Content-Type': 'application/json'}
    params = {
        'maxCalories': calories,
        'number': 10,
        'apiKey': '29e60da263a4461ab634da401a267260'

    }
    response = requests.get('https://api.spoonacular.com/recipes/findByNutrients', headers=headers, params=params)
    if response.status_code == 200:
        recipes = response.json()

        # Clear the queue before adding new recipes
        global recipe_queue
        recipe_queue = []

        # Add each recipe to the priority queue based on protein content
        for recipe in recipes:
            if 'protein' in recipe:
                add_recipe_to_queue(recipe)

        # Suggest the highest-priority recipe (highest protein)
        if recipe_queue:
            best_recipe = heapq.heappop(recipe_queue)[1]  # Extract the recipe from the priority queue
            return render_template('suggestions.html', recipe=best_recipe)
        else:
            return "No suitable recipes found."
    else:
        return f"Error: {response.status_code}, {response.content.decode()}"

@app.route('/log_meal', methods=['POST'])
def log_meal():
    meal = request.form['meal']
    meal_history.append(meal)
    return render_template('index.html', meal_history=meal_history)

@app.route('/undo_meal', methods=['POST'])
def undo_meal():
    if meal_history:
        meal_history.pop()
    return render_template('index.html', meal_history=meal_history)

@app.route('/clear_meals', methods=['POST'])
def clear_meals():
    global meal_history
    meal_history = []
    return render_template('index.html', meal_history=meal_history)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['message']
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only answers questions about food and nutrition."},
                {"role": "user", "content": user_message},
            ],
        )
        chatbot_response = response['choices'][0]['message']['content'].strip()
        return jsonify({'response': chatbot_response})
    except Exception as e:
        return jsonify({'response': f"Sorry, something went wrong. Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
