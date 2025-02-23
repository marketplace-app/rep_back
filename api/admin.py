from django.contrib import admin
from .models import Predio, Imovel, Imagem, Empresa, UsuarioEmpresa

admin.site.register(Empresa)
admin.site.register(UsuarioEmpresa)

@admin.register(Predio)
class PredioAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'endereco')
    search_fields = ('descricao',)


@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'tipo', 'predio', 'endereco')
    list_filter = ('tipo', 'empresa','status')   
    search_fields = ('descricao', 'endereco')


@admin.register(Imagem)
class ImagemAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'imagem') 
    search_fields = ('imagem',)  