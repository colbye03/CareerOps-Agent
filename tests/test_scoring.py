import pytest

from careerops.scoring import FitInputs, score_fit


def test_high_fit_role_is_apply():
    result = score_fit(
        FitInputs(
            technical_alignment=95,
            architecture_alignment=95,
            seniority_scope=90,
            domain_alignment=80,
            compensation=90,
            location=100,
            interview_probability=80,
            career_direction=95,
        )
    )

    assert result.score >= 85
    assert result.decision == "APPLY"


def test_invalid_dimension_rejected():
    with pytest.raises(ValueError):
        score_fit(
            FitInputs(
                technical_alignment=101,
                architecture_alignment=90,
                seniority_scope=90,
                domain_alignment=90,
                compensation=90,
                location=90,
                interview_probability=90,
                career_direction=90,
            )
        )
