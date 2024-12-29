import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from drone.utils import  calculate_enclosed_region


# Create your views here.
def index(request):
    return render(request, 'drone/index.html')


DATA = {}




@csrf_exempt
def disease(request):
    if request.method == 'POST':
        DATA = {'mst': [([16.481738364275817, 80.50837576389314], [16.481172523975527, 80.50843477249147]),
                        ([16.481738364275817, 80.50837576389314], [16.482813456291403, 80.50785541534425])],
                'drone_path': [[(16.481842086691287, 80.50937037017732), (16.481276246390998, 80.50942937877565)],
                               [(16.481302706517994, 80.50747565150124), (16.48237779853358, 80.50695530295235)]]}

        # Log the data to the console
        print(DATA)

        # Return the data as a JSON response
        return JsonResponse(DATA)

    # Render the HTML page for non-POST requests
    return render(request, 'drone/mapped.html')


def enclosed(request):
    if request.method == 'POST':
        # Parse the coordinates sent from the frontend
        coordinates = json.loads(request.POST.get('coordinates', '[]'))

        # Ensure coordinates are valid
        if not coordinates or len(coordinates) < 3:
            return JsonResponse({'error': 'At least 3 points are required to form a region'}, status=400)

        # Calculate the enclosed region (convex hull)
        enclosed_region = calculate_enclosed_region(coordinates)

        # Prepare the response data
        DATA = {'enclosed_region': enclosed_region}
        print(DATA)  # Debugging
        return JsonResponse(DATA)

    return render(request, 'drone/enclosed.html')
