"""Test fixtures and sample data."""

SAMPLE_INSTAGRAM_CAPTION = """
The BEST banana bread you'll ever make 🍌

Serves 8 | Prep time: 10 minutes | Cook time: 55 minutes

Ingredients:
- 3 very ripe bananas
- 1/3 cup melted butter
- 3/4 cup sugar
- 1 egg, beaten
- 1 tsp vanilla extract
- 1 tsp baking soda
- Pinch of salt
- 1.5 cups all-purpose flour

Instructions:
1. Preheat oven to 350°F. Grease a 9x5 loaf pan.
2. Mash bananas until smooth. Stir in butter.
3. Mix in sugar, egg, and vanilla.
4. Add baking soda and salt; fold in flour — don't overmix!
5. Bake 55–65 min until a skewer comes out clean.
6. Cool 15 minutes in pan then turn onto a rack.

Notes: Freeze individual slices for up to 3 months. Add chocolate chips for fun!

#bananabread #baking @foodblogger
"""

SAMPLE_SCHEMA_JSON_LD = """{
  "@context": "https://schema.org/",
  "@type": "Recipe",
  "name": "Pasta al Pomodoro",
  "description": "A simple two-ingredient sauce that tastes like summer.",
  "prepTime": "PT5M",
  "cookTime": "PT25M",
  "totalTime": "PT30M",
  "recipeYield": "2 servings",
  "recipeCategory": "Pasta",
  "recipeCuisine": "Italian",
  "keywords": "pasta,vegetarian,dinner",
  "recipeIngredient": [
    "200g spaghetti",
    "400g can whole San Marzano tomatoes",
    "3 tbsp extra-virgin olive oil",
    "2 garlic cloves, thinly sliced",
    "Salt and pepper to taste"
  ],
  "recipeInstructions": [
    {"@type": "HowToStep", "text": "Bring water to boil and salt it."},
    {"@type": "HowToStep", "text": "Warm olive oil and add garlic."},
    {"@type": "HowToStep", "text": "Add tomatoes and simmer for 20 minutes."},
    {"@type": "HowToStep", "text": "Cook pasta and toss with sauce."}
  ]
}
"""

SAMPLE_HTML_WITH_SCHEMA = f"""
<!DOCTYPE html>
<html>
<head>
  <title>Pasta al Pomodoro Recipe</title>
</head>
<body>
  <h1>Pasta al Pomodoro</h1>
  <p>A simple pasta recipe...</p>
  <script type="application/ld+json">
  {SAMPLE_SCHEMA_JSON_LD}
  </script>
</body>
</html>
"""

SAMPLE_HTML_NO_SCHEMA = """
<!DOCTYPE html>
<html>
<head>
  <title>Simple Pasta Recipe</title>
</head>
<body>
  <nav>Navigation stuff</nav>
  <h1>Quick Pasta</h1>
  
  <h2>Ingredients</h2>
  - 200g pasta
  - 400g tomatoes
  - 3 cloves garlic
  
  <h2>Instructions</h2>
  1. Boil water
  2. Cook pasta
  3. Toss with sauce
  
  <footer>Footer content</footer>
</body>
</html>
"""
