import pytest

from area_lab.domain.errors import PipelineFailure
from area_lab.infrastructure.designs import DESIGNS
from area_lab.infrastructure.validation import VECTOR_COUNT, check_rtl_results, write_vectors


def profile(identifier):
    return next(design for design in DESIGNS if design.id == identifier)


def test_int32_reference_rejects_a_wrong_signed_result(tmp_path):
    design = profile("int16_32")
    stimulus = "FFFF 0000 0000 0000 0001 0000 0000 0000 00000000"
    (tmp_path / "stimuli.txt").write_text((stimulus + "\n") * VECTOR_COUNT)
    # Signed -1 times 1 must be FFFFFFFF, not the unsigned product 0000FFFF.
    (tmp_path / "rtl-results.txt").write_text("0000FFFF\n" * VECTOR_COUNT)
    with pytest.raises(PipelineFailure, match="referencia entera"):
        check_rtl_results(tmp_path, design)
    assert not (tmp_path / "vectors.txt").exists()
    (tmp_path / "rtl-results.txt").write_text("FFFFFFFF\n" * VECTOR_COUNT)
    check_rtl_results(tmp_path, design)
    assert (tmp_path / "vectors.txt").read_text().splitlines()[0].endswith("FFFFFFFF")


@pytest.mark.parametrize("results", ["XXXX\n" * VECTOR_COUNT, "0000\n"])
def test_noninteger_oracle_rejects_undefined_or_incomplete_results(tmp_path, results):
    design = profile("fp16")
    write_vectors(tmp_path, design)
    (tmp_path / "rtl-results.txt").write_text(results)
    with pytest.raises(PipelineFailure):
        check_rtl_results(tmp_path, design)
    assert not (tmp_path / "vectors.txt").exists()


def test_lns_corpus_exercises_finite_values_instead_of_only_exceptions(tmp_path):
    write_vectors(tmp_path, profile("lns16"))
    finite = 0
    for line in (tmp_path / "stimuli.txt").read_text().splitlines():
        words = [int(word, 16) for word in line.split()]
        logs = [((word & 0x1FFF) ^ 0x1000) - 0x1000 for word in words]
        if all(word >> 14 == 1 for word in words) and all(abs(log) <= 1024 for log in logs):
            finite += 1
    assert finite >= 100
