from backend.app.kgbase.api.v1.kgbase.knowledge_graph import _safe_question_error


class WrappedProviderError(Exception):
    status_code = 500


class ProviderResponse:
    status_code = 401


class NestedProviderError(Exception):
    status_code = 500
    response = ProviderResponse()


def test_wrapped_invalid_token_is_sanitized() -> None:
    status_code, message = _safe_question_error(
        WrappedProviderError("500: Error code: 401 - {'message': '无效的令牌', 'request id': 'secret'}")
    )

    assert status_code == 401
    assert message == '当前模型凭据无效，请到个人中心重新配置 API Key'
    assert 'request id' not in message


def test_unknown_provider_error_does_not_leak_original_response() -> None:
    status_code, message = _safe_question_error(Exception('provider returned private diagnostic data'))

    assert status_code == 500
    assert message == '问答处理失败，请检查模型配置或稍后重试'


def test_nested_401_status_takes_priority_over_wrapper_status() -> None:
    status_code, message = _safe_question_error(NestedProviderError('authentication failed'))

    assert status_code == 401
    assert message == '当前模型凭据无效，请到个人中心重新配置 API Key'
