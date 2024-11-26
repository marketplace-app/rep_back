from rest_framework.viewsets import ModelViewSet
from .serializers import PredioSerializer, ImovelSerializer, ImagemSerializer, UserSerializer
from .models import Predio, Imovel, Imagem
from django.contrib.auth.models import User


class PredioViewSet(ModelViewSet):
    serializer_class = PredioSerializer
    queryset = Predio.objects.all()


class ImovelViewSet(ModelViewSet):
    serializer_class = ImovelSerializer
    queryset = Imovel.objects.all()



class ImagemViewSet(ModelViewSet):
    serializer_class = ImagemSerializer
    queryset = Imagem.objects.all()

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

