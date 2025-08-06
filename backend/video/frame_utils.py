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
        return frames

    except Exception as e:
        print(f"[ERROR] Failed to extract frames: {e}")
        return []
