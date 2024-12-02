
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import PredioViewSet, ImovelViewSet, ImagemViewSet, UserViewSet, HomeViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=False)

router.register('predios', PredioViewSet, basename='predios')
router.register('imoveis', ImovelViewSet, basename='imoveis')
router.register('imagens', ImagemViewSet, basename='imagens')
router.register('usuarios', UserViewSet, basename='usuarios')
router.register('home', HomeViewSet, basename='home')




urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls))
]
