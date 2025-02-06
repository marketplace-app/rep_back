from rest_framework import serializers
from .models import Imovel, Predio, Imagem, Empresa, Client
from django.contrib.auth.models import User

# Serializer para Predio
class PredioSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='descricao')  

    class Meta:
        model = Predio
        fields = ['nome', 'endereco']  

# Serializer para Empresa (apenas com id e nome)
class EmpresaSimplificadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nome']  

# Serializer para Imovel
from rest_framework import serializers
from .models import Imovel, Predio, Imagem, Empresa
from django.contrib.auth.models import User


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'  # Todos os campos do modelo Empresa são expostos
# Serializer para Predio
class PredioSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='descricao')  

    class Meta:
        model = Predio
        fields = ['nome', 'endereco']  


# Serializer para Empresa (apenas com id e nome)
class EmpresaSimplificadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nome']  

class ClientSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='user.username', read_only=True)  # Nome vem do User

    class Meta:
        model = Client
        fields = ['nome', 'cpf']  
    
    def validate_cpf(self, value):
        """
        Valida se o CPF já existe na base de dados e exibe uma mensagem personalizada.
        """
        if Client.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("Este CPF já está em uso por outro cliente.")
        return value


# Serializer para Imovel
class ImovelSerializer(serializers.ModelSerializer):
    predio = serializers.PrimaryKeyRelatedField(queryset=Predio.objects.all(), required=False) 
    empresa = serializers.PrimaryKeyRelatedField(queryset=Empresa.objects.all(), write_only=True)  
    empresa_detalhes = EmpresaSimplificadaSerializer(source='empresa', read_only=True)  
    predio_detalhes = PredioSerializer(source='predio', read_only=True)  
    imagens = serializers.SerializerMethodField()  
    proprietario = serializers.SerializerMethodField()  

    def get_imagens(self, instance):
        """Gera uma lista de URLs completas das imagens associadas ao imóvel."""
        if isinstance(instance, Imovel):
            if instance.imagens.exists():
                return [
                    self.context['request'].build_absolute_uri(img.imagem.url)
                    for img in instance.imagens.all()
                ]
        return []  

    def get_proprietario(self, instance):
        """Retorna o nome do proprietário do imóvel."""
        if isinstance(instance, Imovel):
            if instance.usuario:
                return instance.usuario.get_full_name()
        return ""

    def validate(self, data):
        """
        Validações personalizadas para o campo 'predio' quando o tipo do imóvel for 'APARTAMENTO'.
        """
        tipo = data.get('tipo', None)
        predio = data.get('predio', None)

        if tipo == 'APARTAMENTO' and not predio:
            raise serializers.ValidationError({
                'predio': "O campo 'predio' é obrigatório para imóveis do tipo 'APARTAMENTO'."
            })
        return data

    class Meta:
        model = Imovel
        fields = [
            'id', 'descricao', 'valor', 'tipo', 'predio', 'predio_detalhes', 'endereco', 
            'imagens', 'status', 'proprietario', 'empresa', 'empresa_detalhes'
        ]


# Serializer para Imagem
class ImagemSerializer(serializers.ModelSerializer):
    imovel = ImovelSerializer()

    class Meta:
        model = Imagem
        fields = ["imovel", 'url']  # listar no endpoint

# Serializer para User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

# Serializer para Empresa (completo)
class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = "__all__"
