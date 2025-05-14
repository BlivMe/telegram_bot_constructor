from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Bot, Block, BlockConnection, BotDataCapture, MenuButton
from .serializers import (
    BotSerializer, BlockSerializer, BlockConnectionSerializer,
    BotDataCaptureSerializer, MenuButtonSerializer
)
from .generator import generate_bot_code, start_bot, stop_bot


# Заглушка
def index(request):
    return JsonResponse({"message": "Добро пожаловать в конструктор ботов!"})


# CRUD для модели Bot
class BotViewSet(viewsets.ModelViewSet):
    queryset = Bot.objects.filter(deleted=False)
    serializer_class = BotSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_status = instance.status

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        new_status = serializer.validated_data.get('status')

        if old_status != new_status:
            if new_status == 'running':
                if instance.token:
                    generate_bot_code(instance)
                    start_bot(instance)
                else:
                    return Response({'error': 'Укажите токен перед запуском бота'}, status=400)
            elif new_status == 'stopped':
                stop_bot(instance)

        return Response(serializer.data)


# CRUD для блоков бота
class BlockViewSet(viewsets.ModelViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer


# CRUD для соединений между блоками
class BlockConnectionViewSet(viewsets.ModelViewSet):
    queryset = BlockConnection.objects.all()
    serializer_class = BlockConnectionSerializer


# CRUD для полей сбора данных
class BotDataCaptureViewSet(viewsets.ModelViewSet):
    queryset = BotDataCapture.objects.all()
    serializer_class = BotDataCaptureSerializer


# CRUD для кнопок в блоках-меню
class MenuButtonViewSet(viewsets.ModelViewSet):
    queryset = MenuButton.objects.all()
    serializer_class = MenuButtonSerializer


# Получение и сохранение структуры бота
class BotStructureView(APIView):
    def get(self, request, bot_id):
        bot = get_object_or_404(Bot, id=bot_id, deleted=False)
        blocks = Block.objects.filter(bot=bot).prefetch_related('buttons', 'data_fields')

        result = []
        for block in blocks:
            field_types = [f.field_type for f in block.data_fields.all()]
            result.append({
                'id': block.id,
                'bot': bot.id,
                'type': block.type,
                'title': block.title,
                'content': block.content,
                'x': block.x,
                'y': block.y,
                'buttons': [
                    {
                        'id': btn.id,
                        'text': btn.text,
                        'target_block': btn.target_block_id
                    } for btn in block.buttons.all()
                ],
                'collect_email': block.type == 'data_capture',
                'collect_birth_date': 'birth_date' in field_types,
                'collect_username': 'username' in field_types,
                'collect_gender': 'gender' in field_types,
                'collect_phone': 'phone' in field_types,
                'outgoing_connections': list(BlockConnection.objects.filter(source_block=block).values(
                    'id', 'source_block', 'target_block'
                ))
            })

        connections = []
        for block in blocks:
            for conn in BlockConnection.objects.filter(source_block=block):
                connections.append({
                    'source': conn.source_block_id,
                    'target': conn.target_block_id
                })
            for index, btn in enumerate(block.buttons.all()):
                if btn.target_block_id:
                    connections.append({
                        'source': block.id,
                        'target': btn.target_block_id,
                        'button_index': index
                    })

        return Response({'blocks': result, 'connections': connections})

    def post(self, request, bot_id):
        bot = get_object_or_404(Bot, id=bot_id, deleted=False)
        Block.objects.filter(bot=bot).delete()

        blocks_data = request.data.get('blocks', [])
        connections_data = request.data.get('connections', [])

        block_map = {}
        button_info = []

        for block in blocks_data:
            new_block = Block.objects.create(
                bot=bot,
                type=block['type'],
                title=block['title'],
                content=block.get('content', ''),
                x=block.get('x', 0),
                y=block.get('y', 0)
            )
            block_map[block['id']] = new_block
            button_info.append((block['id'], block.get('buttons', [])))

            if block['type'] == 'data_capture':
                BotDataCapture.objects.create(block=new_block, field_type='email')
                for field_type in ['birth_date', 'username', 'gender', 'phone']:
                    if block.get(f'collect_{field_type}'):
                        BotDataCapture.objects.create(block=new_block, field_type=field_type)

        buttons_map = {}
        for old_block_id, buttons in button_info:
            new_block = block_map[old_block_id]
            for i, btn in enumerate(buttons):
                text = btn['text'] if isinstance(btn, dict) else btn
                mb = MenuButton.objects.create(block=new_block, text=text)
                buttons_map[(old_block_id, i)] = mb

        for conn in connections_data:
            source = block_map.get(conn['source'])
            target = block_map.get(conn['target'])

            if source and target:
                button_index = conn.get('button_index')
                if button_index is not None:
                    btn = buttons_map.get((conn['source'], button_index))
                    if btn:
                        btn.target_block = target
                        btn.save()
                else:
                    BlockConnection.objects.create(source_block=source, target_block=target)

        return Response({'success': True})


# Получение и обновление токена бота
class BotTokenView(APIView):
    def get(self, request, bot_id):
        bot = get_object_or_404(Bot, id=bot_id, deleted=False)
        return Response({'token': bot.token})

    def post(self, request, bot_id):
        bot = get_object_or_404(Bot, id=bot_id, deleted=False)
        new_token = request.data.get('token')
        if new_token is not None:
            bot.token = new_token
            bot.save()
            return Response({'message': 'Токен обновлён'})
        return Response({'error': 'Токен не передан'}, status=status.HTTP_400_BAD_REQUEST)