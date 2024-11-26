from django.db import models

# Create your models here.
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
    
    
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)  
    tipo = models.CharField(max_length=15, choices=TIPOS_IMOVEL)
    predio = models.ForeignKey(
        Predio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='predio_id'
    )
    endereco = models.CharField(max_length=255)

    class Meta:
        db_table = 'imovel'
        verbose_name = 'imóvel'
        verbose_name_plural = 'imóveis'

    def __str__(self):
        return f"{self.tipo}: {self.descricao}"

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
    url = models.URLField() 

    class Meta:
        db_table = 'imagem'
        verbose_name = 'imagem'
        verbose_name_plural = 'Imagens'

    def __str__(self):
        return self.url