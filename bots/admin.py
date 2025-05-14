from django.contrib import admin
from .models import Bot, Block, BlockConnection, BotDataCapture, MenuButton

# Админка для модели Bot
@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'status', 'creationdate')
    list_filter = ('status', 'creationdate', 'modificationdate')

# Админка для блоков
@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'type', 'bot', 'creationdate')
    list_filter = ('type', 'creationdate')

# Админка для связей между блоками
@admin.register(BlockConnection)
class BlockConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_block', 'target_block')
    list_filter = ('source_block', 'target_block')

# Админка для кнопок в меню
@admin.register(MenuButton)
class MenuButtonAdmin(admin.ModelAdmin):
    list_display = ('id', 'block', 'text', 'target_block')
    list_filter = ('block',)

# Админка для полей сбора данных
@admin.register(BotDataCapture)
class BotDataCaptureAdmin(admin.ModelAdmin):
    list_display = ('id', 'block', 'field_type', 'required')
    list_filter = ('field_type', 'required')