from flask import Flask, render_template, request, jsonify
import requests
import openai

app = Flask(__name__)

# Spoonacular API key and URL for finding recipes
SPOONACULAR_API_KEY = '29e60da263a4461ab634da401a267260'
SPOONACULAR_API_URL = 'https://api.spoonacular.com/recipes/findByNutrients'

# OpenAI API key to allow user to chat with the chatbot
OPENAI_API_KEY = xxx #NEED TO FIX
openai.api_key = OPENAI_API_KEY

@app.route('/')
def index():
    # Loads main page where users can search for recipes by calorie count
    return render_template('index.html')

@app.route('/get_recipes', methods=['POST'])
def get_recipes():
    # Find the calorie limit from the user
    calories = request.form['calories']

    # Prepare headers and parameters for the API request
    headers = {
        'Content-Type': 'application/json'
    }
    params = {
        'maxCalories': calories,
        'number': 10,  # We want to return 10 recipes
        'apiKey': SPOONACULAR_API_KEY
    }

    # Make a request to Spoonacular API to fetch recipes based on the calorie limit
    response = requests.get(SPOONACULAR_API_URL, headers=headers, params=params)

    # Debugging info to check the status of the API response
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content.decode()}")

    # If the API call was successful, load the recipes page with the results
    if response.status_code == 200:
        recipes = response.json()
        return render_template('recipes.html', recipes=recipes)
    else:
        # If something went wrong, return an error message
        return f"Error: {response.status_code}, {response.content.decode()}"

@app.route('/chatbot')
def chatbot():
    # Renders the chatbot interface page
    return render_template('chatbot.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    # Get the user's message from the chatbot form
    user_message = request.form['message']
    
    try:
        # Make a request to OpenAI's API to get a response from the chatbot
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the model to use
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only answers questions about food and nutrition."},
                {"role": "user", "content": user_message},
            ],
        )
        
        # Extract the chatbot's response from the API response
        chatbot_response = response['choices'][0]['message']['content'].strip()
        print(f"Chatbot response: {chatbot_response}")  # Debugging: See what the chatbot said
        return jsonify({'response': chatbot_response})
    except Exception as e:
        # If something went wrong, log the error and notify the user
        print(f"Error: {e}")  # Print the error for debugging
        return jsonify({'response': f"Sorry, something went wrong. Error: {str(e)}"})

if __name__ == '__main__':
    # Start the Flask app in debugging mode for finding errors faster
    app.run(debug=True)

""" WHAT TO DO NEXT
1. Fix Chatbot
2. Add diet preferences (High protein, keto, vegan...)
3. Filter meals depending on what time the user wants to prepare for (Bfast, lunch, dinner, or snack)
4. Potentially have feature where user can take picture of foods where they can receive breakdown of all of what 
is contained in the meal with nutrional values or even other recommendations (healthier ones)
5. Find a way to display the recipes within the web app and not have users be redirected to Spoonacular
6. Add more images and improve overall design with more colour variety
7. Have the chatbot be a bubble in the corner, so that it looks more appealing for users
8. Potentially add a login page (php required)
9. Collect information about user's goals and personalise the meals to fit this goal (lose weight/build muscle...)
10. If users have any allergies, web app could filter out what meals to prepare."""
