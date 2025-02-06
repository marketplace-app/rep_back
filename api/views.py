from rest_framework.viewsets import ModelViewSet, ViewSet
from .serializers import PredioSerializer, ImovelSerializer, ImagemSerializer, UserSerializer, EmpresaSerializer, ClientSerializer
from .models import Predio, Imovel, Imagem, UsuarioEmpresa, Empresa, Client
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class PredioViewSet(ModelViewSet):
    serializer_class = PredioSerializer
    queryset = Predio.objects.all()


class ImovelViewSet(ModelViewSet):
    serializer_class = ImovelSerializer
    queryset = Imovel.objects.all()
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
     
    """Define a lógica para retornar os imóveis com base na autenticação do usuário. """
    def get_queryset(self):
        user = self.request.user
        print(user)

        if user.is_authenticated:
            if hasattr(user, 'empresa_relacionada'):
                # Usuário tem empresa associada: retorna imóveis dessa empres
                empresas = user.empresa_relacionada.all().values_list('empresa_id', flat=True)
                return Imovel.objects.filter(empresa__id__in=list(empresas)).order_by('id')
            else:
                return Imovel.objects.none()  
        else:
            return Imovel.objects.all().order_by('id')

    def get_serializer_context(self):
        """
        Adiciona o request ao contexto para gerar URLs completas no serializer.
        """
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        """
        Sobrescreve o método create para verificar autenticação antes de criar um imóvel.
        """
        if not request.user.is_authenticated:
            return Response(
                {"error": "É necessário estar autenticado para criar um imóvel."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """
        Associa o imóvel ao usuário autenticado durante a criação.
        """
        serializer.save(usuario=self.request.user)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"error": "É necessário estar autenticado para atualizar um imóvel."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        instance = self.get_object()
        if instance.usuario != request.user:
            return Response(
                {"error": "Você só pode editar imóveis que você criou."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


class EmpresaViewSet(ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Associa o imóvel ao usuário autenticado durante a criação.
        """
        if self.request.user.is_authenticated:
            serializer.save(proprietario=self.request.user)
        else:
            return Response(
                status=status.HTTP_403_FORBIDDEN)


    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"error": "É necessário estar autenticado para atualizar a empresa."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        instance = self.get_object()
        if instance.proprietario != request.user:
            return Response(
                {"error": "Você só pode editar empresa que você criou."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, args, * kwargs)

class ClientViewSet(ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all().order_by('id')
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if hasattr(request.user, 'client'):
            return Response(
                {"error": "Você já é um Cliente"},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        clientes = Client.objects.all()
        serializer = self.get_serializer(clientes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublicViewSet(ViewSet):
    @action(methods=['get'], detail=False)
    def imoveis(self, request, *args, **kwargs):
        """
        Lista imóveis com status 'DISPONIVEL' para todos os usuários.
        """
        imoveis = Imovel.objects.filter(status='DISPONIVEL')
        serializer = ImovelSerializer(imoveis, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def contador_imoveis(self, request, *args, **kwargs):
        """
        Conta imóveis por status.
        """
        imoveis = Imovel.objects.all()
        alugados = imoveis.filter(status='DISPONIVEL').count()
        reservados = imoveis.filter(status='RESERVADO').count()
        vendidos = imoveis.filter(status='VENDIDO').count()

        data = {
            'alugados': alugados,
            'reservados': reservados,
            'vendidos': vendidos,
        }

        return Response(data, status=200)


class HomeViewSet(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Contagem de imóveis por status.
        """
        imoveis = Imovel.objects.all()
        alugados = imoveis.filter(status='DISPONIVEL').count()
        reservados = imoveis.filter(status='RESERVADO').count()
        vendidos = imoveis.filter(status='VENDIDO').count()

        data = {
            'alugados': alugados,
            'reservados': reservados,
            'vendidos': vendidos,
        }

        return Response(data, status=200)


class ImagemViewSet(ModelViewSet):
    serializer_class = ImagemSerializer
    queryset = Imagem.objects.all()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(methods=['get'], detail=True)
    def imoveis(self, request, pk=None, *args, **kwargs):
        """
        Lista imóveis associados às empresas do usuário.
        """
        empresas = UsuarioEmpresa.objects.filter(user=pk).values_list('empresa', flat=True)
        imoveis = Imovel.objects.filter(empresa__in=empresas)
        serializer = ImovelSerializer(imoveis, many=True, context={'request': request})

        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def empresas(self, request, pk=None, *args, **kwargs):
        """
        Lista empresas associadas ao usuário.
        """
        empresas_fk = UsuarioEmpresa.objects.filter(user=pk).values_list('empresa', flat=True)
        empresas = Empresa.objects.filter(pk__in=empresas_fk)
        serializer = EmpresaSerializer(empresas, many=True)

        return Response(serializer.data)
