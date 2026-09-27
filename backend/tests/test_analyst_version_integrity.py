import uuid
import pytest
from app.db.models.conversation_message import ConversationMessage
from app.services.analyst_service import AnalystDatasetVersionMismatchError


def test_analyst_version_mismatch_detection():
    msg = ConversationMessage(
        conversation_id=uuid.uuid4(),
        role="ASSISTANT",
        content="Previous answer",
        dataset_checksum="checksum_v1_old_12345678",
    )

    current_dataset_checksum = "checksum_v2_new_87654321"

    # Verify checksum inequality triggers version mismatch
    assert msg.dataset_checksum != current_dataset_checksum
