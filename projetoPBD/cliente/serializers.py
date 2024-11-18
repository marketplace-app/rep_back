from rest_framework import serializers
from cliente.models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "nome", "email", "telefone", "data_cadastro", "ativo"]
