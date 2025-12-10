from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import mimetypes
import traceback
import logging
from typing import Optional

from container_file_service import ContainerFileService
from assistant_manager import get_openai_client

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize service on first use
service: Optional[ContainerFileService] = None


def get_service() -> ContainerFileService:
    global service
    if service is None:
        client = get_openai_client()
        service = ContainerFileService(client)
    return service


@router.get("/api/file/{file_id}")
async def download_container_file(file_id: str, container_id: str):
    """
    Download a file generated inside the container via OpenAI Containers Files API.
    Both file_id and container_id are required.
    """
    try:
        svc = get_service()
        file_data, file_info = svc.fetch(file_id=file_id, container_id=container_id)

        # Determine content type
        filename = getattr(file_info, "filename", None) or f"output_{file_id}.bin"
        content_type, _ = mimetypes.guess_type(filename)
        content_type = content_type or "application/octet-stream"

        return StreamingResponse(
            iter([file_data.content]),
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Cache-Control": "public, max-age=3600",
            },
        )

    except Exception as e:
        logger.error(f"❌ Error retrieving container file {file_id}: {e}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"File retrieval failed: {str(e)}")

