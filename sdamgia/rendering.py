"""Problem image rendering backends."""

from __future__ import annotations

import asyncio
import os
from os import remove

from bs4 import Tag


class _ProblemImageRenderer:
    """Render problem HTML block to image with selected backend."""

    async def render(
        self,
        *,
        prob_block: Tag,
        renderer: str,
        problem_id: str,
        path_to_img: str | None,
        path_to_tmp_html: str,
        html2img_chrome_path: str,
        grabzit_auth: dict[str, str],
    ) -> None:
        """Render HTML block to image with given backend.

        Args:
            prob_block: Parsed task block from sdamgia page.
            renderer: Backend name: pyppeteer, grabzit, or html2img.
            problem_id: Task identifier used for temp file naming.
            path_to_img: Result image path.
            path_to_tmp_html: Temp html directory for pyppeteer backend.
            html2img_chrome_path: Browser path for html2img backend.
            grabzit_auth: GrabzIT credentials.

        Returns:
            None.
        """
        if renderer == "pyppeteer":
            await self._render_with_pyppeteer(prob_block, problem_id, path_to_img, path_to_tmp_html)
            return
        if renderer == "grabzit":
            await asyncio.to_thread(
                self._render_with_grabzit,
                prob_block,
                path_to_img,
                grabzit_auth,
            )
            return
        if renderer == "html2img":
            await asyncio.to_thread(
                self._render_with_html2img,
                prob_block,
                path_to_img,
                html2img_chrome_path,
            )

    @staticmethod
    async def _render_with_pyppeteer(
        prob_block: Tag,
        problem_id: str,
        path_to_img: str | None,
        path_to_tmp_html: str,
    ) -> None:
        from pyppeteer import launch

        tmp_html_path = os.path.abspath(f"{path_to_tmp_html}{problem_id}.html")
        with open(tmp_html_path, "w", encoding="utf-8") as html_file:
            html_file.write(str(prob_block))

        try:
            browser = await launch()
            page = await browser.newPage()
            await page.goto("file:" + tmp_html_path)
            await page.screenshot({"path": path_to_img, "fullPage": "true"})
            await browser.close()
        finally:
            remove(tmp_html_path)

    @staticmethod
    def _render_with_grabzit(
        prob_block: Tag,
        path_to_img: str | None,
        grabzit_auth: dict[str, str],
    ) -> None:
        from GrabzIt import GrabzItClient, GrabzItImageOptions

        grabzit = GrabzItClient.GrabzItClient(grabzit_auth["AppKey"], grabzit_auth["AppSecret"])
        options = GrabzItImageOptions.GrabzItImageOptions()
        options.browserWidth = 800
        options.browserHeight = -1
        grabzit.HTMLToImage(str(prob_block), options=options)
        grabzit.SaveTo(path_to_img)

    @staticmethod
    def _render_with_html2img(
        prob_block: Tag,
        path_to_img: str | None,
        html2img_chrome_path: str,
    ) -> None:
        from html2image import Html2Image

        if html2img_chrome_path == "chrome":
            html2image = Html2Image()
        else:
            html2image = Html2Image(
                chrome_path=html2img_chrome_path,
                custom_flags=["--no-sandbox"],
            )
        html2image.screenshot(html_str=str(prob_block), save_as=path_to_img)
