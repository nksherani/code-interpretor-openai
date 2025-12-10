"""
Container file management service using OpenAI Containers Files API.
"""
import logging

logger = logging.getLogger(__name__)


class ContainerFileService:
    def __init__(self, client):
        self.client = client

    def fetch(self, file_id: str, container_id: str):
        """
        Fetch file content and metadata using the Containers Files API.
        Both container_id and file_id are required.
        Returns (file_data, file_info)
        """
        logger.info(f"📥 Fetching container file: file_id={file_id}, container_id={container_id}")
        file_info = self.client.containers.files.retrieve(
            container_id=container_id,
            file_id=file_id,
        )
        logger.info(f"File info: {file_info}")
        file_data = self.client.containers.files.content.retrieve(
            container_id=container_id,
            file_id=file_id,
        )
        
        logger.info(f"✓ Retrieved container file via containers.files: {file_id}")
        return file_data, file_info
