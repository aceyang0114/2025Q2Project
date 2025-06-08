import json
import os
from PIL import Image

# 載入 VIA 匯出的 JSON
via_json_path = "C://Users//ADAT//Desktop//Ace/LorryImage//RFID//via_project_2Jun2025_15h21m_json.json"
image_folder = "C://Users//ADAT//Desktop//Ace/LorryImage//RFID//images"  # 放標註圖的資料夾
output_label_folder = "C://Users//ADAT//Desktop//Ace/LorryImage//RFID//labels"  # 轉出的 YOLO label 存這裡
os.makedirs(output_label_folder, exist_ok=True)

# 只使用一種類別（class 0）
CLASS_ID = 0

with open(via_json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data.values():
    filename = item['filename']
    regions = item['regions']
    image_path = os.path.join(image_folder, filename)

    # 取得圖片尺寸
    try:
        with Image.open(image_path) as img:
            img_width, img_height = img.size
    except Exception as e:
        print(f"無法開啟圖片：{filename}，錯誤：{e}")
        continue

    label_lines = []

    for region in regions:
        shape = region['shape_attributes']
        x = shape['x']
        y = shape['y']
        w = shape['width']
        h = shape['height']

        # 轉為相對座標
        x_center = (x + w / 2) / img_width
        y_center = (y + h / 2) / img_height
        rel_w = w / img_width
        rel_h = h / img_height

        label_line = f"{CLASS_ID} {x_center:.6f} {y_center:.6f} {rel_w:.6f} {rel_h:.6f}"
        label_lines.append(label_line)

    # 輸出對應的 txt 檔
    label_path = os.path.join(output_label_folder, filename.rsplit(".", 1)[0] + ".txt")
    with open(label_path, "w") as f:
        f.write("\n".join(label_lines))

print("✅ 轉換完成，YOLO 標註已儲存至 labels 資料夾")
