from PIL import Image, ImageDraw, ImageFont


def try_load_fonts(font_sizes):
    result = {}
    try:
        for name, size in font_sizes:
            result[name] = ImageFont.truetype("msyh.ttc", size)
    except Exception:
        for name, size in font_sizes:
            result[name] = ImageFont.load_default()
    return result


def create_book_cover_image(book, output_path, bg_color='#F5F5DC'):
    width, height = 600, 800
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    fonts = try_load_fonts([
        ('title', 36), ('author', 24), ('isbn', 28), ('price', 32), ('small', 16),
    ])

    # border
    border_margin = 20
    draw.rectangle(
        [(border_margin, border_margin), (width - border_margin, height - border_margin)],
        outline='#8B4513', width=3,
    )

    # title
    title = book['title']
    if len(title) > 12:
        mid = len(title) // 2
        title = title[:mid] + '\n' + title[mid:]
    draw.text((width // 2, 150), title, fill='#333333',
              font=fonts['title'], anchor='mm', align='center')

    # author
    draw.text((width // 2, 260), f"作者：{book['author']}", fill='#666666',
              font=fonts['author'], anchor='mm')

    # price
    draw.rectangle([(200, 320), (400, 390)], fill='#FF6B6B', outline='#FF4757', width=2)
    draw.text((width // 2, 355), f"¥{book['price']}", fill='white',
              font=fonts['price'], anchor='mm')

    # ISBN region
    isbn_y = 500
    draw.rectangle([(50, isbn_y - 10), (width - 50, isbn_y + 80)],
                   fill='white', outline='#333333', width=2)
    draw.text((width // 2, isbn_y + 35), f"ISBN: {book['isbn']}", fill='#000000',
              font=fonts['isbn'], anchor='mm')

    # barcode
    import random
    barcode_y = isbn_y + 100
    barcode_height = 60
    x = 100
    random.seed(book['isbn'])
    while x < width - 100:
        line_width = random.choice([2, 3, 4, 5])
        draw.line([(x, barcode_y), (x, barcode_y + barcode_height)],
                  fill='black', width=line_width)
        x += line_width + random.choice([1, 2, 3])

    draw.text((width // 2, barcode_y + barcode_height + 20),
              book['isbn'], fill='#333333', font=fonts['isbn'], anchor='mm')

    draw.text((width // 2, height - 30), "SeekBook Test Image",
              fill='#999999', font=fonts['small'], anchor='mm')

    img.save(output_path, 'JPEG', quality=95)
    print(f"[OK] Generated: {output_path}")
    print(f"     Title: {book['title']}")
    print(f"     ISBN: {book['isbn']}")
    print()


def create_isbn_only_image(isbn, output_path):
    width, height = 400, 200
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    fonts = try_load_fonts([('big', 48), ('small', 20)])

    draw.rectangle([(10, 10), (width - 10, height - 10)],
                   outline='#333333', width=2)
    draw.text((width // 2, 50), "ISBN", fill='#666666',
              font=fonts['small'], anchor='mm')
    draw.text((width // 2, 120), isbn, fill='#000000',
              font=fonts['big'], anchor='mm')

    img.save(output_path, 'JPEG', quality=95)
    print(f"[OK] Generated: {output_path}")
    print(f"     ISBN: {isbn}")
    print()