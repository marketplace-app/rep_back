from rest_framework.decorators import api_view
from rest_framework.response import Response
from cliente.serializers import ClienteSerializer
from cliente.models import Cliente

#CRUD (Create, Read, Update, Delete). 

@api_view(["GET"])
def apiOverview(request):
    api_urls = {
        "List": "/cliente-list/",
        "Detail View": "cliente-detail/<str:pk>/",
        "Create": "/cliente-create/",
        "Update": "/cliente-update/<str:pk>",
        "Delete": "/cliente-delete/<str:pk>/",

    }
    return Response(api_urls)


@api_view(["GET"])
def clienteList(request):
    clientes = Cliente.objects.all()
    serializer = ClienteSerializer(clientes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def clienteDetail(request, pk):
    clientes = Cliente.objects.get(id=pk)
    serializer = ClienteSerializer(clientes, many=False)
    return Response(serializer.data)

@api_view(["POST"])
def clienteCreate(request):
    serializer = ClienteSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(["PATCH"])
def clienteUpdate(request, pk):
    cliente= Cliente.objects.get(id=pk)
    serializer = ClienteSerializer(instance=cliente, data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(["DELETE"])
def clienteDelete(request, pk):
    cliente = Cliente.objects.get(id=pk)
    cliente.delete()

    return Response("item sucessfully deleted!")