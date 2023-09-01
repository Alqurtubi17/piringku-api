import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def calculate_akg_recommendation(akg_data):
    # Load and preprocess data
    akg_df = preprocess_akg_data(akg_data)
    food_df = preprocess_food_data(akg_df)

    # Calculate nutrient scores and cosine similarity
    nutrient_scores_tfidf = calculate_nutrient_scores_tfidf(food_df)
    cosine_sim = cosine_similarity(nutrient_scores_tfidf, nutrient_scores_tfidf)

    # Get the index of the selected food with highest energy score
    selected_food_index = food_df['Energi_score'].idxmax()

    # Get the similar foods based on cosine similarity
    similar_foods = list(enumerate(cosine_sim[selected_food_index]))

    # Sort similar foods by similarity score
    sorted_similar_foods = sorted(similar_foods, key=lambda x: x[1], reverse=True)

    # Define categories to consider
    categories_to_consider = ['Makanan Pokok', 'Lauk Hewani', 'Lauk Nabati', 'Sayuran', 'Buah']

    # Define energy ranges for each category
    category_energy_ranges = {
        'Makanan Pokok': (200, 250),
        'Lauk Hewani': (150, 200),
        'Lauk Nabati': (90, 150),
        'Sayuran': (40, 120),
        'Buah': (75, 120)
    }

    # Initialize recommended foods and weights
    recommended_foods = []

    # Iterate through categories to consider
    for category in categories_to_consider:
        remaining_energy = akg_df['Energi'].iloc[0] * 0.3 # Set the remaining energy for each meal
        category_foods = []

        for i, score in sorted_similar_foods[1:]:
            recommended_food = food_df.iloc[i]
            if recommended_food['Kategori'] == category:
                food_energy = recommended_food['Energi']

                # Check if the food energy is within the specified range for the category
                min_energy, max_energy = category_energy_ranges[category]

                # Calculate the food weight based on energy and remaining energy
                food_weight = min_energy / food_energy
                if min_energy <= food_weight and food_weight <= max_energy:
                    category_foods.append({
                        'Makanan': recommended_food['Makanan'],
                        'Kategori': recommended_food['Kategori'],
                        'Berat': food_weight
                    })
                    remaining_energy -= food_energy * food_weight

            if remaining_energy <= 0 or len(category_foods) >= 1:
                break

        recommended_foods.extend(category_foods)

    # Calculate total energy recommended based on selected foods
    total_energy_recommended = sum([food['Berat'] * food_df.loc[food_df['Makanan'] == food['Makanan'], 'Energi'].iloc[0] for food in recommended_foods])

    return recommended_foods, total_energy_recommended

def preprocess_akg_data(akg_data):
    # Create AKG DataFrame
    akg_df = pd.DataFrame(akg_data)

    # Calculate BMR and AKG based on user input
    if akg_df.loc[0, 'JenisKelamin'] == 'L':
        akg_df['BMR'] = 66 + (13.7 * akg_df.loc[0, 'BeratBadan']) + (5 * akg_df.loc[0, 'TinggiBadan']) - (6.8 * akg_df.loc[0, 'Umur'])
    else:
        akg_df['BMR'] = 655 + (9.6 * akg_df.loc[0, 'BeratBadan']) + (1.8 * akg_df.loc[0, 'TinggiBadan']) - (4.7 * akg_df.loc[0, 'Umur'])

    # Calculate energy based on activity level
    af = akg_df.loc[0, 'AktivitasFisik']
    if af == 'Ringan':
        energy_multiplier = 1.3
    elif af == 'Sedang':
        energy_multiplier = 1.45
    else:
        energy_multiplier = 1.75

    akg_df['Energi'] = akg_df['BMR'] * energy_multiplier
    akg_df['Protein'] = akg_df['Energi'] * 0.15
    akg_df['Lemak'] = akg_df['Energi'] * 0.225
    akg_df['Karbohidrat'] = akg_df['Energi'] * 0.625
    return akg_df

def preprocess_food_data(akg_df):
    # Load and preprocess food data

    food_df = pd.read_csv('https://raw.githubusercontent.com/Alqurtubi17/piringku-api/main/ini_piringku/Makanan.csv')

    # Calculate nutrient scores for each food
    nutrients = ['Energi', 'Protein', 'Lemak', 'Karbohidrat']
    for nutrient in nutrients:
        food_df[nutrient + '_score'] = food_df[nutrient] / akg_df[nutrient].iloc[0]

    # Convert nutrient scores to text for TF-IDF vectorization
    food_df['nutrient_scores_text'] = food_df.apply(lambda row: ' '.join(map(str, [row[nutrient + '_score'] for nutrient in nutrients])), axis=1)

    return food_df

def calculate_nutrient_scores_tfidf(food_df):
    vectorizer = TfidfVectorizer()
    nutrient_scores_tfidf = vectorizer.fit_transform(food_df['nutrient_scores_text'])
    return nutrient_scores_tfidf
