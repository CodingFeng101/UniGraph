import unittest

from backend.app.kgbase.api.v1.kgbase.knowledge_graph import merge_async_generators
from backend.app.kgbase.service.knowledge_graph_service import resolve_local_file_path
from backend.common.security.outbound_url import validate_outbound_http_url
from backend.common.security.secret_store import decrypt_secret, encrypt_secret


class ReleaseHardeningTests(unittest.IsolatedAsyncioTestCase):
    async def test_stream_merger_finishes_after_all_generators(self):
        async def generate(*values):
            for value in values:
                yield value

        result = [item async for item in merge_async_generators(generate('a', 'b'), generate('c'))]
        self.assertCountEqual(result, ['a', 'b', 'c'])

    async def test_private_model_endpoint_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Private or local'):
            await validate_outbound_http_url('http://127.0.0.1:11434/v1')

    async def test_model_endpoint_rejects_embedded_credentials(self):
        with self.assertRaisesRegex(ValueError, 'must not contain credentials'):
            await validate_outbound_http_url('https://user:password@example.com/v1')

    def test_uploaded_file_resolver_rejects_unmanaged_paths(self):
        with self.assertRaisesRegex(FileNotFoundError, 'path is invalid'):
            resolve_local_file_path('../backend/.env')

    def test_model_api_keys_are_encrypted_at_rest(self):
        encrypted = encrypt_secret('test-api-key')
        self.assertTrue(encrypted.startswith('enc:v1:'))
        self.assertNotIn('test-api-key', encrypted)
        self.assertEqual(decrypt_secret(encrypted), 'test-api-key')
