from django.db import models
from django.contrib.auth.models import User


class Empresa(models.Model):
    nome = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    proprietario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='criador_id',
        related_name='empresas_criadas'  # Identifica quem criou a empresa
    )

    class Meta:
        db_table = 'empresa'
        verbose_name = 'empresa'
        verbose_name_plural = 'empresas'

    def __str__(self):  
        return self.nome  
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.nome:
            raise ValidationError("O campo 'nome' é obrigatório.")


class UsuarioEmpresa(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='empresa_relacionada')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='usuarios')

    class Meta:
        db_table = 'usuario_empresa'
        verbose_name = 'Usuário e Empresa'
        verbose_name_plural = 'Usuários e Empresas'

    def __str__(self):  # Correção do método __str__
        return f"{self.user.username} - {self.empresa.nome}"  



class Predio(models.Model):
   
    descricao = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)

    class Meta:
        db_table = 'predio'
        verbose_name = 'prédio'
        verbose_name_plural = 'prédios'

    def __str__(self):
        return self.descricao


class Imovel(models.Model):
    TIPOS_IMOVEL = [
        ('CASA', 'Casa'),
        ('APARTAMENTO', 'Apartamento'),
    ]
    STATUS_CHOICES = [
        ('DISPONIVEL', 'Disponível'),
        ('RESERVADO', 'Reservado'),
        ('VENDIDO', 'Vendido'),
        ('ALUGADO', 'Alugado'),
    ]
    
    
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)  
    tipo = models.CharField(max_length=15, choices=TIPOS_IMOVEL)
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default= 'DISPONIVEL'
    )
    
    predio = models.ForeignKey(
        Predio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='predio_id'
    )

    endereco = models.CharField(max_length=255)

   # Apenas como exemplo.
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column= 'user_id'
    )
    empresa = models.ForeignKey(  
        Empresa,
        on_delete=models.SET_NULL,
        null=True,  
        blank=True,
        db_column= 'empresa_id'
    )


    class Meta:
        db_table = 'imovel'
        verbose_name = 'imóvel'
        verbose_name_plural = 'imóveis'

    def __str__(self):
        return f"{self.tipo}: {self.descricao}"
    
    def _str_(self):
        return self.nome

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.tipo == 'APARTAMENTO' and not self.predio:
            raise ValidationError("O campo 'predio' é obrigatório para imóveis do tipo 'APARTAMENTO'.")



    
class Imagem(models.Model):
    imovel = models.ForeignKey(
        Imovel,
        on_delete=models.CASCADE,
        related_name='imagens'
    )
    imagem = models.ImageField(upload_to='imoveis/', null=True, blank=True)

    class Meta:
        db_table = 'imagem'
        verbose_name = 'imagem'
        verbose_name_plural = 'Imagens'

    def __str__(self):
        return self.imagem.name if self.imagem else "Sem imagem!"