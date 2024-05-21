
import os
import yaml
import json
from PIL import Image
from tqdm import tqdm

def parse_yolo(dataset_dir):
    dataset = {}
    names = {}
    image_files = {}
    label_files = {}

    for root_path, dir_list, file_list in os.walk(dataset_dir):
        for file_path in tqdm(file_list, 'Collecting Files', total=len(file_list)):
            file_name, file_ext = os.path.splitext(file_path)
            if file_ext == '.txt':
                label_files[file_name] = os.path.join(root_path, file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                image_files[file_name] = os.path.join(root_path, file_path)
            elif file_ext == '.yaml':
                with open(os.path.join(root_path, file_path), 'r') as f:
                    metadata = yaml.safe_load(f)
                    if 'names' in metadata:
                        names = metadata['names']
            elif file_ext == '.json':
                with open(os.path.join(root_path, file_path), 'r') as f:
                    metadata = json.load(f)
                    if 'names' in metadata:
                        names = metadata['names']
    
    for file_name, image_path in tqdm(image_files.items(), 'Processing Files', total=len(image_files)):
        if file_name not in label_files: continue

        img = Image.open(image_path)
        width, height = img.size


        data = {
            'filepath': image_path,
            'labels': [],
        }        

        data['width'] = width
        data['height'] = height

        with open(label_files[file_name], 'r') as f:
            for line in f:
                class_idx, x, y, w, h = map(float, line.split())
                class_idx = int(class_idx)
                if class_idx not in names:
                    names[class_idx] = str(class_idx)
                x *= width
                y *= height
                w *= width
                h *= height
                x1 = x - w / 2
                y1 = y - h / 2
                x2 = x1 + w
                y2 = y1 + h
                data['labels'].append({
                    'class': names[class_idx],
                    'xyxy': [x1, y1, x2, y2],
                    'xywh': [x, y, w, h],
                })
            dataset[file_name] = data

    return dataset, names
