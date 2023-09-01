from django.shortcuts import render
from django.http import JsonResponse
from .utils import calculate_akg_recommendation
from django.views.decorators.csrf import csrf_exempt
import json, pandas as pd

@csrf_exempt
def calculate_recommendation(request):
    if request.method == 'POST':
        try:
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

            response_data = {
                'recommended_foods': recommended_food_list,
                'total_energy_recommended': round(total_energy_recommended, 2)
            }

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
