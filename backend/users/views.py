from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser, Subscription
from .serializers import CustomUserCreateSerializer, SetAvatarSerializer, SetPasswordSerializer
from .serializers import (
    CustomUserSerializer
)
from .serializers import UserWithRecipesSerializer


class CustomUserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        return CustomUserSerializer


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


User = get_user_model()


class SubscriptionListView(generics.ListAPIView):
    serializer_class = UserWithRecipesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(subscribers__subscriber=self.request.user)



class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        author = get_object_or_404(User, pk=id)
        if author == request.user:
            return Response({'error': 'Нельзя подписаться на себя.'}, status=status.HTTP_400_BAD_REQUEST)
        subscription, created = Subscription.objects.get_or_create(subscriber=request.user, author=author)
        if not created:
            return Response({'error': 'Вы уже подписаны.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserWithRecipesSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, pk=id)
        subscription = Subscription.objects.filter(subscriber=request.user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Вы не подписаны на данного пользователя.'}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = SetAvatarSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.avatar = serializer.validated_data['avatar']
            user.save()
            return Response({"avatar": user.avatar.url if user.avatar else None}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({"current_password": ["Неверный текущий пароль."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
