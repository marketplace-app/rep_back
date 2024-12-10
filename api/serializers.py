from rest_framework import serializers
from .models import Imovel, Predio, Imagem
from django.contrib.auth.models import User

# Serializer para Predio
class PredioSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='descricao')  

    class Meta:
        model = Predio
        fields = ['nome', 'endereco']  

class ImovelSerializer(serializers.ModelSerializer):
    predio = PredioSerializer()
    imagens = serializers.SerializerMethodField()
    proprietario = serializers.SerializerMethodField()
    def get_imagens(self, instance):
        # Verifica se o imóvel tem imagens associadas antes de tentar acessar a URL
        if instance.imagens.exists():
            return [self.context['request'].build_absolute_uri(img.imagem.url) for img in instance.imagens.all()]
        return []  # Retorna uma lista vazia se não houver imagens

    class Meta:
        model = Imovel
        fields = ['id', 'descricao', 'valor', 'tipo', 'predio', 'endereco', 'imagens', 'status', 'proprietario']

    def get_proprietario(self, instance):
        if instance.usuario:
            return instance.usuario.get_full_name()
        return ""

class ImagemSerializer(serializers.ModelSerializer):

    imovel = ImovelSerializer()

    class Meta:
        model = Imagem
        fields = ["imovel", 'url']  # listar no endpoint




class UserSerializer(serializers.ModelSerializer):
     
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']