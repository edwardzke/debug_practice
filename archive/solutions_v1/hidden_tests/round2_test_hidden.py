"""Hidden test for the BRIEF.md bug report (decorated functions lose identity)."""
from svcutils import retry


def test_retry_preserves_metadata():
    @retry()
    def fetch_labels(batch_id):
        """Fetch labels for a batch."""
        return batch_id

    assert fetch_labels.__name__ == "fetch_labels"
    assert fetch_labels.__doc__ == "Fetch labels for a batch."
    assert fetch_labels.__wrapped__ is not None
