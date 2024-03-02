from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_http_methods
from .models import Rating

require_http_methods('POST')
def rate_movie_view(request):
    if not request.htmx:
        return HttpResponse("Not Allowed", status=404)
    object_id = request.POST.get('object_id')
    rating_value = request.POST.get('rating_value')
    if object_id is None or rating_value is None:
         response = HttpResponse("skipping", status=200)
         response['HX-Trigger'] = 'did-skip-anime'
         return response
    user = request.user
    message = "You must <a href='/accounts/login/'>login</a> to Rate this."
    if user.is_authenticated:
        ctype = ContentType.objects.get(app_label='anime', model='anime')
        rating_obj = Rating.objects.create(content_type=ctype, object_id=object_id, value=rating_value, user=user)
        if rating_obj.content_object is not None:
           message = "<span class='bg-danger text-light py-1 px-3 rounded'>Rating Saved Successfully!</span>"

    return HttpResponse(message, status=200)