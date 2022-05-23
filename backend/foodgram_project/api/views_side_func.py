from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response

User = get_user_model()


def manage_many_to_many_model_with_user(request, *args, **kwargs):
    second_model = kwargs.get('second_model')
    second_model_name = kwargs.get('second_model_name')
    second_model_id = kwargs.get('pk', 0)
    serializer_class = kwargs.get('serializer_class')
    many_to_many_model = kwargs.get('many_to_many_model')
    user = request.user

    if not second_model.objects.filter(id=second_model_id).exists():
        text = (
            f'{second_model_name.title()}'
            f'with id={second_model_id} does not exists'
        )
        return Response(
            {'errors': text},
            status=status.HTTP_400_BAD_REQUEST,
        )

    model_obj = second_model.objects.get(id=second_model_id)

    if second_model == User and model_obj == user:
        return Response(
            {'errors': 'can not subscribe to yourself'},
            status=status.HTTP_404_NOT_FOUND,
        )

    params = {
            second_model_name: model_obj,
            'user': user,
        }

    if request.method == 'POST':
        row, created = many_to_many_model.objects.get_or_create(**params)
        if created:
            serializer = serializer_class(instance=model_obj)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'errors': f'The {second_model_name.lower()} is already add'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if many_to_many_model.objects.filter(**params).exists():
        row = many_to_many_model.objects.get(**params)
        row.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(
        {'errors': f'The {second_model_name.lower()} is not add'},
        status=status.HTTP_400_BAD_REQUEST,
    )
