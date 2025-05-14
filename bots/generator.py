import os
import subprocess
import platform
import signal
from pathlib import Path

from django.conf import settings
from jinja2 import Environment, FileSystemLoader

from bots.models import Block, BlockConnection

# Основные директории для шаблонов и выходных файлов
BASE_DIR = Path(settings.BASE_DIR).resolve().parent
GENERATED_BOTS_DIR = BASE_DIR / 'bots' / 'generated_bots'
GENERATED_BOTS_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATE_DIR = BASE_DIR / 'bots' / 'templates'
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

# Генерация Python-бота из шаблона Jinja2
def generate_bot_code(bot):
    template = env.get_template('bot_template.py.j2')

    blocks = Block.objects.filter(bot=bot).prefetch_related('buttons', 'data_fields')
    connections = BlockConnection.objects.filter(source_block__bot=bot)

    # Составление карты переходов между блоками
    outgoing_map = {}
    for conn in connections:
        outgoing_map.setdefault(conn.source_block_id, []).append(conn.target_block_id)

    block_data = []
    start_block_id = None

    # Формируем данные по каждому блоку
    for block in blocks:
        if block.type == 'start':
            start_block_id = block.id
        block_data.append({
            'id': block.id,
            'type': block.type,
            'title': block.title,
            'content': block.content or '',
            'buttons': [
                {'text': btn.text, 'target_block': btn.target_block_id}
                for btn in block.buttons.all()
            ],
            'fields': [f.field_type for f in block.data_fields.all()],
            'outgoing': outgoing_map.get(block.id, [])
        })

    if start_block_id is None:
        raise ValueError("Стартовый блок не найден для этого бота.")

    rendered_code = template.render(
        token=bot.token,
        blocks=block_data,
        start_block_id=start_block_id
    )

    output_path = GENERATED_BOTS_DIR / f'bot_{bot.id}.py'
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(rendered_code)

    return output_path

# Получение пути к .pid-файлу процесса
def get_pid_file_path(bot_id):
    return GENERATED_BOTS_DIR / f'bot_{bot_id}.pid'

# Запуск сгенерированного .py-бота
def start_bot(bot):
    script_path = GENERATED_BOTS_DIR / f'bot_{bot.id}.py'
    if not script_path.exists():
        raise FileNotFoundError(f"Скрипт бота не найден: {script_path}")

    python_path = BASE_DIR / 'venv' / 'Scripts' / 'python.exe'  # путь под Windows

    process = subprocess.Popen(
        [str(python_path), str(script_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    with open(get_pid_file_path(bot.id), 'w') as file:
        file.write(str(process.pid))

    print(f"[start_bot] Бот запущен с PID {process.pid}")

# Остановка процесса бота по PID
def stop_bot(bot):
    pid_path = get_pid_file_path(bot.id)
    if pid_path.exists():
        try:
            with open(pid_path, 'r') as file:
                pid = int(file.read())
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
            else:
                os.kill(pid, signal.SIGKILL)
            print(f"[stop_bot] Процесс с PID {pid} остановлен.")
        except Exception as e:
            print(f"[stop_bot] Не удалось остановить процесс PID {pid}: {e}")
        finally:
            pid_path.unlink(missing_ok=True)
    else:
        print(f"[stop_bot] PID-файл не найден для бота {bot.id}")
