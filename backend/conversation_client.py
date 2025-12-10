"""
Lightweight wrapper around OpenAI Responses + Conversations APIs.

Notes:
- Uses the new Conversations API for multi-turn context.
- Uses the Responses API to run model calls with tools (code interpreter).
- Designed to keep a narrow surface area so we can swap providers later.
"""
import time
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class ResponsesClient:
    def __init__(self, client, default_model: str = "gpt-4.1"):
        self.client = client
        self.default_model = default_model
        if not hasattr(self.client, "conversations"):
            raise RuntimeError(
                "OpenAI client does not support Conversations API. "
                "Please upgrade openai package to >=1.60.0"
            )

    def create_conversation(self) -> str:
        convo = self.client.conversations.create()
        logger.info(f"✓ Conversation created: {convo.id}")
        return convo.id

    def run_response(
        self,
        conversation_id: str,
        input_blocks: List[Dict[str, Any]],
        model: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        model_to_use = model or self.default_model
        logger.info(f"Creating response with model={model_to_use}, tools={tools}")
        response = self.client.responses.create(
            model=model_to_use,
            conversation=conversation_id,
            input=input_blocks,
            tools=tools or [],
        )
        logger.info(f"Response: {response}")
        logger.info(f"✓ Response created: {response.id}, status={response.status}")
        return response

    def wait_on_response(self, response, poll_interval: float = 0.6, timeout: float = 120.0):
        start = time.time()
        while response.status in ("in_progress", "queued", "requires_action"):
            if time.time() - start > timeout:
                raise TimeoutError("Response polling timed out")
            time.sleep(poll_interval)
            response = self.client.responses.retrieve(response.id)
            logger.info(f"… polling response {response.id}, status={response.status}")
        logger.info(f"✓ Response completed with status={response.status}")
        return response

    def parse_response_output(self, response):
        """
        Extract text and file annotations from a Responses API response.
        """
        text_chunks = []
        annotations = []

        response_id = getattr(response, "id", None)
        current_container_id = None

        # Convenience: output_text attribute if present
        if hasattr(response, "output_text") and response.output_text:
            text_chunks.append(response.output_text)

        outputs = getattr(response, "output", None)
        if outputs:
            for block in outputs:
                # Track container id if present on tool call blocks
                current_container_id = getattr(block, "container_id", current_container_id)

                # Some blocks have .content as a list
                content_list = getattr(block, "content", [])
                for item in content_list:
                    item_type = getattr(item, "type", "")
                    # Text handling
                    if item_type in ("text", "output_text", "summary_text", "refusal"):
                        txt_obj = getattr(item, "text", None)
                        val = getattr(txt_obj, "value", None) if txt_obj else None
                        if not val:
                            val = getattr(item, "output_text", None) or getattr(item, "value", None)
                        if val:
                            text_chunks.append(val)
                    # File/image handling
                    if item_type == "file_path" and hasattr(item, "file_path"):
                        fp = item.file_path
                        annotations.append({
                            "type": "file_path",
                            "file_id": fp.file_id,
                            "text": getattr(item, "text", ""),
                            "filename": getattr(fp, "filename", None) or getattr(fp, "path", None),
                            "path": getattr(fp, "path", None) or getattr(fp, "filepath", None),
                            "mime_type": getattr(fp, "mime_type", None) or getattr(fp, "content_type", None),
                            "response_id": response_id,
                            "container_id": current_container_id,
                        })
                    if item_type == "image_file" and hasattr(item, "image_file"):
                        img = item.image_file
                        annotations.append({
                            "type": "image_file",
                            "file_id": img.file_id,
                            "filename": getattr(img, "filename", None) or getattr(img, "path", None),
                            "path": getattr(img, "path", None) or getattr(img, "filepath", None),
                            "mime_type": getattr(img, "mime_type", None) or getattr(img, "content_type", None),
                            "response_id": response_id,
                            "container_id": current_container_id,
                        })
                    if item_type in ("output_file", "file") and hasattr(item, "file"):
                        fobj = item.file
                        annotations.append({
                            "type": "file_path",
                            "file_id": fobj.file_id if hasattr(fobj, "file_id") else getattr(fobj, "id", None),
                            "text": getattr(item, "text", ""),
                            "filename": getattr(fobj, "filename", None) or getattr(fobj, "path", None),
                            "path": getattr(fobj, "path", None) or getattr(fobj, "filepath", None),
                            "mime_type": getattr(fobj, "mime_type", None) or getattr(fobj, "content_type", None),
                            "response_id": response_id,
                            "container_id": current_container_id,
                        })
                    if item_type in ("output_image", "image") and hasattr(item, "image"):
                        img = item.image
                        annotations.append({
                            "type": "image_file",
                            "file_id": img.file_id if hasattr(img, "file_id") else getattr(img, "id", None),
                            "filename": getattr(img, "filename", None) or getattr(img, "path", None),
                            "path": getattr(img, "path", None) or getattr(img, "filepath", None),
                            "mime_type": getattr(img, "mime_type", None) or getattr(img, "content_type", None),
                            "response_id": response_id,
                            "container_id": current_container_id,
                        })
                    # Annotations inside text blocks (e.g., container file citations)
                    ann_list = getattr(item, "annotations", []) or []
                    for ann in ann_list:
                        ann_type = getattr(ann, "type", "")
                        if ann_type in ("container_file_citation", "file_citation", "file_path"):
                            fid = getattr(ann, "file_id", None) or getattr(ann, "id", None)
                            if fid:
                                annotations.append({
                                    "type": "image_file" if str(fid).endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")) else "file_path",
                                    "file_id": fid,
                                    "text": getattr(ann, "text", ""),
                                    "filename": getattr(ann, "filename", None),
                                    "path": getattr(ann, "path", None) or getattr(ann, "filepath", None),
                                    "mime_type": getattr(ann, "mime_type", None) or getattr(ann, "content_type", None),
                                    "response_id": response_id,
                                    "container_id": current_container_id,
                                })

        # Also handle top-level output_files if present
        if hasattr(response, "output_files"):
            for f in response.output_files:
                fid = getattr(f, "id", None) or getattr(f, "file_id", None)
                if fid:
                    annotations.append({
                        "type": "file_path",
                        "file_id": fid,
                        "text": getattr(f, "filename", ""),
                        "filename": getattr(f, "filename", None) or getattr(f, "path", None),
                        "path": getattr(f, "path", None) or getattr(f, "filepath", None),
                        "mime_type": getattr(f, "mime_type", None) or getattr(f, "content_type", None),
                        "response_id": response_id,
                        "container_id": current_container_id,
                    })

        return "".join(text_chunks), annotations


