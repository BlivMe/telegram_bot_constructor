from rest_framework import serializers
from .models import Bot, Block, BlockConnection, BotDataCapture, MenuButton

# Сериализатор для кнопок меню
class MenuButtonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuButton
        fields = ['id', 'text', 'target_block']


# Сериализатор для полей сбора данных в блоке
class BotDataCaptureSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotDataCapture
        fields = ['id', 'field_type', 'required']


# Сериализатор для соединений между блоками
class BlockConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockConnection
        fields = ['id', 'source_block', 'target_block']


# Сериализатор блока
class BlockSerializer(serializers.ModelSerializer):
    buttons = MenuButtonSerializer(many=True, read_only=True)
    data_fields = BotDataCaptureSerializer(many=True, read_only=True)
    outgoing_connections = BlockConnectionSerializer(many=True, read_only=True)

    class Meta:
        model = Block
        fields = [
            'id', 'bot', 'type', 'title', 'content', 'creationdate',
            'x', 'y',
            'buttons', 'data_fields', 'outgoing_connections'
        ]


# Сериализатор бота
class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = '__all__'

    def validate_token(self, value):
        if value and value != 'placeholder-token':
            qs = Bot.objects.filter(token=value, deleted=False)
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError("Такой токен уже используется другим ботом.")
        return value
