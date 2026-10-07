import json
from careerops.cli import main


def invoke(path, *args):
    return main(['--workspace', str(path), *args])


def test_end_to_end_cli(tmp_path, capsys):
    workspace = tmp_path / 'private'
    assert invoke(workspace, 'init') == 0
    assert invoke(workspace, 'init') == 2
    assert invoke(workspace, 'run') == 0
    report = json.loads((workspace / 'report.json').read_text())
    target = next(r for r in report['results'] if r['decision'] == 'APPLY')
    job_id = target['job']['id']
    assert invoke(workspace, 'jobs') == 0
    assert invoke(workspace, 'explain', job_id) == 0
    assert invoke(workspace, 'resume', job_id) == 0
    draft = (workspace / 'resumes' / f'{job_id}.md').read_text()
    assert '[evidence:' in draft
    assert json.loads((workspace / 'ledger.json').read_text()) == []
    assert invoke(workspace, 'ledger', '--job-id', job_id, '--status', 'applied') == 0
    assert invoke(workspace, 'run') == 0
    assert invoke(workspace, 'resume', job_id) == 2
    assert invoke(workspace, 'ledger') == 0


def test_resume_refreshes_removed_evidence(tmp_path):
    w = tmp_path / 'private'
    invoke(w, 'init')
    invoke(w, 'run')
    report = json.loads((w / 'report.json').read_text())
    target = next(r for r in report['results'] if r['decision'] == 'APPLY')
    (w / 'evidence.json').write_text('[]')
    assert invoke(w, 'resume', target['job']['id']) == 0
    assert 'Synthetic project demonstrated' not in (w / 'resumes' / f"{target['job']['id']}.md").read_text()


def test_event_import_and_errors(tmp_path):
    w = tmp_path / 'private'
    invoke(w, 'init', '--persona', 'technical-program-manager')
    events = tmp_path / 'events.json'
    events.write_text(json.dumps([{'job_id': 'demo', 'status': 'interviewing', 'source': 'employer_portal', 'observed_at': '2026-01-01T00:00:00+00:00'}]))
    assert invoke(w, 'ledger', '--events', str(events)) == 0
    assert invoke(w, 'ledger', '--job-id', 'demo') == 2
    assert invoke(w, 'ledger', '--job-id', 'demo', '--status', 'invented') == 2
    assert invoke(w, 'run', '--jobs', str(tmp_path / 'missing.json')) == 2
