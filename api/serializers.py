from datetime import timedelta
from rest_framework import serializers
from .models import Imovel, Predio, Imagem, Empresa, Client, Contrato, Parcela
from django.contrib.auth.models import User
from django.utils import timezone
from dateutil.relativedelta import relativedelta

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

from rest_framework import serializers
from .models import Imovel, Predio, Imagem, Empresa, Client

from django.contrib.auth.models import User


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'  
# Serializer para Predio
class PredioSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='descricao')  

    class Meta:
        model = Predio
        fields = ['nome', 'endereco']  

class EmpresaSimplificadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['id', 'nome']  

class ClientSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(write_only=True)  
    nome_display = serializers.CharField(source='user.first_name', read_only=True)  

    class Meta:
        model = Client
        fields = ['nome_display', 'nome', 'cpf']  # Define os campos na resposta
    def validate_cpf(self, value):
        if Client.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("Este CPF já está em uso por outro cliente.")
        return value
    
    def create(self, validated_data):
        nome = validated_data.pop('nome', '')  
        user = validated_data.get('user')
        user.first_name = nome  
        user.save() 
        return super().create(validated_data) 

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            'nome': representation['nome_display'],
            'cpf': representation['cpf']
        }

# Serializer para Imovel
class ImovelSerializer(serializers.ModelSerializer):
    predio = serializers.PrimaryKeyRelatedField(queryset=Predio.objects.all(), required=False) 
    empresa = serializers.PrimaryKeyRelatedField(queryset=Empresa.objects.all(), write_only=True)  
    empresa_detalhes = EmpresaSimplificadaSerializer(source='empresa', read_only=True)  
    predio_detalhes = PredioSerializer(source='predio', read_only=True)  
    imagens = serializers.SerializerMethodField()  
    proprietario = serializers.SerializerMethodField()  

    """Gera uma lista de URLs completas das imagens associadas ao imóvel."""
    def get_imagens(self, instance):
        
        if isinstance(instance, Imovel):
            if instance.imagens.exists():
                return [
                    self.context['request'].build_absolute_uri(img.imagem.url)
                    for img in instance.imagens.all()
                ]
        return []  
    """Retorna o nome do proprietário do imóvel."""
    def get_proprietario(self, instance):
        
        if isinstance(instance, Imovel):
            if instance.usuario:
                return instance.usuario.get_full_name()
        return ""
    
    """Validações personalizadas para o campo 'predio' quando o tipo do imóvel for 'APARTAMENTO'. """  
    def validate(self, data):
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
        
    """Validações personalizadas para o campo 'predio' quando o tipo do imóvel for 'APARTAMENTO'."""
    def validate(self, data):

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = "__all__"

class PagamentoParcela(serializers.Serializer):
    valor_pago = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        parcela = self.context.get('parcela')
        
        # Verificar se a parcela já está paga
        if parcela.status == 'Pago':
            raise serializers.ValidationError(
                "Esta parcela já foi paga."
            )
        # Verificar se o valor pago é maior que o valor da parcela
        if data['valor_pago'] > (parcela.valor - parcela.valor_pago):
            raise serializers.ValidationError(
                "Valor pago não pode ser maior que o valor restante da parcela."
            )
        # Verificar se existem parcelas anteriores em aberto
        parcelas_anteriores = Parcela.objects.filter(
            contrato=parcela.contrato,
            data_vencimento__lt=parcela.data_vencimento,
            status='Aberto'
        ).exists()

        if parcelas_anteriores:
            raise serializers.ValidationError(
                "Existem parcelas anteriores em aberto. Por favor, pague-as primeiro."
            )
        return data

class ParcelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcela
        fields = '__all__'
        read_only_fields = ['data_pagamento', 'valor_pago']

class ContratoSerializer(serializers.ModelSerializer):
    parcelas = ParcelaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Contrato
        fields = [
            'id', 'cliente', 'imovel', 'data_inicio', 'data_fim',
            'valor_total', 'quantidade_parcelas', 'data_primeira_parcela',
            'parcelas'
        ]
    
    def validate(self, data):
        # Validação de datas
        if data['data_inicio'] > data['data_fim']:
            raise serializers.ValidationError(
                "A data de início não pode ser maior que a data de fim do contrato."
            )
        
        if data['data_primeira_parcela'] < data['data_inicio']:
            raise serializers.ValidationError(
                "A data da primeira parcela não pode ser anterior à data de início do contrato."
            )

        # Validação do cliente não ser proprietário
        imovel = data.get('imovel')
        cliente = data.get('cliente')
        
        if imovel.usuario == cliente.user:
            raise serializers.ValidationError(
                "O cliente não pode ser o proprietário do imóvel."
            )
        
        # Validação da quantidade de parcelas
        if data['quantidade_parcelas'] < 1 or data['quantidade_parcelas'] > 60:
            raise serializers.ValidationError(
                "A quantidade de parcelas deve estar entre 1 e 60."
            )

        return data

    def create(self, validated_data):
        contrato = Contrato.objects.create(**validated_data)
        valor_parcela = contrato.valor_total / contrato.quantidade_parcelas
        data_parcela = contrato.data_primeira_parcela
        for _ in range(contrato.quantidade_parcelas):
            Parcela.objects.create(
                contrato=contrato,
                data_vencimento=data_parcela,
                valor=valor_parcela
            )
            # Adiciona 30 dias para a próxima parcela
            data_parcela = data_parcela + timedelta(days=30)

        # Atualizar status do imóvel
        imovel = contrato.imovel
        imovel.status = 'ALUGADO'
        imovel.save()

        return contrato