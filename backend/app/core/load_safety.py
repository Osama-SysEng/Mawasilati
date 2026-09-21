from urllib.parse import urlparse


def assert_safe_target(url: str, allow_remote: bool) -> None:
    if urlparse(url).hostname not in {'localhost', '127.0.0.1', '::1'} and not allow_remote:
        raise ValueError('Remote target requires --allow-remote and an approved staging window')
