import asyncio
import hashlib
import http.cookiejar as cookielib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
import httpx

from config import SRCHHPGUSR_COOKIES, U_COOKIES
from kelra.logger import logger


class AuthCookieEmpty(Exception):
    pass


class AuthCookieError(Exception):
    pass


class PromptRejectedError(Exception):
    pass


class BingArt:
    BASE_URL = "https://www.bing.com"

    def __init__(
        self,
        auth_cookie_u: str = U_COOKIES,
        auth_cookie_s: str = SRCHHPGUSR_COOKIES,
        cookies_netscape: Optional[Path] = Path("storage/cookies/bing/bing.txt"),
    ):
        self.timeout = httpx.Timeout(60.0)
        self.cookies_list = []

        if not auth_cookie_u or not auth_cookie_s:
            raise AuthCookieEmpty("Missing cookies for Bing Image Creator.")
        self.cookies_list.append((auth_cookie_u, auth_cookie_s))

        self.current_combo = 0
        self.cookies = self._current_cookies()

        self.headers: Dict[str, str] = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/120.0.0.0 Safari/537.36"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": f"{self.BASE_URL}/images/create",
        }

    def _current_cookies(self) -> Dict[str, str]:
        u, s = self.cookies_list[self.current_combo]
        return {"_U": u, "SRCHHPGUSR": s}

    def _rotate_cookies(self):
        self.current_combo = (self.current_combo + 1) % len(self.cookies_list)
        self.cookies = self._current_cookies()
        logger.info(f"Rotated to cookie combo #{self.current_combo + 1}")

    def _load_json_cookies(self, path: Path) -> None:
        try:
            with path.open("r", encoding="utf-8") as f:
                cookies = json.load(f)
            self.cookies_list = [(c["auth_cookie_u"], c["auth_cookie_srchhpgusr"]) for c in cookies if "auth_cookie_u" in c and "auth_cookie_srchhpgusr" in c]
            if not self.cookies_list:
                raise AuthCookieEmpty("No valid cookies in JSON file.")
        except Exception as e:
            raise AuthCookieError(f"Failed to load JSON cookies: {e}")

    def _load_netscape_cookies(self, path: Path) -> None:
        jar = cookielib.MozillaCookieJar()
        try:
            jar.load(str(path), ignore_discard=True, ignore_expires=True)
        except Exception as e:
            raise AuthCookieError(f"Netscape cookie load error: {e}")

        cookies = {c.name: c.value for c in jar if c.domain.endswith("bing.com")}
        if "_U" not in cookies or "SRCHHPGUSR" not in cookies:
            raise AuthCookieError("Missing _U or SRCHHPGUSR in Netscape cookies")
        self.cookies_list.append((cookies["_U"], cookies["SRCHHPGUSR"]))

    async def generate_images(self, prompt: str, timeout: float = 200.0, max_images: int = 4, max_try: int = 5) -> List[str]:
        async with httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=False,
        ) as client:
            for attempt in range(max_try):
                try:
                    logger.info(f"[Attempt {attempt + 1}] Submitting prompt: {prompt}")
                    client.cookies = self.cookies
                    redirect = await self._submit_prompt(client, prompt)

                    if not redirect:
                        logger.warning("No redirect returned by Bing.")
                        if len(self.cookies_list) > 1:
                            self._rotate_cookies()
                        await asyncio.sleep(1)
                        continue

                    result_id = redirect.split("id=")[-1].split("&")[0]
                    results_url = f"{self.BASE_URL}/images/create/async/results/{result_id}?q={prompt}"

                    async for html in self._wait_for_results(client, results_url, int(timeout)):
                        images = self._extract_image_urls(html)
                        if not images:
                            logger.debug("Received HTML but no images found.")
                            continue
                        logger.info(f"Found {len(images)} image(s). Saving max {max_images}.")
                        unique_images = list(dict.fromkeys(images))
                        return await self.save(unique_images[:max_images])

                except TimeoutError as te:
                    logger.warning(f"[Attempt {attempt + 1}] Timeout: {te}")
                except Exception as e:
                    logger.error(f"[Attempt {attempt + 1}] Unexpected error: {e}")

                if len(self.cookies_list) > 1:
                    self._rotate_cookies()
                await asyncio.sleep(1)
        return []

    async def _submit_prompt(self, client: httpx.AsyncClient, prompt: str) -> Optional[str]:
        try:
            resp = await client.post(
                f"{self.BASE_URL}/images/create?q={prompt}&rt=3&FORM=GUH2CR",
                data={"q": prompt, "qs": "ds"},
            )
            if resp.status_code == 302:
                return resp.headers.get("Location")
            else:
                logger.debug(f"No redirect. Status: {resp.status_code}")
                logger.debug(f"Headers: {resp.headers}")
                logger.debug(f"Body (truncated): {resp.text[:500]}")
                return None
        except httpx.RequestError as e:
            logger.error(f"Prompt submission error: {e}")
            return None

    async def _wait_for_results(self, client: httpx.AsyncClient, url: str, timeout: int):
        elapsed = 0
        while elapsed < timeout:
            response = await client.get(url)
            if response.status_code == 200 and response.text and "errorMessage" not in response.text:
                yield response.text
                return
            await asyncio.sleep(1)
            elapsed += 1
        raise TimeoutError(f"No results within {timeout} seconds.")

    def _extract_image_urls(self, html: str) -> List[str]:
        return ["https://tse" + link.split("?w=")[0] for link in re.findall(r'src="https://tse([^\"]+)', html)]

    async def save(self, images: List[str], output_dir: str = "downloads") -> List[str]:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        seen, saved = set(), []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for idx, url in enumerate(images, 1):
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    img_hash = hashlib.md5(resp.content).hexdigest()
                    if img_hash in seen:
                        logger.info(f"Duplicate skipped: {url}")
                        continue
                    seen.add(img_hash)
                    file_path = output_path / f"image_{idx}.jpeg"
                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(resp.content)
                    saved.append(str(file_path))
                except Exception as e:
                    logger.warning(f"Failed to save {url}: {e}")
        return saved
