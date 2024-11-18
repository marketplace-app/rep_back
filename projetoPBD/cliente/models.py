from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=15, blank=True, null=True)  # Optional
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)  # Conta ativa por padrão

    def __str__(self):
        return self.nome
