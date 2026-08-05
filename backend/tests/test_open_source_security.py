import ast
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKIPPED_DIRS = {
    '.git',
    '.cache',
    '.venv',
    '.run-venv.local',
    'node_modules',
    'dist',
    'var',
    '__pycache__',
}


def read_source(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding='utf-8-sig')


def find_async_function(tree: ast.AST, name: str) -> ast.AsyncFunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name:
            return node
    raise AssertionError(f'Async function {name!r} was not found')


def route_decorator(function: ast.AsyncFunctionDef, method: str, path: str) -> ast.Call:
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
            continue
        if decorator.func.attr != method or not decorator.args:
            continue
        value = decorator.args[0]
        if isinstance(value, ast.Constant) and value.value == path:
            return decorator
    raise AssertionError(f'{method.upper()} route {path!r} was not found')


def dependency_names(decorator: ast.Call) -> set[str]:
    for keyword in decorator.keywords:
        if keyword.arg != 'dependencies' or not isinstance(keyword.value, (ast.List, ast.Tuple)):
            continue
        return {item.id for item in keyword.value.elts if isinstance(item, ast.Name)}
    return set()


class OpenSourceSecurityTests(unittest.TestCase):
    def test_sensitive_runtime_files_are_not_tracked(self):
        if not (REPO_ROOT / '.git').exists():
            self.skipTest('Git metadata is unavailable in this source archive')
        sensitive_paths = [
            'backend/.env',
            'backend/.env.dev',
            'backend/.env.prod',
            'var/log/fba_access.log',
            'var/log/fba_error.log',
            'frontend/Apache/privkey.key',
            'frontend/IIS/fullchain.pfx',
            'frontend/IIS/password.txt',
        ]
        tracked = set(
            subprocess.run(
                ['git', '-C', str(REPO_ROOT), 'ls-files'],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
        )
        self.assertEqual([path for path in sensitive_paths if path in tracked], [])

    def test_required_open_source_documents_exist(self):
        required = [
            'README.md',
            'LICENSE',
            'SECURITY.md',
            'CONTRIBUTING.md',
            'THIRD_PARTY_NOTICES.md',
        ]
        missing = [path for path in required if not (REPO_ROOT / path).is_file()]
        self.assertEqual(missing, [])

    def test_model_key_probe_is_authenticated_post(self):
        tree = ast.parse(read_source('backend/app/admin/api/v1/llm/model_routers.py'))
        function = find_async_function(tree, 'test_api_key')
        decorator = route_decorator(function, 'post', '/test')
        self.assertIn('DependsJwtAuth', dependency_names(decorator))

    def test_upload_is_authenticated_and_bounded(self):
        source = read_source('backend/app/file/file.py')
        tree = ast.parse(source)
        function = find_async_function(tree, 'upload_file')
        decorator = route_decorator(function, 'post', '/upload')
        self.assertIn('DependsJwtAuth', dependency_names(decorator))
        self.assertIn('MAX_UPLOAD_SIZE = 50 * 1024 * 1024', source)
        self.assertIn('MAX_IMAGE_UPLOAD_SIZE = 5 * 1024 * 1024', source)
        self.assertIn("filename in {'.', '..'}", source)
        self.assertIn('ALLOWED_EXTENSIONS', source)
        self.assertIn('image.verify()', source)

    def test_raw_upload_directories_are_not_publicly_mounted(self):
        source = read_source('backend/core/registrar.py')
        self.assertNotIn("app.mount('/static'", source)
        self.assertNotIn("app.mount('/files'", source)

    def test_auth_encryption_key_is_not_hard_coded_in_source(self):
        frontend_source = read_source('frontend/src/api/runtime/config.js')
        backend_source = read_source('backend/app/admin/service/auth_service.py')
        self.assertIn('VITE_AUTH_AES_SECRET_KEY', frontend_source)
        self.assertIn('settings.AUTH_AES_SECRET_KEY', backend_source)
        self.assertNotIn('G8ZyYyZ0Xf5x5f6uZrwf6ft4gD0pniYAkHp/Y6f4Pv4=', frontend_source + backend_source)

    def test_arbitrary_llm_provider_creation_route_is_not_mounted(self):
        source = read_source('backend/app/admin/api/v1/llm/__init__.py')
        self.assertNotIn('creater_router', source)

    def test_legacy_sso_login_bypass_is_not_mounted(self):
        source = read_source('backend/app/admin/api/v1/auth/__init__.py')
        self.assertNotIn('sso_router', source)

    def test_public_registration_does_not_grant_admin_permissions(self):
        source = read_source('backend/app/admin/crud/crud_user.py')
        self.assertNotIn("dict_obj.update({'is_superuser': True})", source)
        self.assertIn("'is_superuser': False", source)

    def test_profile_updates_enforce_resource_owner(self):
        source = read_source('backend/app/admin/service/user_service.py')
        self.assertGreaterEqual(source.count('request.user.username != username'), 2)

    def test_model_api_keys_are_not_returned_to_the_browser(self):
        source = read_source('backend/app/admin/schema/llm_provider_schema.py')
        self.assertGreaterEqual(source.count("self.api_key = '********' if self.api_key else ''"), 2)

    def test_production_openapi_is_disabled(self):
        source = read_source('backend/core/conf.py')
        for setting in ('FASTAPI_DOCS_URL', 'FASTAPI_REDOCS_URL', 'FASTAPI_OPENAPI_URL'):
            self.assertRegex(source, rf"values\[['\"]{setting}['\"]\]\s*=\s*None")

    def test_error_logging_does_not_dump_local_variables(self):
        source = read_source('backend/common/log.py')
        self.assertNotIn("'diagnose': True", source)
        self.assertNotIn('diagnose=True', source)
        self.assertNotIn('backtrace=True', source)

    def test_unhandled_exceptions_are_not_returned_to_clients(self):
        source = read_source('backend/common/exception/exception_handler.py')
        self.assertNotIn("'msg': str(exc)", source)
        self.assertIn("'msg': '服务暂时不可用，请稍后重试'", source)

    def test_registration_maps_database_conflicts_to_business_errors(self):
        source = read_source('backend/app/admin/service/auth_service.py')
        self.assertIn('await db.flush()', source)
        self.assertIn('except IntegrityError as exc:', source)
        self.assertIn("msg='用户名、邮箱或昵称已存在'", source)

    def test_source_tree_has_no_high_confidence_secrets(self):
        patterns = [
            re.compile(r'sk-[A-Za-z0-9_-]{20,}'),
            re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}'),
            re.compile(r'AKIA[0-9A-Z]{16}'),
            re.compile('-----BEGIN ' + r'(?:RSA |EC |OPENSSH )?' + 'PRIVATE KEY-----'),
        ]
        findings = []
        for path in REPO_ROOT.rglob('*'):
            if not path.is_file() or any(part in SKIPPED_DIRS for part in path.parts):
                continue
            if path.suffix.lower() in {'.crt', '.gif', '.ico', '.jpeg', '.jpg', '.png', '.ttf', '.woff', '.woff2'}:
                continue
            if path.stat().st_size > 5 * 1024 * 1024:
                continue
            try:
                content = path.read_text(encoding='utf-8-sig')
            except UnicodeDecodeError:
                continue
            if any(pattern.search(content) for pattern in patterns):
                findings.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(findings, [])


if __name__ == '__main__':
    unittest.main()
