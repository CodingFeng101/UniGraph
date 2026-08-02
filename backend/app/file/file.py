import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from backend.common.response.response_schema import response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.core.path_conf import FILES_DIR, STATIC_DIR

MAX_UPLOAD_SIZE = 50 * 1024 * 1024
MAX_IMAGE_UPLOAD_SIZE = 5 * 1024 * 1024
UPLOAD_CHUNK_SIZE = 1024 * 1024
IMAGE_EXTENSIONS = {'.gif', '.jpeg', '.jpg', '.png', '.webp'}
DOCUMENT_EXTENSIONS = {'.docx', '.json', '.pdf', '.txt'}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS

router = APIRouter()


def _validate_filename(filename: str | None) -> str:
    if not filename or filename in {'.', '..'} or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid filename')
    return filename


@router.post('/upload', dependencies=[DependsJwtAuth])
async def upload_file(file: UploadFile = File(...)):
    filename = _validate_filename(file.filename)
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail='Unsupported file type',
        )
    is_image = extension in IMAGE_EXTENSIONS
    storage_root = Path(STATIC_DIR) if is_image else Path(FILES_DIR)
    folder_path = storage_root / str(uuid.uuid4())
    file_location = folder_path / filename
    max_size = MAX_IMAGE_UPLOAD_SIZE if is_image else MAX_UPLOAD_SIZE

    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        size = 0
        with file_location.open('xb') as output:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                size += len(chunk)
                if size > max_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f'File exceeds the {max_size // (1024 * 1024)} MiB upload limit',
                    )
                output.write(chunk)

        if is_image:
            try:
                with Image.open(file_location) as image:
                    image.verify()
            except (OSError, UnidentifiedImageError) as exc:
                raise HTTPException(status_code=400, detail='Invalid image file') from exc

        prefix = 'static' if is_image else 'files'
        file_url = f'{prefix}/{folder_path.name}/{filename}'
        return response_base.success(data={'url': file_url})
    except HTTPException:
        file_location.unlink(missing_ok=True)
        folder_path.rmdir()
        raise
    except OSError:
        file_location.unlink(missing_ok=True)
        if folder_path.exists():
            folder_path.rmdir()
        raise HTTPException(status_code=500, detail='Unable to store uploaded file')
    finally:
        await file.close()
