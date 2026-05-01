from storage import UsernameStorage


def make_storage(tmp_path):
    return UsernameStorage(str(tmp_path / "usernames.sqlite"))


def seed_score(storage, username, score=8.0, batch_num=1):
    assert storage.save_scores(
        username=username,
        readability=score,
        brandability=score,
        meaning=score,
        rarity=score,
        total_score=score,
        generation_type="brandable",
        batch_num=batch_num,
    )


def test_storage_records_statuses_queries_and_stats(tmp_path):
    storage = make_storage(tmp_path)
    assert storage.add_batch(1, 3, "mixed")
    assert storage.add_batch_usernames(
        1,
        ["noria", "lumen", "velon"],
        {"noria": "brandable", "lumen": "multilingual", "velon": "brandable"},
    ) == 3

    seed_score(storage, "noria", 9.1)
    seed_score(storage, "lumen", 8.2)
    seed_score(storage, "velon", 7.3)

    assert storage.add_checked_username("noria", True, score=9.1, status="available", batch_num=1)
    assert storage.add_checked_username("velon", False, score=7.3, status="checked_taken", batch_num=1)

    available = storage.get_available_by_score(limit=10)
    assert [row["username"] for row in available] == ["noria"]
    assert available[0]["status"] == "available"

    unchecked = storage.get_username_records(status="unchecked", valid_only=True)
    assert [row["username"] for row in unchecked] == ["lumen"]

    taken_invalid = storage.get_username_records(status="taken_invalid")
    assert [row["username"] for row in taken_invalid] == ["velon"]

    stats = storage.get_stats()
    assert stats["total_evaluated"] == 3
    assert stats["total_checked"] == 2
    assert stats["total_available"] == 1
    assert stats["total_taken_invalid"] == 1
    assert stats["total_unchecked"] == 1
    assert stats["total_batches"] == 1
    assert stats["last_batch_num"] == 1
    assert stats["last_batch_count"] == 3
    assert stats["last_batch_checked"] == 2
    assert stats["last_batch_available"] == 1


def test_add_checked_username_updates_existing_status(tmp_path):
    storage = make_storage(tmp_path)

    assert storage.add_checked_username("noria", False, score=5.0, status="checked_taken")
    assert storage.get_username_record("noria")["status"] == "checked_taken"

    assert storage.add_checked_username("noria", True, score=8.5, status="available")
    record = storage.get_username_record("noria")
    assert record["status"] == "available"
    assert storage.is_username_checked("noria")


def test_check_candidates_prefers_unchecked_last_batch(tmp_path):
    storage = make_storage(tmp_path)
    assert storage.add_batch(1, 1, "mixed")
    assert storage.add_batch(2, 2, "mixed")
    assert storage.add_batch_usernames(1, ["noria"]) == 1
    assert storage.add_batch_usernames(2, ["lumen", "miran"]) == 2

    seed_score(storage, "noria", 9.0, batch_num=1)
    seed_score(storage, "lumen", 8.0, batch_num=2)
    seed_score(storage, "miran", 5.5, batch_num=2)

    candidates, source = storage.get_check_candidates(min_score=6.0, limit=10)

    assert source == "last_batch"
    assert [row["username"] for row in candidates] == ["lumen"]
