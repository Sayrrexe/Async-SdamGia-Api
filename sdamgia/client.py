"""Main API client for sdamgia.ru."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Any
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup
import httpx

from sdamgia import images
from sdamgia.parsers import _CatalogParser, _extract_problem_ids, _ProblemParser
from sdamgia.rendering import _ProblemImageRenderer


class SdamGIA:
    """Client for interacting with educational portal sdamgia.ru."""

    def __init__(
        self,
        timeout_seconds: float = 20.0,
        retries: int = 2,
        retry_base_delay_seconds: float = 1.0,
        user_agent: str = "sdamgia-api/async",
    ) -> None:
        """Initialize API client with default subjects and tool settings.

        Args:
            timeout_seconds: Request timeout for all HTTP calls.
            retries: Number of retry attempts after the first request.
            retry_base_delay_seconds: Linear backoff base for retries.
            user_agent: User-Agent header for outgoing requests.

        Returns:
            None.
        """
        base_domain = "sdamgia.ru"
        self._subject_base_url = {
            "math": f"https://math-ege.{base_domain}",
            "mathb": f"https://mathb-ege.{base_domain}",
            "phys": f"https://phys-ege.{base_domain}",
            "inf": f"https://inf-ege.{base_domain}",
            "rus": f"https://rus-ege.{base_domain}",
            "bio": f"https://bio-ege.{base_domain}",
            "en": f"https://en-ege.{base_domain}",
            "chem": f"https://chem-ege.{base_domain}",
            "geo": f"https://geo-ege.{base_domain}",
            "soc": f"https://soc-ege.{base_domain}",
            "de": f"https://de-ege.{base_domain}",
            "fr": f"https://fr-ege.{base_domain}",
            "lit": f"https://lit-ege.{base_domain}",
            "sp": f"https://sp-ege.{base_domain}",
            "hist": f"https://hist-ege.{base_domain}",
        }
        self.tesseract_src = "tesseract"
        self.html2img_chrome_path = "chrome"
        self.grabzit_auth = {"AppKey": "grabzit", "AppSecret": "grabzit"}
        self._problem_parser = _ProblemParser()
        self._catalog_parser = _CatalogParser()
        self._renderer = _ProblemImageRenderer()
        self._timeout_seconds = timeout_seconds
        self._retries = retries
        self._retry_base_delay_seconds = retry_base_delay_seconds
        self._headers = {"User-Agent": user_agent}
        self._http_client = httpx.AsyncClient(
            timeout=self._timeout_seconds,
            headers=self._headers,
            follow_redirects=True,
        )

    async def __aenter__(self) -> SdamGIA:
        """Enter async context manager for client reuse.

        Args:
            None.

        Returns:
            Initialized client instance.
        """
        return self

    async def __aexit__(self, _exc_type: Any, _exc: Any, _tb: Any) -> None:
        """Exit async context manager and close HTTP resources.

        Args:
            _exc_type: Exception type from context manager.
            _exc: Exception instance from context manager.
            _tb: Traceback object from context manager.

        Returns:
            None.
        """
        await self.aclose()

    async def aclose(self) -> None:
        """Close underlying asynchronous HTTP client.

        Args:
            None.

        Returns:
            None.
        """
        await self._http_client.aclose()

    async def get_problem_by_id(
        self,
        subject: str,
        id: str,
        img: str | None = None,
        path_to_img: str | None = None,
        path_to_tmp_html: str = "",
    ) -> dict[str, object] | None:
        """Get problem details by ID.

        Args:
            subject: Subject short code.
            id: Problem identifier.
            img: Image backend: pyppeteer, grabzit, html2img, or None.
            path_to_img: Output image path when img is provided.
            path_to_tmp_html: Temp html folder for pyppeteer rendering.

        Returns:
            Parsed problem payload or None if problem block is missing.
        """
        subject_base_url = self._subject_base_url[subject]
        soup = await self._fetch_soup(f"{subject_base_url}/problem?id={id}")
        prob_block = soup.find("div", {"class": "prob_maindiv"})
        if prob_block is None:
            return None

        self._problem_parser.normalize_images(prob_block, subject_base_url)
        problem_url = f"{subject_base_url}/problem?id={id}"

        if img is not None:
            for info_block in prob_block.find_all("div", {"class": "minor"}):
                info_block.decompose()
            tail_blocks = prob_block.find_all("div")
            if tail_blocks:
                tail_blocks[-1].decompose()

            await self._renderer.render(
                prob_block=prob_block,
                renderer=img,
                problem_id=id,
                path_to_img=path_to_img,
                path_to_tmp_html=path_to_tmp_html,
                html2img_chrome_path=self.html2img_chrome_path,
                grabzit_auth=self.grabzit_auth,
            )

        return self._problem_parser.parse_problem(prob_block, id, problem_url)

    async def search(self, subject: str, request: str, page: int = 1) -> list[str]:
        """Search problem IDs by text query.

        Args:
            subject: Subject short code.
            request: Search phrase.
            page: Search page number.

        Returns:
            List of problem identifiers.
        """
        subject_base_url = self._subject_base_url[subject]
        soup = await self._fetch_soup(f"{subject_base_url}/search?search={request}&page={page}")
        return _extract_problem_ids(soup)

    async def get_test_by_id(self, subject: str, testid: str) -> list[str]:
        """Get problem IDs from a generated test.

        Args:
            subject: Subject short code.
            testid: Test identifier.

        Returns:
            List of problem identifiers from test.
        """
        subject_base_url = self._subject_base_url[subject]
        soup = await self._fetch_soup(f"{subject_base_url}/test?id={testid}")
        return _extract_problem_ids(soup)

    async def get_category_by_id(self, subject: str, categoryid: str, page: int = 1) -> list[str]:
        """Get problem IDs from category page.

        Args:
            subject: Subject short code.
            categoryid: Category identifier.
            page: Category page number.

        Returns:
            List of problem identifiers for category.
        """
        subject_base_url = self._subject_base_url[subject]
        soup = await self._fetch_soup(
            f"{subject_base_url}/test?&filter=all&theme={categoryid}&page={page}"
        )
        return _extract_problem_ids(soup)

    async def get_catalog(self, subject: str) -> list[dict[str, object]]:
        """Get subject catalog with topics and categories.

        Args:
            subject: Subject short code.

        Returns:
            Catalog structure with topics and nested categories.
        """
        subject_base_url = self._subject_base_url[subject]
        soup = await self._fetch_soup(f"{subject_base_url}/prob_catalog")
        return self._catalog_parser.parse(soup)

    async def get_random_problem(
        self,
        subject: str,
        topic_id: str,
        period_days: int = 30,
        seed: int | None = None,
    ) -> dict[str, object] | None:
        """Get random problem for subject topic with a best-effort period filter.

        Args:
            subject: Subject short code.
            topic_id: Topic identifier (for example, "1" for task 1).
            period_days: Relative period window in days.
            seed: Optional random seed for deterministic selection.

        Returns:
            Parsed problem payload or None if no valid candidate is found.
        """
        if period_days < 1:
            raise ValueError("period_days must be >= 1")

        catalog = await self.get_catalog(subject)
        topic_exists = any(str(topic.get("topic_id")) == topic_id for topic in catalog)
        if not topic_exists:
            return None

        pages_per_category = self._resolve_pages_per_category(period_days)
        candidate_ids = await self._collect_topic_candidate_ids(subject, topic_id, pages_per_category)

        if not candidate_ids:
            fallback_pages = self._resolve_pages_per_category(365)
            candidate_ids = await self._collect_topic_candidate_ids(subject, topic_id, fallback_pages)

        if not candidate_ids:
            return None

        first_candidate = self._pick_problem_with_seed(candidate_ids, seed)
        if first_candidate is None:
            return None

        randomizer = random.Random(seed)
        remaining_ids = [problem_id for problem_id in candidate_ids if problem_id != first_candidate]
        randomizer.shuffle(remaining_ids)

        for problem_id in [first_candidate, *remaining_ids]:
            problem = await self.get_problem_by_id(subject, problem_id)
            if problem is not None:
                return problem

        return None

    async def generate_test(self, subject: str, problems: dict[Any, int] | None = None) -> str:
        """Generate test and return test ID.

        Args:
            subject: Subject short code.
            problems: Test generation map.

        Returns:
            Generated test identifier.
        """
        subject_base_url = self._subject_base_url[subject]
        if problems is None:
            problems = {"full": 1}

        if "full" in problems:
            catalog = await self.get_catalog(subject)
            levels = {f"prob{i}": problems["full"] for i in range(1, len(catalog) + 1)}
        else:
            levels = {f"prob{i}": problems[i] for i in problems}

        response = await self._request_with_retry(
            lambda: self._http_client.get(
                f"{subject_base_url}/test",
                params={"a": "generate", **levels},
                follow_redirects=False,
            ),
            allow_redirect_response=True,
        )
        location = self._extract_redirect_location(response)
        test_id = parse_qs(urlparse(location).query).get("id", [""])[0]
        if not test_id.isdigit():
            raise ValueError(f"Failed to parse generated test id from redirect: {location}")
        return test_id

    async def generate_pdf(
        self,
        subject: str,
        testid: str,
        solution: bool | str = "",
        nums: bool | str = "",
        answers: bool | str = "",
        key: bool | str = "",
        crit: bool | str = "",
        instruction: bool | str = "",
        col: str = "",
        pdf: bool | str = True,
    ) -> str:
        """Generate PDF link for test.

        Args:
            subject: Subject short code.
            testid: Test identifier.
            solution: Include solution section.
            nums: Include task numbers.
            answers: Include answers section.
            key: Include answer key.
            crit: Include criteria.
            instruction: Include instruction text.
            col: Footer text.
            pdf: PDF layout mode.

        Returns:
            Absolute URL to generated PDF.
        """
        subject_base_url = self._subject_base_url[subject]

        def normalize_flag(flag: bool | str) -> bool | str:
            if flag is False:
                return ""
            return flag

        response = await self._request_with_retry(
            lambda: self._http_client.get(
                f"{subject_base_url}/test",
                params={
                    "id": testid,
                    "print": "true",
                    "pdf": pdf,
                    "sol": normalize_flag(solution),
                    "num": normalize_flag(nums),
                    "ans": normalize_flag(answers),
                    "key": normalize_flag(key),
                    "crit": normalize_flag(crit),
                    "pre": normalize_flag(instruction),
                    "dcol": normalize_flag(col),
                },
                follow_redirects=False,
            ),
            allow_redirect_response=True,
        )
        location = self._extract_redirect_location(response)
        return urljoin(f"{subject_base_url}/", location)

    async def search_by_img(self, subject: str, path: str) -> list[str]:
        """Search problems by text recognized from image.

        Args:
            subject: Subject short code.
            path: Path to source image.

        Returns:
            List of unique problem identifiers.
        """
        subject_base_url = self._subject_base_url[subject]
        words_from_img = (
            await asyncio.to_thread(images.img_to_str, path, self.tesseract_src)
        ).split()
        result: list[str] = []
        result_lock = asyncio.Lock()
        semaphore = asyncio.Semaphore(20)

        async def parse_chunk(start_index: int) -> None:
            try:
                request_phrase = " ".join([words_from_img[index] for index in range(start_index, start_index + 10)])
            except IndexError:
                return

            try:
                async with semaphore:
                    soup = await self._fetch_soup(
                        f"{subject_base_url}/search?search={request_phrase}&page=1"
                    )
            except httpx.HTTPError:
                return

            async with result_lock:
                for problem_id in _extract_problem_ids(soup):
                    if problem_id not in result:
                        result.append(problem_id)

        await asyncio.gather(*(parse_chunk(index) for index in range(len(words_from_img))))

        return result

    def _resolve_pages_per_category(self, period_days: int) -> int:
        """Resolve how many category pages to scan for the requested period.

        Args:
            period_days: Relative period window in days.

        Returns:
            Number of pages to scan in each category.
        """
        if period_days <= 10:
            return 1
        if period_days <= 30:
            return 3
        if period_days <= 90:
            return 6
        return 10

    async def _collect_topic_candidate_ids(
        self,
        subject: str,
        topic_id: str,
        pages_per_category: int,
    ) -> list[str]:
        """Collect unique problem IDs from topic categories and page range.

        Args:
            subject: Subject short code.
            topic_id: Topic identifier.
            pages_per_category: Number of pages to scan for each category.

        Returns:
            Unique candidate problem identifiers.
        """
        catalog = await self.get_catalog(subject)
        target_topic = next((topic for topic in catalog if str(topic.get("topic_id")) == topic_id), None)
        if target_topic is None:
            return []

        categories = target_topic.get("categories", [])
        if not isinstance(categories, list):
            return []

        category_ids: list[str] = []
        for category in categories:
            if not isinstance(category, dict):
                continue
            category_id = category.get("category_id")
            if isinstance(category_id, str) and category_id:
                category_ids.append(category_id)

        if not category_ids:
            return []

        semaphore = asyncio.Semaphore(10)
        lock = asyncio.Lock()
        seen_ids: set[str] = set()
        candidate_ids: list[str] = []

        async def collect_for_page(category_id: str, page: int) -> None:
            async with semaphore:
                page_ids = await self.get_category_by_id(subject, category_id, page=page)

            async with lock:
                for problem_id in page_ids:
                    if problem_id in seen_ids:
                        continue
                    seen_ids.add(problem_id)
                    candidate_ids.append(problem_id)

        await asyncio.gather(
            *(
                collect_for_page(category_id, page)
                for category_id in category_ids
                for page in range(1, pages_per_category + 1)
            )
        )
        return candidate_ids

    def _pick_problem_with_seed(self, candidate_ids: list[str], seed: int | None) -> str | None:
        """Pick one problem identifier from candidates.

        Args:
            candidate_ids: Candidate identifiers to pick from.
            seed: Optional random seed for deterministic selection.

        Returns:
            Selected problem identifier or None if candidates are empty.
        """
        if not candidate_ids:
            return None
        return random.Random(seed).choice(candidate_ids)

    async def _fetch_soup(self, url: str) -> BeautifulSoup:
        """Fetch URL and parse response as HTML.

        Args:
            url: Absolute URL.

        Returns:
            Parsed BeautifulSoup document.
        """
        response = await self._request_with_retry(lambda: self._http_client.get(url))
        return BeautifulSoup(response.content, "html.parser")

    async def _request_with_retry(
        self,
        request: Callable[[], Awaitable[httpx.Response]],
        allow_redirect_response: bool = False,
    ) -> httpx.Response:
        """Execute HTTP request with retry and explicit status checks.

        Args:
            request: Zero-argument async function returning HTTP response.
            allow_redirect_response: Return redirect responses without raising.

        Returns:
            Successful HTTP response object.
        """
        last_error: Exception | None = None
        for attempt in range(self._retries + 1):
            try:
                response = await request()
                if allow_redirect_response and response.is_redirect:
                    return response
                response.raise_for_status()
                return response
            except httpx.HTTPError as error:
                last_error = error
                if attempt == self._retries:
                    raise
                await asyncio.sleep(self._retry_base_delay_seconds * (attempt + 1))

        if last_error is not None:
            raise last_error
        raise RuntimeError("Unexpected request wrapper state")

    @staticmethod
    def _extract_redirect_location(response: httpx.Response) -> str:
        location = response.headers.get("location")
        if location is None:
            raise ValueError("Redirect response does not include a location header.")
        return location
