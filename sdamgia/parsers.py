"""HTML parsers for sdamgia pages."""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag


class _ProblemParser:
    """Build structured problem payload from HTML."""

    @staticmethod
    def normalize_images(prob_block: Tag, subject_base_url: str) -> None:
        """Normalize relative image URLs inside problem block."""
        for image in prob_block.find_all("img"):
            src = image.get("src", "")
            if "sdamgia.ru" not in src:
                image["src"] = f"{subject_base_url}{src}"

    @staticmethod
    def parse_problem(prob_block: Tag, problem_id: str, problem_url: str) -> dict[str, object]:
        """Parse a problem page block into API payload format."""
        topic_id = " ".join(
            prob_block.find("span", {"class": "prob_nums"}).text.split()[1:][:-2]
        )
        condition: dict[str, object] = {}
        solution: dict[str, object] = {}
        answer = ""
        analogs: list[str] = []

        pbody_blocks = prob_block.find_all("div", {"class": "pbody"})
        if len(pbody_blocks) > 0:
            condition = {
                "text": pbody_blocks[0].text,
                "images": [image["src"] for image in pbody_blocks[0].find_all("img")],
            }
        if len(pbody_blocks) > 1:
            solution = {
                "text": pbody_blocks[1].text,
                "images": [image["src"] for image in pbody_blocks[1].find_all("img")],
            }

        answer_block = prob_block.find("div", {"class": "answer"})
        if answer_block is not None:
            answer = answer_block.text.replace("Ответ: ", "")

        analogs_block = prob_block.find("div", {"class": "minor"})
        if analogs_block is not None:
            analogs = [link.text for link in analogs_block.find_all("a")]
            if "Все" in analogs:
                analogs.remove("Все")

        return {
            "id": problem_id,
            "topic": topic_id,
            "condition": condition,
            "solution": solution,
            "answer": answer,
            "analogs": analogs,
            "url": problem_url,
        }


class _CatalogParser:
    """Build subject catalog payload from HTML."""

    @staticmethod
    def parse(soup: BeautifulSoup) -> list[dict[str, object]]:
        """Parse catalog page into API payload format."""
        topic_blocks: list[Tag] = []
        for block in soup.find_all("div", {"class": "cat_category"}):
            if block.get("data-id") is None:
                topic_blocks.append(block)

        catalog: list[dict[str, object]] = []
        for topic_block in topic_blocks[1:]:
            topic_name_raw = topic_block.find("b", {"class": "cat_name"}).text
            topic_id, topic_name = topic_name_raw.split(". ", maxsplit=1)

            if topic_id.startswith(" "):
                topic_id = topic_id[2:]
            if topic_id.startswith("Задания "):
                topic_id = topic_id.replace("Задания ", "")

            categories = []
            children = topic_block.find("div", {"class": "cat_children"})
            for category in children.find_all("div", {"class": "cat_category"}):
                categories.append(
                    {
                        "category_id": category["data-id"],
                        "category_name": category.find("a", {"class": "cat_name"}).text,
                    }
                )

            catalog.append(
                {
                    "topic_id": topic_id,
                    "topic_name": topic_name,
                    "categories": categories,
                }
            )

        return catalog


def _extract_problem_ids(soup: BeautifulSoup) -> list[str]:
    """Extract problem IDs from search-like pages."""
    return [item.text.split()[-1] for item in soup.find_all("span", {"class": "prob_nums"})]
