from django.http import HttpResponse

# Create your views here.
def rate_movie_view(request):
    if not request.htmx:
        return HttpResponse("Not Allowed", status=404)
    object_id = request.POST.get('object_id')
    rating_value = request.POST.get('')
    rating_value = request.POST.get('')
    user = request.user
    message = "You must <a href='/accounts/login/'>login</a> to Rate this."
    if user.is_authenticated:
        pass