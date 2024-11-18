from django.urls import path
from .views import site
from cliente import views

app_name= "cliente"
from django.views.generic import TemplateView

urlpatterns = [

    path("api/", views.apiOverview, name="api-overview"), # Lista de Rotas que passa pra o front-end
    path("api/clientelist/", views.clienteList, name="api-list"), #consultar essas Rotas disponível
    path("api/clientedetail/<str:pk>/", views.clienteDetail, name="api-detail"), #informacões apenas de um cliente de acordo com o id que passar.
    path("api/clientecreate/", views.clienteCreate, name="api-create"), #cadastrar um cliente, vai ser um post
    path("api/clienteupdate/<str:pk>/", views.clienteUpdate, name="api-update"), # Atualizar , passa um id tbm
    path("api/clientedelete/<str:pk>/", views.clienteDelete, name="api-delete"), # Apagar e retornar uma mensagem pra o  usuário






]
