from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    # Call the default exception handler to get the standard error response
    response = exception_handler(exc, context)

    if response is not None:
        # If the error is an authentication error (e.g., JWT issues), modify the response.
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            response.data = {
                'detail': 'Usuário não autenticado.'
            }

    return response
