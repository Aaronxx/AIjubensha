"""LLM API client with retry, fallback, and rate limiting."""
from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMResponse:
    raw_text: str
    model: str
    latency_ms: float
    tokens_used: int


class TokenBucket:
    """Simple token bucket rate limiter."""

    def __init__(self, rate: float, burst: int):
        self.rate = rate  # tokens per second
        self.burst = burst
        self.tokens = float(burst)
        self.last_refill = time.monotonic()

    async def acquire(self):
        while True:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_refill = now
            if self.tokens >= 1:
                self.tokens -= 1
                return
            wait = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait)


class LLMClient:
    """LLM API client with retry, timeout, and model fallback."""

    def __init__(
        self,
        primary_api_key: str | None = None,
        primary_base_url: str | None = None,
        primary_model: str | None = None,
        fallback_api_key: str | None = None,
        fallback_base_url: str | None = None,
        fallback_model: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit: float = 5.0,
        rate_burst: int = 10,
    ):
        self.primary_config = {
            "api_key": primary_api_key or os.getenv("DEEPSEEK_API_KEY", ""),
            "base_url": primary_base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            "model": primary_model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        }
        self.fallback_config = {
            "api_key": fallback_api_key or os.getenv("FALLBACK_API_KEY", ""),
            "base_url": fallback_base_url or os.getenv("FALLBACK_BASE_URL", ""),
            "model": fallback_model or os.getenv("FALLBACK_MODEL", ""),
        }
        self.timeout = timeout
        self.max_retries = max_retries
        self._bucket = TokenBucket(rate=rate_limit, burst=rate_burst)
        self._http_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self._http_client

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.8,
        max_tokens: int = 512,
    ) -> LLMResponse:
        """Send a chat request with retry and fallback support."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        return await self._call_with_retry(messages, temperature, max_tokens, use_fallback=False)

    async def _call_with_retry(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        use_fallback: bool,
    ) -> LLMResponse:
        config = self.fallback_config if use_fallback else self.primary_config
        if not config["api_key"]:
            if use_fallback:
                raise LLMError("No fallback API key configured")
            return await self._call_with_retry(messages, temperature, max_tokens, use_fallback=True)

        last_error = None
        for attempt in range(self.max_retries):
            try:
                await self._bucket.acquire()
                return await self._do_call(config, messages, temperature, max_tokens)
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait = 2 ** attempt
                    await asyncio.sleep(wait)
            except RateLimitError:
                last_error = RateLimitError("Rate limited")
                await asyncio.sleep(3.0)
            except LLMError as e:
                # Non-retryable error, try fallback immediately
                if not use_fallback and self.fallback_config["api_key"]:
                    return await self._call_with_retry(messages, temperature, max_tokens, use_fallback=True)
                raise e

        if not use_fallback and self.fallback_config["api_key"]:
            return await self._call_with_retry(messages, temperature, max_tokens, use_fallback=True)

        raise LLMError(f"All retries exhausted: {last_error}")

    async def _do_call(
        self, config: dict, messages: list[dict], temperature: float, max_tokens: int
    ) -> LLMResponse:
        url = f"{config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        start = time.monotonic()
        client = await self._get_client()
        resp = await client.post(url, json=payload, headers=headers)

        if resp.status_code == 429:
            raise RateLimitError("Rate limited")
        if resp.status_code != 200:
            raise LLMError(f"API error {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        latency_ms = (time.monotonic() - start) * 1000
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)

        return LLMResponse(
            raw_text=content,
            model=config["model"],
            latency_ms=latency_ms,
            tokens_used=tokens,
        )


class LLMError(Exception):
    pass


class RateLimitError(LLMError):
    pass
