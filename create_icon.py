from PIL import Image, ImageDraw

def draw_icon(size):
    """Рисует иконку ChatList - символ чата со списком."""
    # Создаем RGB изображение с градиентным фоном
    img = Image.new("RGB", (size, size), (41, 128, 185))  # Синий фон
    draw = ImageDraw.Draw(img)
    
    # Цвета
    bg_color = (41, 128, 185)  # Синий фон
    chat_color = (255, 255, 255)  # Белый для чата
    accent_color = (52, 152, 219)  # Светло-синий акцент
    
    # Рисуем фон с градиентом (упрощенный)
    padding = int(size * 0.05)
    
    # Рисуем символ чата (пузырь сообщения)
    chat_size = int(size * 0.4)
    chat_x = int(size * 0.3)
    chat_y = int(size * 0.25)
    
    # Основной пузырь чата
    chat_coords = [
        chat_x,
        chat_y,
        chat_x + chat_size,
        chat_y + chat_size
    ]
    draw.ellipse(chat_coords, fill=chat_color, outline=accent_color, width=2)
    
    # Хвостик пузыря (указывает вниз)
    tail_size = int(size * 0.08)
    tail_points = [
        (chat_x + int(chat_size * 0.3), chat_y + chat_size),
        (chat_x + int(chat_size * 0.5), chat_y + chat_size + tail_size),
        (chat_x + int(chat_size * 0.7), chat_y + chat_size)
    ]
    draw.polygon(tail_points, fill=chat_color, outline=accent_color)
    
    # Рисуем список (три линии под чатом)
    list_y_start = int(size * 0.65)
    list_line_height = int(size * 0.04)
    list_spacing = int(size * 0.08)
    list_x_start = int(size * 0.2)
    list_x_end = int(size * 0.8)
    
    for i in range(3):
        y_pos = list_y_start + i * list_spacing
        # Линия списка
        draw.rectangle(
            [list_x_start, y_pos, list_x_end, y_pos + list_line_height],
            fill=chat_color,
            outline=accent_color
        )
        # Точка перед линией (маркер списка)
        dot_size = int(size * 0.03)
        dot_x = list_x_start - int(size * 0.05)
        draw.ellipse(
            [dot_x, y_pos, dot_x + dot_size, y_pos + list_line_height],
            fill=accent_color
        )
    
    return img

# Размеры иконки
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
icons = [draw_icon(s) for s, _ in sizes]

# Изображения уже в RGB режиме, просто убеждаемся
rgb_icons = []
for icon in icons:
    # Убеждаемся, что изображение в RGB режиме (не палитра)
    if icon.mode != "RGB":
        rgb_img = icon.convert("RGB")
    else:
        rgb_img = icon
    rgb_icons.append(rgb_img)

# Сохранение с явным указанием формата и цветов
# ВАЖНО: Изображения уже в RGB режиме с красным фоном, что гарантирует
# сохранение цветов и избегает автоматической конвертации в градации серого
try:
    rgb_icons[0].save(
        "app.ico",
        format="ICO",
        sizes=sizes,
        append_images=rgb_icons[1:]
    )
    print("Иконка 'app.ico' создана!")
    print("   Дизайн: символ чата со списком (ChatList)")
    print("   Цвета: синий фон, белый чат, светло-синий акцент")
except Exception as e:
    print(f"Ошибка при сохранении: {e}")
    # Альтернативный способ - сохранить каждое изображение отдельно
    print("Попытка альтернативного метода сохранения...")
    rgb_icons[0].save("app.ico", format="ICO")
    print("Иконка 'app.ico' создана (только один размер)")