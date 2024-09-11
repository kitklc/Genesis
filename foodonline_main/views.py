from django.shortcuts import render
from django.http import HttpResponse
from vendor.models import Vendor
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance

def get_or_set_current_location(request):
    if 'lat' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return lng, lat
    elif 'lat' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        request.session['lat'] = lat
        request.session['lng'] = lng
        return lng, lat
    else:
        return None



def home(request):
    if get_or_set_current_location(request) is not None:
      
        # Handle potential errors in fetching latitude and longitude
        try:
            pnt = GEOSGeometry('POINT(%s %s)' % (get_or_set_current_location(request)))
        except (TypeError, ValueError) as e:
            # Add error handling if needed, e.g., logging or default values
            pnt = None

        if pnt:
            vendors = Vendor.objects.filter(
            user_profile__location__distance_lte=(pnt, D(km=1000))
            ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
            
            for v in vendors:
                v.kms = round(v.distance.km, 1)
        else:
            # Fallback if the point couldn't be created
            vendors = Vendor.objects.none()  # Or handle as needed
    else:
        # Fallback for when lat/lng are not in request.GET
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]

    context = {
        'vendors': vendors,
    }
    return render(request, 'home.html', context)