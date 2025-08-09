import cv2

"""Extracts frames from a video file at a specified FPS."""
"""
Args:
    video_path (str): Full path to the video file.
    fps (int): Number of frames per second to extract (default is 5).

Returns:
    list: A list of extracted frames as BGR images (NumPy arrays).
"""
def extract_frames(video_path: str, fps: int = 5) -> list:
    
    frames = []
    try:
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        video_fps = cap.get(cv2.CAP_PROP_FPS)
        if video_fps == 0:
            raise ValueError("FPS is zero — corrupt or unreadable video.")

        frame_interval = int(video_fps // fps) if video_fps > fps else 1
        count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if count % frame_interval == 0:
                frames.append(frame)

            count += 1

        cap.release()
        if not frames:
            try:
                import imageio.v3 as iio
                # Read every Nth frame to approximate fps
                idx = 0
                for frm in iio.imiter(video_path):
                    if idx % frame_interval == 0:
                        # imageio returns RGB; convert to BGR for cv2 consumers
                        frames.append(cv2.cvtColor(frm, cv2.COLOR_RGB2BGR))
                    idx += 1
            except Exception as e:
                print(f"[ERROR] imageio fallback failed: {e}")

        return frames

    except Exception as e:
        print(f"[ERROR] Failed to extract frames: {e}")
        return []
