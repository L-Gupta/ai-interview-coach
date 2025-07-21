#Saves and processed audio
import os
from fastapi import UploadFile
import aiofiles

async def save_audio_file(file: UploadFile) -> str:
    filename = f"temp_audio/{file.filename}"
    os.makedirs("temp_audio", exist_ok=True)
    
    async with aiofiles.open(filename, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    return filename
