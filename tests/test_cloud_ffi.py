"""Regressions for host binding results that to_py leaves as proxies.

These are native doubles; the real workerd smoke remains the integration gate.
"""
import json
import sys
from types import SimpleNamespace
import pytest
from cloud_adapter.d1 import native


class HostResult:
    def __init__(self, value):
        self.value = value

    def to_py(self):
        return self  # Behavior seen for host/non-plain JavaScript objects.


@pytest.mark.parametrize('value', [None, True, 7, 'text', [], {'success': True}])
def test_native_values_do_not_need_js(value):
    assert native(value) is value


@pytest.mark.parametrize('value', [
    {'success': True},
    {'success': False},
    {'success': True, 'results': [{'id': 1, 'empty': None, 'cp': '0410'}]},
    [{'success': True, 'results': []}, {'success': True, 'results': [{'id': 2}]}],
])
def test_host_results_materialize_json(value, monkeypatch):
    obj = HostResult(value)
    assert obj.to_py() is obj
    monkeypatch.setitem(sys.modules, 'js', SimpleNamespace(JSON=SimpleNamespace(
        stringify=lambda candidate: json.dumps(candidate.value))))
    result = native(obj)
    assert result == value
    assert type(result) is type(value)
    if isinstance(result, dict):
        assert result.get('success') == value['success']


def test_non_json_result_rejected(monkeypatch):
    monkeypatch.setitem(sys.modules, 'js', SimpleNamespace(JSON=SimpleNamespace(stringify=lambda _: None)))
    with pytest.raises(TypeError, match='not JSON serializable'):
        native(HostResult(object()))
