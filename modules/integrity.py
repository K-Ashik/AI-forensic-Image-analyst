import hashlib
import os
from PIL import Image, ImageChops, ImageEnhance, ImageStat
import io

def calculate_hash(image_path):
    sha256_hash = hashlib.sha256()
    with open(image_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def extract_metadata(image_path):
    img = Image.open(image_path)
    exif_data = img._getexif()
    
    if not exif_data:
        return {"Status": "No Metadata Found (Likely a Screenshot or Stripped)"}
    
    from PIL.ExifTags import TAGS
    metadata = {}
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name not in ["MakerNote", "PrintImageMatching"]:
            # Truncate long binary data
            val_str = str(value)
            if len(val_str) > 50: 
                val_str = val_str[:50] + "..."
            metadata[tag_name] = val_str
            
    return metadata

def perform_ela(image_path, quality=90):
    """
    Generates ELA image and calculates a mathematical verdict.
    """
    original = Image.open(image_path).convert('RGB')
    
    # 1. Create ELA Image
    buffer = io.BytesIO()
    original.save(buffer, 'JPEG', quality=quality)
    buffer.seek(0)
    compressed = Image.open(buffer)
    
    ela_image = ImageChops.difference(original, compressed)
    
    # 2. Amplify the signal
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
    
    # 3. MATHEMATICAL VERDICT (The New Feature)
    # We calculate the brightness statistics of the ELA noise
    stat = ImageStat.Stat(ela_image)
    avg_brightness = sum(stat.mean) / len(stat.mean)
    max_brightness = sum(stat.extrema[0]) / len(stat.extrema[0]) # Approximate max
    
    # Heuristic: If specific pixels are wildly brighter than the average, it's suspicious.
    # A generic "noisy" image has high average brightness.
    # A spliced image has low average brightness but high peaks.
    
    verdict_score = max_diff # The raw difference level
    
    verdict_text = "Analysis Inconclusive"
    color = "orange"
    
    if avg_brightness < 15 and max_brightness > 100:
        verdict_text = "⚠️ POTENTIAL TAMPERING DETECTED (High Local Variance)"
        color = "red"
    elif avg_brightness > 30:
        verdict_text = "ℹ️ Low Quality / Resaved Image (High Global Noise)"
        color = "blue"
    else:
        verdict_text = "✅ Likely Original / Consistent Compression"
        color = "green"

    return ela_image, verdict_text, color