import base64
import json
import os
import re
import time
from openai import OpenAI

API_KEY = "sk-a4a3bf5831e44ec4be7fb6add02bf995"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-vl-plus"
IMAGE_DIR = "uploads"
OUT_FILE = "isbn_results.json"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')


def extract_isbn(text):
    patterns = [
        r'ISBN[-\s]*(?:13)?[-\s]*[:]?[-\s]*(\d{3}[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?\d{1})',
        r'ISBN[-\s]*(?:10)?[-\s]*[:]?[-\s]*(\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?[\dX])',
        r'(\d{3}[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?\d{1})',
        r'(\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,7}[-\s]?[\dX])',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).replace('-', '').replace(' ', '').upper()
    return None


def recognize_isbn(image_path):
    prompt = """请仔细查看这张图片，识别并提取书中的 ISBN 码。
ISBN 通常是 10 位或 13 位数字，可能带有连字符分隔。
请以纯文本格式返回找到的 ISBN 号码，如果没有找到请说明。
格式示例：978-7-111-12345-6 或 9787111123456"""
    try:
        base64_data = encode_image(image_path)
        messages = [{"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}, {"type": "text", "text": prompt}]}]
        response = client.chat.completions.create(model=MODEL, messages=messages)
        result_text = response.choices[0].message.content
        isbn = extract_isbn(result_text)
        return {"success": True, "image_path": image_path, "raw_response": result_text, "isbn": isbn, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    except Exception as e:
        return {"success": False, "image_path": image_path, "error": str(e), "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}


def batch_recognize(image_dir=IMAGE_DIR, output_file=OUT_FILE):
    valid_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    results = []
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(valid_exts):
            image_path = os.path.join(image_dir, filename)
            print(f"\n处理: {filename}")
            result = recognize_isbn(image_path)
            results.append(result)
            if result["success"]:
                print(f"✓ ISBN: {result['isbn']}" if result["isbn"] else f"⚠ 未找到: {result['raw_response'][:100]}...")
            else:
                print(f"✗ 失败: {result['error']}")
            time.sleep(0.5)

    output_path = os.path.join(image_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    total = len(results)
    success = sum(1 for r in results if r["success"] and r["isbn"])
    print(f"\n{'='*50}\n完成! 总计: {total}, 成功: {success}, 失败: {total - success}\n保存至: {output_path}")
    return results


def verify_image(image_path, username=None):
    result = recognize_isbn(image_path)
    if username:
        result["username"] = username
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        if os.path.exists(image_path):
            print(json.dumps(recognize_isbn(image_path), ensure_ascii=False, indent=2))
        else:
            print(f"错误: 文件不存在 - {image_path}")
    else:
        print("开始批量识别 ISBN...")
        batch_recognize()
