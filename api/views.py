from rest_framework.viewsets import ModelViewSet
from .serializers import PredioSerializer, ImovelSerializer, ImagemSerializer, UserSerializer
from .models import Predio, Imovel, Imagem
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response



class PredioViewSet(ModelViewSet):
    serializer_class = PredioSerializer
    queryset = Predio.objects.all()
 #   authentication_classes = [JWTAuthentication]
 #   permission_classes = [IsAuthenticated]



class ImovelViewSet(ModelViewSet):
    serializer_class = ImovelSerializer
    queryset = Imovel.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
'''
class ImovelViewSet(ModelViewSet):
    serializer_class = ImovelSerializer
    queryset = Imovel.objects.all()
   # authentication_classes = [JWTAuthentication]
   # permission_classes = [IsAuthenticated]
'''


class HomeViewSet(ModelViewSet):
    # Usamos ModelViewSet mas não vamos criar nem atualizar objetos diretamente
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):

        # Realiza as contagens de imóveis com os status solicitados
        imoveis = Imovel.objects.all()
        alugados = imoveis.filter(status='DISPONIVEL').count()
        reservados = imoveis.filter(status='RESERVADO').count()
        vendidos = imoveis.filter(status='VENDIDO').count()

        # Monta a resposta com os dados agregados
        data = {
            'alugados': alugados,
            'reservados': reservados,
            'vendidos': vendidos,
        }

        return Response(data, status=200)



class ImagemViewSet(ModelViewSet):
    serializer_class = ImagemSerializer
    queryset = Imagem.objects.all()
 #   authentication_classes = [JWTAuthentication]
 #   permission_classes = [IsAuthenticated]



class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


  