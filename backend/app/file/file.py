import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.common.response.response_schema import response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.core.path_conf import STATIC_DIR

MAX_UPLOAD_SIZE = 50 * 1024 * 1024
UPLOAD_CHUNK_SIZE = 1024 * 1024

router = APIRouter()


def _validate_filename(filename: str | None) -> str:
    if not filename or filename in {'.', '..'} or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid filename')
    return filename


@router.post('/upload', dependencies=[DependsJwtAuth])
async def upload_file(file: UploadFile = File(...)):
    filename = _validate_filename(file.filename)
    folder_path = Path(STATIC_DIR) / str(uuid.uuid4())
    file_location = folder_path / filename

    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        size = 0
        with file_location.open('xb') as output:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail='File exceeds the 50 MiB upload limit',
                    )
                output.write(chunk)

        file_url = f'static/{folder_path.name}/{filename}'
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
