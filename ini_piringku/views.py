from django.shortcuts import render
from django.http import JsonResponse
from .utils import calculate_akg_recommendation
from django.views.decorators.csrf import csrf_exempt
import json, pandas as pd


@csrf_exempt
def calculate_recommendation(request):
    if request.method ==  ['GET', 'POST']:
        try:
            if request.method == 'POST':
            # Get user input from JSON data
            # Mengambil data dari body permintaan JSON
                data = json.loads(request.body)  # Assuming you are using Django REST framework
                umur = int(data.get('umur'))
                berat_badan = float(data.get('berat_badan'))
                tinggi_badan = float(data.get('tinggi_badan'))
                jenis_kelamin = data.get('jenis_kelamin')
                aktivitas_fisik = data.get('aktivitas_fisik')

                # Prepare AKG data
                akg_data = {
                    'Umur': [umur],
                    'BeratBadan': [berat_badan],
                    'TinggiBadan': [tinggi_badan],
                    'JenisKelamin': jenis_kelamin,
                    'AktivitasFisik': aktivitas_fisik
                }

                # Calculate recommended foods and total energy
                recommended_foods, total_energy_recommended = calculate_akg_recommendation(akg_data)

                # Create a list of recommended foods with categories and weights
                recommended_food_list = []
                for food in recommended_foods:
                    recommended_food_list.append({
                        'Makanan': food['Makanan'],
                        'Kategori': food['Kategori'],
                        'Berat': round(food['Berat'], 2)
                    })
            if request.method == 'POST':
                # Sample recommendation data (replace with your recommendation logic)
                recommended_foods = [
                    {'Makanan': 'Food 1', 'Kategori': 'Category 1', 'Berat': 100},
                    {'Makanan': 'Food 2', 'Kategori': 'Category 2', 'Berat': 150},
                ]
                total_energy_recommended = 500

            response_data = {
                'recommended_foods': recommended_food_list,
                'total_energy_recommended': round(total_energy_recommended, 2)
            }

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def add_diary_entry(request):
    if request.method == 'POST':
        try:
            user = request.user  # Assuming you have user authentication
            data = json.loads(request.body)  # Assuming you are using Django REST framework
            date_consumed = data.get('date_consumed')  # Date of consumption
            food_items = data.get('food_items', [])  # Food items consumed

            # Calculate nutritional values for each food item and store them in the database
            consumed_foods = []
            total_calories = 0
            total_protein = 0
            total_sugar = 0

            for item in food_items:
                food_id = item.get('food_id')
                weight = item.get('weight')  # Weight of the food item consumed

                # Retrieve the food item from the database
                food = FoodItem.objects.get(pk=food_id)

                # Calculate nutritional values based on weight
                calories = (food.calories / 100) * weight
                protein = (food.protein / 100) * weight
                sugar = (food.sugar / 100) * weight

                consumed_foods.append({
                    'food_id': food.id,
                    'food_name': food.name,
                    'weight': weight,
                    'calories': calories,
                    'protein': protein,
                    'sugar': sugar,
                })

                # Update total nutritional values
                total_calories += calories
                total_protein += protein
                total_sugar += sugar

            # Create a diary entry to store the consumed foods
            diary_entry = DiaryEntry.objects.create(
                user=user,
                date_consumed=date_consumed,
                consumed_foods=consumed_foods,
                total_calories=total_calories,
                total_protein=total_protein,
                total_sugar=total_sugar,
            )

            response_data = {
                'message': 'Diary entry created successfully',
                'entry_id': diary_entry.id
            }

            return JsonResponse(response_data, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=405)

def get_nutrition_diary(request, days_back=7):
    # Calculate the date from which to start fetching entries
    today = date.today()
    start_date = today - timedelta(days=days_back)

    # Get diary entries for the user within the specified period
    user = request.user  # Assuming you have user authentication
    diary_entries = DiaryEntry.objects.filter(user=user, date_consumed__gte=start_date, date_consumed__lte=today)

    # Serialize the diary entries to JSON
    diary_data = []
    for entry in diary_entries:
        consumed_foods_data = []
        for food in entry.consumed_foods:
            consumed_foods_data.append({
                'food_name': food['food_name'],
                'weight': food['weight'],
                'calories': food['calories'],
                'protein': food['protein'],
                'sugar': food['sugar'],
            })

        diary_data.append({
            'entry_id': entry.id,
            'date_consumed': entry.date_consumed.strftime('%Y-%m-%d'),
            'total_calories': entry.total_calories,
            'total_protein': entry.total_protein,
            'total_sugar': entry.total_sugar,
            'consumed_foods': consumed_foods_data,
        })

    response_data = {
        'nutrition_diary': diary_data,
    }

    return JsonResponse(response_data)

def calculate_nutrition(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Assuming you are using Django REST framework
            food_items = data.get('food_items', [])

            # Calculate nutritional values for the entered food items
            total_calories = 0
            total_protein = 0
            total_sugar = 0

            for item in food_items:
                food_name, quantity = item.split(' ')
                quantity = float(quantity)

                if food_name in food_data:
                    food_info = food_data[food_name]
                    total_calories += (food_info['calories'] * quantity) / 100
                    total_protein += (food_info['protein'] * quantity) / 100
                    total_sugar += (food_info['sugar'] * quantity) / 100
                else:
                    return JsonResponse({'error': f"Nutritional information for {food_name} not found."}, status=400)

            response_data = {
                'total_calories': round(total_calories, 2),
                'total_protein': round(total_protein, 2),
                'total_sugar': round(total_sugar, 2),
            }

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=405)