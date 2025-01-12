from django.shortcuts import render
from django.shortcuts import render
from django.http import JsonResponse
from decouple import config
import json
import google.generativeai as genai
import logging
import re 


genai.configure(api_key=config("GENERATIVE_AI_API_KEY"))

def home(request):
    return render(request, 'index.html')

def generate_recipe(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            ingredients = data.get("ingredients", [])
            cuisine = data.get("cuisine", "")

            ingredient_list = ", ".join(
                [f"{item['quantity']} of {item['ingredient']}" for item in ingredients]
            )
            prompt = (
                f"Create a recipe using these ingredients: {ingredient_list}. "
                f"Cuisine: {cuisine}. Provide a recipe name, list of ingredients, and step-by-step instructions (use * bullets). Don't add note."
            )

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            if not response.text or 'error' in response.text.lower():
                raise ValueError("Failed to generate a valid recipe. Response was empty or error-prone.")

            response_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", response.text)
            recipe_name = ""
            ingredients_section = []
            steps_section = []
            parsing_ingredients = False
            parsing_steps = False

            for line in response_text.split("\n"):
                clean_line = line.strip()

                if not clean_line:
                    continue

                clean_line = clean_line.lstrip('*').strip()

                if not recipe_name and not (parsing_ingredients or parsing_steps):
                    recipe_name = clean_line
                    continue

                if "Ingredients" in clean_line and not parsing_ingredients:
                    parsing_ingredients = True
                    parsing_steps = False
                    continue

                if "Steps" in clean_line or "Instructions" in clean_line:
                    parsing_ingredients = False
                    parsing_steps = True
                    continue

                if parsing_ingredients:
                    ingredients_section.append(clean_line)

                if parsing_steps:
                    steps_section.append(clean_line)

            if not recipe_name:
                recipe_name = "Unnamed Recipe"  

            return JsonResponse({
                "title": recipe_name,  
                "ingredients": ingredients_section,
                "steps": steps_section,
            }, safe=False)

        except Exception as e:
            logging.error(f"Error generating recipe: {str(e)}")
            return JsonResponse({"error": f"Error generating recipe: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)
