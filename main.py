"""
Appwrite Function: Frame Generator for Keyword Video
Generates PNG frames with keyword highlighting effect
"""

import json
import os
import random
import tempfile
import io
import base64
from appwrite.client import Client
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile
from appwrite.permission import Permission
from appwrite.role import Role

from PIL import Image, ImageDraw, ImageFont

# Configuration
W, H = 540, 970
BG_COLOR = (245, 242, 235)
TEXT_COLOR = (150, 150, 150)
HIGHLIGHT_COLOR = (255, 230, 120)

COLUMN_X_MIN = -200
COLUMN_X_MAX = 200

LINE_H = 52
LINES_ABOVE = 20
LINES_BELOW = 20

CORPUS = (
    "The city council convened early that morning as reports continued "
    "to circulate through the press and among residents who had grown "
    "increasingly uneasy about the unfolding situation and its possible "
    "implications for the wider region and beyond"
)

def generate_line(min_words=14, max_words=24):
    """Generate a random line of text from corpus"""
    words = CORPUS.split()
    count = random.randint(min_words, max_words)
    return " ".join(random.choice(words) for _ in range(count))

def generate_context(min_words=4, max_words=10):
    """Generate context text around keyword"""
    words = CORPUS.split()
    count = random.randint(min_words, max_words)
    return " ".join(random.choice(words) for _ in range(count))

def faded_color(base, strength):
    """Create faded grayscale color"""
    v = max(140, int(base - strength))
    return (v, v, v)

def layout_anchor_line(font, center_x, before_text, after_text, keyword):
    """Calculate positions for keyword and surrounding text"""
    before = before_text.capitalize()
    key = keyword
    after = after_text.rstrip(".") + "."

    before_w = font.getlength(before)
    key_w = font.getlength(key)

    key_left = center_x - key_w / 2

    return {
        "before": (key_left - before_w, before),
        "key": (key_left, key),
        "after": (key_left + key_w, after)
    }

def render_frame(keyword, highlight_box=True):
    """Render a single frame and return as bytes"""
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to load Arial, fallback to default
    try:
        font = ImageFont.truetype(os.path.join(os.getcwd(), "fonts", "Arial.ttf"), 52)
    except:
        font = ImageFont.load_default()
    
    # Generate text
    before_text = generate_context() + " "
    after_text = " " + generate_context()
    
    bbox = font.getbbox(keyword)
    kw = bbox[2] - bbox[0]
    kh = bbox[3] - bbox[1]
    
    pad = 6

    center_y = H // 2
    center_x = W // 2
    anchor = layout_anchor_line(font, center_x, before_text, after_text, keyword)
    column_x = anchor["before"][0]
    column_jitter = random.randint(COLUMN_X_MIN, COLUMN_X_MAX)
    column_x += column_jitter
    
    # Draw lines above
    for i in range(LINES_ABOVE):
        dist = i
        fade = dist * 15
        color = faded_color(220, fade)
    
        y = center_y - (LINES_ABOVE - i) * LINE_H
        text = generate_line()
        draw.text((column_x, y), text, font=font, fill=color)

    # Draw anchor line with keyword
    y = center_y
    y += random.randint(-2, 2)  # slight vertical jitter

    key_x = anchor["key"][0]

    draw.text((anchor["before"][0], y), anchor["before"][1],
              font=font, fill=TEXT_COLOR)
    
    if highlight_box:
        draw.rectangle([
            (key_x - pad, y - pad),
            (key_x + kw + pad, y + kh + pad)],
        fill=(255, 245, 180)
        )
    
    draw.text((anchor["key"][0], y), anchor["key"][1],
              font=font, fill=HIGHLIGHT_COLOR)
    draw.text((anchor["after"][0], y), anchor["after"][1],
              font=font, fill=TEXT_COLOR)

    # Draw lines below
    for i in range(LINES_BELOW):
        dist = abs(i - LINES_BELOW)
        fade = dist * 15
        color = faded_color(220, fade)
        
        y = center_y + (i + 1) * LINE_H
        text = generate_line()
        draw.text((column_x, y), text, font=font, fill=color)

    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()

def main(context):
    """Main function handler for Appwrite"""
    
    # Parse request
    try:
        if context.req.body:
            payload = json.loads(context.req.body)
        else:
            payload = {}
    except:
        return context.res.json({
            "success": False,
            "error": "Invalid JSON payload"
        }, 400)
    
    # Extract parameters
    keyword = payload.get("keyword", "Hello World")
    highlight = payload.get("highlight", True)
    frame_count = payload.get("frame_count", 7)
    
    # Validate
    if not keyword or len(keyword) > 50:
        return context.res.json({
            "success": False,
            "error": "Keyword must be between 1-50 characters"
        }, 400)
    
    if frame_count < 1 or frame_count > 20:
        return context.res.json({
            "success": False,
            "error": "Frame count must be between 1-20"
        }, 400)
    
    # Initialize Appwrite client
    client = Client()
    client.set_endpoint(os.environ.get('APPWRITE_FUNCTION_API_ENDPOINT'))
    client.set_project(os.environ.get('APPWRITE_FUNCTION_PROJECT_ID'))
    client.set_key(os.environ.get("APPWRITE_API_KEY"))
    
    storage = Storage(client)
    bucket_id = os.environ.get('BUCKET_ID', 'frames')
    
    # Generate and upload frames
    frames = []
    
    try:
        for i in range(frame_count):
            # Generate frame
            frame_bytes = render_frame(keyword, highlight_box=highlight)
            
            # Upload to storage
            file_id = f"frame_{random.randint(100000, 999999)}_{i:03d}"
            tmp_path = f"/tmp/{file_id}.png"

            # Write bytes to temp file
            with open(tmp_path, "wb") as f:
                f.write(frame_bytes)
            
            # file=InputFile.from_bytes(frame_bytes, filename=f"{file_id}.png"),

            result = storage.create_file(
                bucket_id=bucket_id,
                file_id=file_id,
                file=InputFile.from_path(tmp_path),
                permissions=[
                    Permission.read(Role.any()),
                    Permission.write(Role.any())
                ]
            )
            
            # Get file URL
            file_url = f"{os.environ.get('APPWRITE_FUNCTION_API_ENDPOINT')}/storage/buckets/{bucket_id}/files/{file_id}/view?project={os.environ.get('APPWRITE_FUNCTION_PROJECT_ID')}"
            
            frames.append({
                "id": file_id,
                "url": file_url,
                "index": i
            })
            
            context.log(f"Generated frame {i+1}/{frame_count}")
    
    except Exception as e:
        context.error(f"Error generating frames: {str(e)}")
        return context.res.json({
            "success": False,
            "error": f"Failed to generate frames: {str(e)}"
        }, 500)
    
    # Return success
    return context.res.json({
        "success": True,
        "frames": frames,
        "frame_count": len(frames),
        "keyword": keyword,
        "highlight": highlight
    })
