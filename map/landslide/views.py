from django.shortcuts import render
from landslide.models import Cracks
from django.http import HttpResponse, HttpResponseRedirect
import csv, json
from geojson import Feature, FeatureCollection, Point
from django.core import serializers
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
from io import BytesIO
import subprocess
from django.shortcuts import redirect

model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)


def home(request):
    print( serializers.serialize('json',Cracks.objects.all()))
    return render(request, "home.html")

def mapping(request):
    return render(request, "map.html")

def cracks(request):
    features = []
    for x in Cracks.objects.all():
        long, lat, date = x.long.replace(',', '.'), x.lat.replace(',', '.'), x.date
        features.append(
            Feature(
                geometry = Point((float(long), float(lat))),
                properties = {
                    'date': str(date),
                }
            )
        )

        #data = x.long, x.lat, str(x.date)])
    collection = FeatureCollection(features)
    return HttpResponse(str(collection))

def historical(request):
    reader = csv.reader(open('/home/manwar/map/landslide/static/historical.csv', 'r'), delimiter=',')
    features = []
    print(reader)
    for landslides, longitude, latitude, date in reader:
        latitude, longitude = map(float, (latitude, longitude))
        features.append(
            Feature(
                geometry = Point((longitude, latitude)),
                properties = {
                    'landslides': str(landslides),
                    'date': str(date),
                }
            )
        )

    collection = FeatureCollection(features)
    return HttpResponse(str(collection))

def get_data(request):
    user_long, user_lat = float(request.GET["long"]), float(request.GET["lat"])
    csv = open("worldcities.csv", "r").read().split("\n")
    diff = 2
    human_output = []
    hist_csv = open("/home/manwar/map/landslide/static/historical.csv", "r").read().split("\n")
    hist_diff = 2
    hist_output = []
    for i in csv[1:-1]:
        x = i.split(",")
        city = x[0]
        lat = float(x[1])
        long = float(x[2])
        population = x[3]
        temp_diff =  abs(user_long - long) + abs(user_lat - lat)
        if temp_diff < diff:
            diff = temp_diff
            output = [x[0], x[-1]]
    for i in hist_csv[1:-1]:
        x = i.split(",")
        landslides = x[0]
        long = float(x[1])
        lat = float(x[2])
        temp_diff =  abs(user_long - long) + abs(user_lat - lat)
        if temp_diff < hist_diff:
            hist_diff = temp_diff
            hist_output = x
    cracks = list(Cracks.objects.raw('SELECT * FROM landslide_cracks WHERE abs(%s - long) + abs(%s - lat) < 1', [user_long, user_lat]))
    out = json.dumps({"human": output, "historical": hist_output, "cracks": len(cracks)})
    return HttpResponse(str(out))

def upload_crack(request):
    if request.method == "POST":
        file = request.FILES['image']
        image = Image.open(BytesIO(file.read())).convert('RGB')
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)

        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        data[0] = normalized_image_array

        prediction = model.predict(data)[0]
        if prediction[0] > prediction[1] or abs(prediction[0] - prediction[1]) < .5:
            try:
                print("found image")
                if request.GET['lat'] != '':
                    print(request.GET['lat'])
                    Cracks.objects.create(lat=request.GET['lat'], long=request.GET['long'])
                    subprocess.check_call("sudo apachectl restart".split())
                return redirect('https://mysterious588.tech')
            except:
                pass
    try:
        long = request.GET["long"]
        lat = request.GET["lat"]
        context = {"long": long, "lat": lat}
    except:
        context = {}
    return render(request, "upload.html", context)
