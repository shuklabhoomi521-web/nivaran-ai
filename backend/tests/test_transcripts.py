from app.voice.transcripts import load, save


def test_transcript_is_encrypted_on_disk_and_secrets_are_removed(tmp_path):
    key = tmp_path / "key"
    p = save("CA123", [{"who": "agent", "text": "Please confirm your card 4111 1111 1111 1111", "t": 1.0},
                       {"who": "ai", "text": "Hello. I am an AI assistant.", "t": 2.0}], tmp_path, key)
    raw = p.read_bytes()
    assert b"AI assistant" not in raw and b"4111" not in raw                     # unreadable without the key
    back = load("CA123", tmp_path, key)
    assert "4111" not in back["turns"][0]["text"] and back["turns"][1]["text"].startswith("Hello")


def test_call_id_cannot_escape_the_folder(tmp_path):
    p = save("../../evil", [{"who": "ai", "text": "x", "t": 0}], tmp_path, tmp_path / "k")
    assert p.parent == tmp_path
