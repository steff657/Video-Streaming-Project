import os
import subprocess
import uuid


def generate_thumbnail_from_video(
    input_path, output_dir, time='00:00:01'
):
    """Generate a JPG thumbnail for a video and return its file path."""
    if not input_path or not os.path.exists(input_path):
        return None

    os.makedirs(output_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    output_path = os.path.join(output_dir, filename)

    cmd = [
        'ffmpeg', '-y', '-ss', time, '-i', input_path,
        '-vframes', '1', '-q:v', '2', output_path,
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except OSError:
            pass
        return None

    return output_path
