#api/views.py
import csv
import io
import json
import datetime

import requests

from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum, Count, Min, Max, ExpressionWrapper, DecimalField

from rest_framework import serializers, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view

from .models import Company, SubUser, Client
from bots.models import Bot
from .serializers import CompanyRegisterSerializer,SubUserSerializer, ClientSerializer, BotSerializer


# --- Регистрация компании ---
class RegisterView(APIView):
    def post(self, request):
        serializer = CompanyRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Компания успешно зарегистрирована!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- Логин компании или субпользователя ---
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            subuser = SubUser.objects.get(email=email)
            if check_password(password, subuser.password):
                return Response({
                    "message": "Вход выполнен",
                    "user_type": "subuser",
                    "id": subuser.id,
                    "email": subuser.email,
                    "company_id": subuser.company.id,
                }, status=status.HTTP_200_OK)
        except SubUser.DoesNotExist:
            pass

        try:
            company = Company.objects.get(email=email)
            if check_password(password, company.passwordhash):
                return Response({
                    "message": "Вход выполнен",
                    "user_type": "company",
                    "id": company.id,
                    "title": company.title,
                    "email": company.email,
                }, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            pass

        return Response({"error": "Неверные данные для входа"}, status=status.HTTP_401_UNAUTHORIZED)


# --- Выход ---
class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Выход выполнен"})


# --- Обновление информации о компании ---
class CompanyUpdateView(APIView):
    def put(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Компания не найдена"}, status=status.HTTP_404_NOT_FOUND)

        company.title = request.data.get("title", company.title)
        company.email = request.data.get("email", company.email)

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if old_password and new_password:
            if check_password(old_password, company.passwordhash):
                company.passwordhash = make_password(new_password)
            else:
                return Response({"error": "Старый пароль неверен"}, status=status.HTTP_400_BAD_REQUEST)

        company.save()
        return Response({"message": "Информация о компании обновлена!"})


# --- Работа с субпользователями ---
class SubUserListCreateView(APIView):
    def get(self, request):
        company_id = request.query_params.get('company_id')
        if not company_id:
            return Response({"error": "company_id обязателен"}, status=400)

        subusers = SubUser.objects.filter(company_id=company_id)
        serializer = SubUserSerializer(subusers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        subuser_id = request.data.get('id')
        if not subuser_id:
            return Response({"error": "id обязателен для удаления"}, status=400)

        try:
            subuser = SubUser.objects.get(id=subuser_id)
            subuser.delete()
            return Response({"success": "Пользователь удалён"}, status=204)
        except SubUser.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=404)


# --- Работа с клиентами ---
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.none()
    serializer_class = ClientSerializer

    def get_queryset(self):
        company_id = self.request.query_params.get("company_id")
        qs = Client.objects.all()

        if company_id:
            qs = qs.filter(company_id=company_id)

        return qs.annotate(
            total_amount=Sum('purchases__total_amount'),
            purchases_count=Count('purchases', distinct=True),
            total_tickets=Sum('purchases__total_tickets'),
            first_purchase=Min('purchases__purchase_date'),
            last_purchase=Max('purchases__purchase_date'),
            avg_check=ExpressionWrapper(
                Sum('purchases__total_amount') / Count('purchases', distinct=True),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )


# --- Получение ботов пользователя ---
class UserBotsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        company_id = request.query_params.get('company_id')
        if not company_id:
            return Response({"error": "company_id обязателен в запросе"}, status=400)

        bots = Bot.objects.filter(company_id=company_id, deleted=False).order_by('-creationdate')
        serializer = BotSerializer(bots, many=True)
        return Response(serializer.data)


# --- Получение username бота по токену ---
@api_view(['GET'])
def get_bot_username(request):
    token = request.GET.get('token')
    if not token:
        return Response({'error': 'Token обязателен'}, status=400)

    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        data = response.json()
        if data.get('ok'):
            return Response({'username': data['result']['username']})
        else:
            return Response({'error': 'Ошибка запроса к Telegram'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# --- Импорт клиентов из CSV ---
class ClientImportView(APIView):
    def post(self, request):

        file = request.FILES.get("file")

        company_id = request.query_params.get("company_id")
        if not company_id:
            return Response({"error": "company_id обязателен в параметрах"}, status=400)

        try:
            field_mapping_raw = request.data.get("field_mapping", "{}")
            field_mapping = json.loads(field_mapping_raw)
        except json.JSONDecodeError:
            return Response({"error": "Невалидный JSON в field_mapping"}, status=400)

        exclude_invalid_emails = request.data.get("exclude_invalid_emails", "false") == "true"
        tags = request.data.get("tags", "")

        if not file or not field_mapping.get("email"):
            return Response({"error": "CSV файл и поле email обязательны"}, status=400)

        decoded_file = file.read().decode("utf-8")
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        imported = 0
        skipped = 0

        for row in reader:
            email_value = row.get(field_mapping["email"])
            if exclude_invalid_emails:
                try:
                    validate_email(email_value)
                except ValidationError:
                    skipped += 1
                    continue

            client_data = {}
            for model_field, csv_field in field_mapping.items():
                client_data[model_field] = row.get(csv_field)

            client_data.pop("id", None)
            client_data["tags"] = tags
            client_data["creationdate"] = timezone.now()
            client_data["company_id"] = company_id

            # Сохраняем клиента
            Client.objects.create(**client_data)
            imported += 1

        return Response({"imported": imported, "skipped": skipped}, status=200)


# --- Импорт клиентов из Telegram ---
class TelegramClientDataView(APIView):
    def post(self, request):
        email = request.data.get("email")
        company_id = request.data.get("company_id")
        bot_id = request.data.get("bot_id")

        if not email or not company_id:
            return Response({"error": "email и company_id обязательны"}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Невалидный email"}, status=400)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Компания не найдена"}, status=404)

        birth_date = None
        birth_date_raw = request.data.get("birth_date")
        if birth_date_raw:
            try:
                birth_date = datetime.datetime.strptime(birth_date_raw, "%d.%m.%Y").date()
            except ValueError:
                return Response({"error": "Дата рождения должна быть в формате ДД.ММ.ГГГГ"}, status=400)

        client = Client.objects.filter(company=company, email=email).first()

        if client:
            updated = False
            for field in ["full_name", "phone", "gender", "telegram_id"]:
                value = request.data.get(field)
                if value and not getattr(client, field):
                    setattr(client, field, value)
                    updated = True

            if birth_date and not client.birth_date:
                client.birth_date = birth_date
                updated = True

            tags = set(client.tags.split(",")) if client.tags else set()
            if "telegram" not in tags:
                tags.add("telegram")
                client.tags = ",".join(tags)
                updated = True

            if bot_id and not client.bot_id:
                client.bot_id = bot_id
                updated = True

            if updated:
                client.save()

            return Response({"message": "Клиент обновлён"}, status=200)

        new_client_data = {
            "company": company,
            "email": email,
            "full_name": request.data.get("full_name"),
            "phone": request.data.get("phone"),
            "birth_date": birth_date,
            "gender": request.data.get("gender"),
            "telegram_id": request.data.get("telegram_id"),
            "tags": "telegram",
            "creationdate": timezone.now()
        }

        if bot_id:
            try:
                bot = Bot.objects.get(id=bot_id, company=company)
                new_client_data["bot"] = bot
            except Bot.DoesNotExist:
                pass

        Client.objects.create(**new_client_data)
        return Response({"message": "Клиент создан"}, status=200)