import json

from django.http import JsonResponse
from django.shortcuts import render

from drone.utils import calculate_paths


# Create your views here.
def index(request):
    return render(request, 'drone/index.html')


def map_view(request):
    if request.method == 'POST':
        coordinates = json.loads(request.POST.get('coordinates', '[]'))
        mst, drone_path = calculate_paths(coordinates)
        return JsonResponse({'mst': mst, 'drone_path': drone_path})
    return render(request, 'drone/mapper.html')
