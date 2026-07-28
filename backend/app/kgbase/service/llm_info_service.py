import logging

import httpx
from fastapi import HTTPException

from backend.core.conf import settings

logger = logging.getLogger(__name__)


async def fetch_info(user_token, url):
    headers = {'Authorization': f'Bearer {user_token}'}

    logger.debug(f'Fetching user LLM info from {url} with token: {user_token[:10]}...')

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # 抛出 HTTP 错误（如 4xx, 5xx）

            user_info = response.json()
            data = user_info.get('data', {})
            model = data.get('model', '')

            if not model:
                logger.error('No LLM models found for user')
                raise HTTPException(status_code=400, detail='模型为空')

            api_key = data.get('api_key')
            api_url = data.get('base_url')
            print(api_url)

            logger.info('Successfully fetched user LLM info')
            return api_key, api_url, model

        except httpx.HTTPStatusError as e:
            logger.error(f'HTTP status error: {e.response.status_code} - {e}')
            raise  # 抛出原始异常
        except httpx.RequestError as e:
            logger.error(f'HTTP request error: {e}')
            raise  # 抛出原始异常（如 ConnectError）
        except httpx.HTTPError as e:
            logger.error(f'General HTTP error: {e}')
            raise  # 捕获其他 HTTP 错误
        except Exception as e:
            logger.error(f'Unexpected error in get_user_llm_info: {e}')
            raise  # 抛出未预期的异常


async def _get_legacy_user_llm_info(user_token: str):
    """
    通过 user_token 查询用户的 api-key
    :param user_token: 用户 user_token
    :return: (api_key, api_url, model_name) 或抛出异常
    """
    url = settings.SSO_USER_INFO_URL  # 获取单点登录用户信息的 URL
    # 尝试使用门户sso
    try:
        return await fetch_info(user_token, url)
    except httpx.HTTPStatusError:
        return await fetch_info(user_token, 'https://data.jxselab.com/knowg/v1/sys/users/me')


async def get_user_llm_info(user_token: str):
    """Return the first active LLM configured in the user's model settings."""
    url = settings.SSO_USER_INFO_URL
    headers = {'Authorization': f'Bearer {user_token}'}
    api_root = url.rsplit('/sys/users/me', 1)[0]

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f'{api_root}/llm/provider/all', headers=headers)
        response.raise_for_status()
        for provider in response.json().get('data', []):
            if provider.get('status') != 1 or not provider.get('api_key') or not provider.get('api_url'):
                continue
            detail_response = await client.get(
                f'{api_root}/llm/provider/{provider["uuid"]}/detail',
                headers=headers,
            )
            detail_response.raise_for_status()
            detail = detail_response.json().get('data', {})
            model = next(
                (item for item in detail.get('models', []) if item.get('type') == 'llm' and item.get('status') == 1),
                None,
            )
            if model:
                return detail['api_key'], detail['api_url'], model['name']

    return await _get_legacy_user_llm_info(user_token)
