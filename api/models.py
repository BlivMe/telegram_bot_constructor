from django.db import models


# Основная модель компании
class Company(models.Model):
    class Meta:
        db_table = 'company'

    title = models.CharField(max_length=255)
    creationdate = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approvedate = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(unique=True)
    passwordhash = models.CharField(max_length=255)
    gmtoffset = models.IntegerField(default=0)

    def __str__(self):
        return self.title


# Субпользователь компании
class SubUser(models.Model):
    class Meta:
        db_table = 'subusers'

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    creationdate = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='subusers')

    def __str__(self):
        return self.email


# Покупатель
class Client(models.Model):
    class Meta:
        db_table = 'client'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='clients')
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    tags = models.CharField(max_length=500, blank=True, null=True)
    creationdate = models.DateTimeField(auto_now_add=True)
    bot = models.ForeignKey('bots.Bot', null=True, blank=True, on_delete=models.SET_NULL, related_name='clients')

    def __str__(self):
        return self.email


# Модель события
class Event(models.Model):
    class Meta:
        db_table = 'event'

    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    city = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


# Тип билета
class TicketType(models.Model):
    class Meta:
        db_table = 'ticket_type'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.price}₽)"


# Заказ
class Purchase(models.Model):
    class Meta:
        db_table = 'purchase'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='purchases')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='purchases')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_tickets = models.PositiveIntegerField()
    purchase_date = models.DateTimeField()

    def __str__(self):
        return f"Покупка на {self.event.name} ({self.total_amount}₽)"


# Билет
class PurchaseItem(models.Model):
    class Meta:
        db_table = 'purchase_item'

    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.ticket_type.name} ×{self.quantity}"
