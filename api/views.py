from rest_framework.viewsets import ModelViewSet, ViewSet
from .serializers import PredioSerializer, ImovelSerializer, ImagemSerializer, UserSerializer,  EmpresaSerializer
from .models import Predio, Imovel, Imagem, UsuarioEmpresa, Empresa
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class PredioViewSet(ModelViewSet):
    serializer_class = PredioSerializer
    queryset = Predio.objects.all()
 #   authentication_classes = [JWTAuthentication]
 #   permission_classes = [IsAuthenticated]


'''
class ImovelViewSet(ModelViewSet):
    serializer_class = ImovelSerializer
    queryset = Imovel.objects.all()
   # authentication_classes = [JWTAuthentication]
   # permission_classes = [IsAuthenticated]
'''
class ImovelViewSet(ModelViewSet):
    serializer_class = ImovelSerializer
    queryset = Imovel.objects.all()
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Define a lógica para retornar os imóveis com base na autenticação do usuário.
        """
        user = self.request.user

        if user.is_authenticated:
            # Usuário autenticado
            if hasattr(user, 'empresa_relacionada') and user.empresa_relacionada.empresa:
                # Usuário tem empresa associada: retorna imóveis dessa empresa
                empresa = user.empresa_relacionada.empresa
                return Imovel.objects.filter(empresa=empresa)
            else:
                # Usuário autenticado, mas sem empresa associada
                return Imovel.objects.none()  # Nenhum imóvel será retornado
        else:
            # Usuário não autenticado: retorna todos os imóveis
            return Imovel.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

 # def get_queryset(self):
        # return Imovel.objects.filter(status='DISPONIVEL')
  
class PublicViewSet(ViewSet):


    @action(methods=['get'], detail=False)
    def imoveis(self, request, *args, **kwargs):
        
        imoveis = Imovel.objects.filter(status='DISPONIVEL')
        serializer = ImovelSerializer(imoveis, many=True, context={'request': request})
        return Response (serializer.data)

    @action(methods=['get'], detail=False)
    def contador_imoveis(self, request, *args, **kwargs):
        
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
       


class HomeViewSet(ViewSet):
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
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]


    @action(methods=['get'], detail=True)
    def imoveis(self, request, pk=None, *args, **kwargs):
        
        empresas = UsuarioEmpresa.objects.filter(user=pk).values_list('empresa', flat=True)
        imoveis = Imovel.objects.filter(empresa__in=empresas)
        serializer = ImovelSerializer(imoveis, many=True, context={'request': request})
    
        return Response (serializer.data)

    @action(methods=['get'], detail=True)
    def empresas(self, request, pk=None, *args, **kwargs):
        
        empresas_fk = UsuarioEmpresa.objects.filter(user=pk).values_list('empresa', flat=True)
        empresas = Empresa.objects.filter(pk__in=empresas_fk)
        serializer = EmpresaSerializer(empresas, many=True)
    
        return Response (serializer.data)


  