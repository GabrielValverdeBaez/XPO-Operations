"""FFI regressions. Native doubles supplement, not replace, real workerd tests."""
import json
import sys
from types import SimpleNamespace
import pytest
from cloud_adapter.d1 import native, js_array


class HostResult:
    def __init__(self, value):
        self.value = value

    def to_py(self):
        return self


class SDKDict(dict):
    """Model workers.rpc.JsDict without importing the JS-only runtime SDK."""


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


@pytest.mark.parametrize('success', [True, False])
def test_sdk_dict_keeps_rate_limit_decision(success, monkeypatch):
    # Serializing a Python proxy as JS JSON used to turn this into {}.
    def forbidden(_):
        raise AssertionError('SDK dictionaries must not cross back into JavaScript')
    monkeypatch.setitem(sys.modules, 'js', SimpleNamespace(JSON=SimpleNamespace(stringify=forbidden)))
    result = SDKDict(success=success)
    assert native(result) is result
    assert native(result).get('success') is success


def test_sdk_d1_rows_keep_dictionary_subclasses_and_nulls():
    row = SDKDict(id=1, empty=None, cp='0410')
    result = SDKDict(success=True, results=[row])
    assert native(result)['results'][0] is row
    assert native([result])[0]['results'][0]['empty'] is None


def test_statement_list_is_left_for_sdk_rpc_conversion(monkeypatch):
    def forbidden(_):
        raise AssertionError('Manual to_js creates borrowed statement proxies')
    monkeypatch.setitem(sys.modules, 'pyodide', SimpleNamespace())
    monkeypatch.setitem(sys.modules, 'pyodide.ffi', SimpleNamespace(to_js=forbidden))
    statements = [object(), object()]
    assert js_array(statements) is statements
    assert js_array(statements)[0] is statements[0]
