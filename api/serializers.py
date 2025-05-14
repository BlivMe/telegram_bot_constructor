from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from .models import Company, SubUser, Client, Event, TicketType, Purchase, PurchaseItem
from bots.models import Bot


# Базовый сериализатор компании
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


# Сериализатор регистрации компании
class CompanyRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Company
        fields = ['title', 'email', 'password']

    def create(self, validated_data):
        validated_data['passwordhash'] = make_password(validated_data.pop('password'))
        validated_data['creationdate'] = timezone.now()
        return Company.objects.create(**validated_data)


# Сериализатор субпользователя компании
class SubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubUser
        fields = '__all__'

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


# Сериализатор покупателя
class ClientSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_tickets = serializers.IntegerField(read_only=True)
    purchases_count = serializers.IntegerField(read_only=True)
    first_purchase = serializers.DateTimeField(read_only=True)
    last_purchase = serializers.DateTimeField(read_only=True)
    avg_check = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Client
        fields = [
            'id', 'company', 'email', 'phone', 'full_name', 'birth_date', 'gender',
            'tags', 'creationdate',
            'total_amount', 'total_tickets', 'purchases_count',
            'avg_check', 'first_purchase', 'last_purchase', 'telegram_id'
        ]


# Сериализатор Telegram-бота
class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ['id', 'name', 'creationdate', 'modificationdate', 'status', 'token']


# Сериализатор событий
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


# Сериализатор типов билетов
class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = '__all__'


# Сериализатор купленного товара
class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = '__all__'


# Сериализатор заказа
class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = '__all__'