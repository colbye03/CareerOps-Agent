import copy
import json
from importlib.resources import files

import pytest
from jsonschema import ValidationError

from careerops.engine import normalize, run, tailor
from careerops.models import starter, validate
from careerops.storage import record_event


def inputs(persona='data-cloud-architect'):
    p = starter('personas', persona)
    packs = {path.stem: json.loads(path.read_text()) for path in files('careerops').joinpath('resources/role-packs').iterdir()}
    return starter('jobs', 'demo'), p['profile'], p['evidence'], packs


def test_all_nine_packs_validate():
    _, _, _, packs = inputs()
    assert len(packs) == 9
    for pack in packs.values():
        validate('role-pack', pack)


def test_pipeline_counts_and_exclusions():
    report = run(*inputs())
    f = report['funnel']
    assert f['raw_postings'] == 12 and f['unique_postings'] == 11
    assert f['apply'] + f['maybe'] + f['skip'] == f['unique_postings']
    assert f['fully_evaluated'] + f['excluded'] == f['unique_postings']
    low = next(r for r in report['results'] if r['job'].get('requisition_id') == 'LOW-SALARY')
    assert low['exclusion'] == 'compensation_below_floor' and low['score'] is None


def test_same_job_different_candidates():
    scores = []
    for name in ('data-cloud-architect', 'technical-program-manager', 'infrastructure-architect'):
        result = next(r for r in run(*inputs(name))['results'] if r['job'].get('requisition_id') == 'SHARED-1')
        scores.append(result['score'])
    assert len(set(scores)) == 3


def test_unverified_evidence_never_becomes_resume_claim():
    jobs, profile, evidence, packs = inputs()
    for item in evidence:
        item['verified'] = False
    result = run([jobs[0]], profile, evidence, packs)['results'][0]
    assert result['score'] == 0 and result['decision'] == 'SKIP'
    assert 'Synthetic project demonstrated' not in tailor(result)


def test_profile_skills_are_not_verified_evidence():
    jobs, profile, _, packs = inputs()
    profile['skills'] = [t for d in packs['data-platform-architect']['dimensions'] for t in d['terms']]
    result = run([jobs[0]], profile, [], packs)['results'][0]
    assert result['score'] == 25
    assert all(not d['evidence'] for d in result['dimensions'])


def test_pack_extensibility_without_engine_edits():
    jobs, profile, evidence, packs = inputs()
    pack = {'schema_version': 1, 'id': 'custom', 'name': 'Custom', 'title_aliases': ['custom role'],
            'dimensions': [{'id': 'communication', 'terms': ['communication'], 'weight': 1, 'required_level': 3}]}
    packs['custom'] = pack
    profile['role_packs'] = ['custom']
    jobs[0]['title'] = 'Custom Role'
    jobs[0]['description'] = 'communication'
    assert run([jobs[0]], profile, evidence, packs)['results'][0]['role_pack'] == 'custom'


def test_unknown_requirements_require_review_not_apply():
    jobs, profile, evidence, packs = inputs()
    jobs[0]['description'] = 'Unrecognized responsibilities'
    result = run([jobs[0]], profile, evidence, packs)['results'][0]
    assert result['decision'] == 'MAYBE' and result['warnings']


@pytest.mark.parametrize('change,reason', [({'work_mode': 'onsite'}, 'work_mode'), ({'clearance': 'SECRET'}, 'clearance_not_held')])
def test_hard_exclusions(change, reason):
    jobs, profile, evidence, packs = inputs()
    jobs[0].update(change)
    assert run([jobs[0]], profile, evidence, packs)['results'][0]['exclusion'] == reason


def test_exact_application_excludes_only_that_job():
    jobs, profile, evidence, packs = inputs()
    second = dict(jobs[0], requisition_id='NEW-REQ')
    ledger = []
    record_event(ledger, normalize(jobs[0])['id'], 'applied', 'user_confirmed')
    results = run([jobs[0], second], profile, evidence, packs, ledger)['results']
    assert sum(r['exclusion'] == 'existing_application' for r in results) == 1


def test_communication_reconciliation_is_idempotent_and_authoritative():
    ledger = []
    record_event(ledger, 'test', 'interviewing', 'recruiter', '2026-01-01T00:00:00+00:00')
    for _ in range(2):
        record_event(ledger, 'test', 'rejected', 'employer_email', '2026-01-02T00:00:00+00:00')
    assert ledger[0]['status'] == 'interviewing'
    assert len(ledger[0]['events']) == 2
    with pytest.raises(ValueError):
        record_event(ledger, 'test', 'applied', 'recruiter', '2026-01-01T00:00:00')


def test_invalid_config_fails_explicitly():
    jobs, profile, evidence, packs = inputs()
    packs['data-platform-architect']['dimensions'][0]['weight'] = .8
    with pytest.raises(ValueError, match='weights'):
        run(jobs, profile, evidence, packs)
    with pytest.raises(ValidationError):
        validate('candidate', {'id': 'bad'})
    evidence.append(copy.deepcopy(evidence[0]))
    with pytest.raises(ValueError, match='unique'):
        validate('evidence', evidence)


def test_public_schemas_match_packaged_contracts():
    from pathlib import Path
    for resource in files('careerops').joinpath('resources/schemas').iterdir():
        assert json.loads(resource.read_text()) == json.loads(Path('schemas', resource.stem + '.schema.json').read_text())


def test_no_cross_candidate_evidence_leak():
    _, profile, evidence, packs = inputs('technical-program-manager')
    report = run(*inputs('technical-program-manager'))
    ids = {e['id'] for e in evidence}
    assert all(h['evidence_id'] in ids for r in report['results'] for d in r['dimensions'] for h in d['evidence'])


def test_known_salary_currency_constraint():
    jobs, profile, evidence, packs = inputs()
    profile['hard_exclusions']['require_known_salary'] = True
    jobs[0]['salary']['currency'] = 'EUR'
    assert run([jobs[0]], profile, evidence, packs)['results'][0]['exclusion'] == 'compensation_unknown_or_currency_mismatch'


def test_retriever_cannot_inject_resume_facts():
    class UntrustedRetriever:
        def retrieve(self, terms, evidence):
            return [{'evidence_id': 'invented', 'matched_terms': terms, 'summary': 'Fabricated claim'},
                    {'evidence_id': evidence[0]['id'], 'matched_terms': terms, 'summary': 'Fabricated claim', 'level': 5}]
    jobs, profile, evidence, packs = inputs()
    result = run([jobs[0]], profile, evidence, packs, retriever=UntrustedRetriever())['results'][0]
    assert 'Fabricated claim' not in tailor(result)
    assert all(h['level'] == evidence[0]['level'] for d in result['dimensions'] for h in d['evidence'])


def test_insufficient_proficiency_creates_gap():
    jobs, profile, evidence, packs = inputs()
    for e in evidence:
        e['level'] = 1
    result = run([jobs[0]], profile, evidence, packs)['results'][0]
    assert result['score'] == 33.33
    assert all(d['gaps'] for d in result['dimensions'])
