import mimetypes
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.core.path_conf import STATIC_DIR

router = APIRouter()
IMAGE_EXTENSIONS = {'.gif', '.jpeg', '.jpg', '.png', '.webp'}


@router.get(
    '/static/{unique_id}/{filename}',
    summary='获取图片',
)
async def get_image(unique_id: str, filename: str) -> FileResponse:
    """
    前端通过URL的方式，经过fastapi路由中专请求，并返回图片
    """
    try:
        if filename in {'.', '..'} or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail='Invalid filename')
        if Path(filename).suffix.lower() not in IMAGE_EXTENSIONS:
            raise HTTPException(status_code=404, detail='Image does not exist')

        if unique_id != 'default':
            try:
                UUID(unique_id)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail='Invalid image directory') from exc

        file_path = Path(STATIC_DIR) / str(unique_id) / filename
        if not file_path.is_file():
            raise HTTPException(status_code=404, detail='文件不存在')

        mime_type, _ = mimetypes.guess_type(str(file_path))
        return FileResponse(
            path=file_path,
            media_type=mime_type or 'application/octet-stream',
            headers={'X-Content-Type-Options': 'nosniff'},
        )
    except HTTPException:
        raise
    except OSError:
        raise HTTPException(status_code=500, detail='Unable to read file')
