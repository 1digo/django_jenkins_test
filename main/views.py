from django.contrib.auth.models import User
from django.core.cache import cache
from django.http.response import JsonResponse
from django.http.response import HttpResponseNotFound
from django.http.response import HttpResponse
from django.views.generic.base import View
from django.conf import settings

class UserApi(View):
   def post(self, request, *args, **kwargs):
       """
       Создает пользователя
       """
       user = User.objects.create_user(
           username=request.POST.get('username'),
           email=request.POST.get('email'),
           password=request.POST.get('password')
       )
       return {
           'id': user.id,
           'username': user.username,
           'email': user.email,
       }

   def get(self, request, *args, **kwargs):
       """
       Возвращает список пользователей
       """
       return {
           'users': [{
               'id': user.id,
               'username': user.username,
               'email': user.email,
           } for user in User.objects.all().order_by("id")]
       }

   def dispatch(self, request, *args, **kwargs):
       result = super(UserApi, self).dispatch(request, *args, **kwargs)
       return JsonResponse(result)


class TrackerView(View):
   def post(self, request, *args, **kwargs):
       """
       Фиксирует пользователя как активного на settings.TRACKER_CACHE_TIMEOUT секунд
       """
       if request.user:
           cache.set("tracker_{}".format(request.user.pk), "active", settings.TRACKER_CACHE_TIMEOUT)
       return HttpResponse()

   def get(self, request, *args, **kwargs):
       """
       Возвращает 200, если пользователь активный или 404 в обратном случае
       """
       user_id = request.GET['id']
       value = cache.get("tracker_{}".format(user_id))
       if not value:
           return HttpResponseNotFound()
       return HttpResponse()
