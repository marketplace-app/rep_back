from django.utils import timezone
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet, ViewSet
from .serializers import PredioSerializer, ImovelSerializer, ImagemSerializer, UserSerializer, EmpresaSerializer, ClientSerializer, ContratoSerializer, ParcelaSerializer, PagamentoParcela 
from .models import Predio, Imovel, Imagem, UsuarioEmpresa, Empresa, Client, Contrato, Parcela
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
                empresas = user.empresa_relacionada.all().values_list('empresa_id', flat=True)
                return Imovel.objects.filter(empresa__id__in=list(empresas)).order_by('id')
            else:
                return Imovel.objects.none()  
        else:
            return Imovel.objects.all().order_by('-id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
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
       
    """ Associa o imóvel ao usuário autenticado durante a criação."""
    def perform_create(self, serializer):
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"error": "Você só pode editar cliente que você criou."},
                status= status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
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
  
    """Lista imóveis associados às empresas do usuário."""
    @action(methods=['get'], detail=True)
    def imoveis(self, request, pk=None, *args, **kwargs):
        empresas = UsuarioEmpresa.objects.filter(user=pk).values_list('empresa', flat=True)
        imoveis = Imovel.objects.filter(empresa__in=empresas)
        serializer = ImovelSerializer(imoveis, many=True, context={'request': request})

        return Response(serializer.data)
 
    """ Lista empresas associadas ao usuário."""
        
    @action(methods=['get'], detail=True) 
    def empresas(self, request, pk=None, *args, **kwargs):
       
        empresas_fk = UsuarioEmpresa.objects.filter(user=pk).values_list('empresa', flat=True)
        empresas = Empresa.objects.filter(pk__in=empresas_fk)
        serializer = EmpresaSerializer(empresas, many=True)

        return Response(serializer.data)

class ContratoViewSet(ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        imovel = serializer.validated_data.get('imovel')
        
        if imovel.status != 'DISPONIVEL':
            return Response(
                {"error": "Este imóvel não está disponível para contratação."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contrato = serializer.save() # AQUI chama o create() do serializer
        return Response(self.get_serializer(contrato).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def parcelas(self, request, pk=None):
        contrato = self.get_object()
        parcelas = contrato.parcelas.all()
        serializer = ParcelaSerializer(parcelas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path=r'parcelas/(?P<parcela_id>\d+)')
    def pagar_parcela(self, request, pk=None, parcela_id=None):
        try:
            parcela = Parcela.objects.get(id=parcela_id, contrato_id=pk)
        except Parcela.DoesNotExist:
            return Response({"error": "Parcela não encontrada"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PagamentoParcela(data=request.data, context={'parcela': parcela})
        serializer.is_valid(raise_exception=True)
        valor_pago = serializer.validated_data['valor_pago']
        parcela.valor_pago = valor_pago  # Define o valor exato pago
        parcela.data_pagamento = timezone.now().date()  #
        
        if parcela.valor_pago >= parcela.valor:
            parcela.status = 'Pago'
        parcela.save()
        return Response(ParcelaSerializer(parcela).data)