from django.db import models
from api.models import Company

# Модель Telegram-бота
class Bot(models.Model):
    class Meta:
        db_table = 'bots_bot'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bots')
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    creationdate = models.DateTimeField(auto_now_add=True)
    modificationdate = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, default='draft')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Блок внутри чат-бота
class Block(models.Model):
    class Meta:
        db_table = 'bots_block'

    BLOCK_TYPE_CHOICES = [
        ('start', 'Start'),
        ('menu', 'Menu'),
        ('message', 'Message'),
        ('data_capture', 'Data Capture'),
    ]

    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='blocks')
    type = models.CharField(max_length=50, choices=BLOCK_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    creationdate = models.DateTimeField(auto_now_add=True)
    x = models.FloatField(default=100)
    y = models.FloatField(default=100)

    def __str__(self):
        return f"{self.type}: {self.title}"


# Кнопка в блоке меню
class MenuButton(models.Model):
    class Meta:
        db_table = 'bots_menubutton'

    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='buttons')
    text = models.CharField(max_length=100)
    target_block = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_buttons')

    def __str__(self):
        return f"{self.text} → {self.target_block}"


# Прямая связь между блоками
class BlockConnection(models.Model):
    class Meta:
        db_table = 'bots_blockconnection'

    source_block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='outgoing_connections')
    target_block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='incoming_connections')

    def __str__(self):
        return f"{self.source_block} ➝ {self.target_block}"


# Описание поля для блока "Сбор данных"
class BotDataCapture(models.Model):
    class Meta:
        db_table = 'bots_botdatacapture'

    FIELD_TYPE_CHOICES = [
        ('email', 'Email'),
        ('birth_date', 'Birth Date'),
        ('username', 'Username'),
        ('gender', 'Gender'),
        ('phone', 'Phone'),
    ]

    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='data_fields')
    field_type = models.CharField(max_length=50, choices=FIELD_TYPE_CHOICES)
    required = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.block.title} — {self.field_type} ({'обязательно' if self.required else 'опционально'})"