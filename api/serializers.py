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

    class Meta:
        model = Imovel
        fields = ['descricao', 'valor', 'tipo', 'predio', 'endereco', 'imagens']  # listar no endpoint


    def get_imagens(self, instance):
        queryset = Imagem.objects.filter(imovel=instance)
        return queryset.values_list("url", flat=True)



class ImagemSerializer(serializers.ModelSerializer):

    imovel = ImovelSerializer()

    class Meta:
        model = Imagem
        fields = ["imovel", 'url']  # listar no endpoint


class UserSerializer(serializers.ModelSerializer):
     
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']