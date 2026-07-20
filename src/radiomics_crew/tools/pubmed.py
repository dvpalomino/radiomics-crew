"""PubMed access through NCBI E-utilities. No API key required (one is recommended)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..settings import settings
from ._http import cached_get, freeze

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


class PubMedSearchInput(BaseModel):
    query: str = Field(description="PubMed boolean query, e.g. '(radiomics[tiab]) AND (pancrea*[tiab])'")
    max_results: int = Field(default=25, description="Cap on returned PMIDs (1-100)")
    min_year: int | None = Field(default=None, description="Optional lower bound on publication year")


class PubMedSearchTool(BaseTool):
    name: str = "pubmed_search"
    description: str = (
        "Search PubMed with a boolean query and return matching PMIDs with titles. "
        "Use real PubMed syntax ([tiab], [mh], AND/OR/NOT). "
        "Returns 'NO_RESULTS' when the query is too narrow."
    )
    args_schema: type[BaseModel] = PubMedSearchInput

    def _run(self, query: str, max_results: int = 25, min_year: int | None = None) -> str:
        max_results = max(1, min(int(max_results), 100))
        term = query if min_year is None else f'({query}) AND ("{min_year}"[PDAT] : "3000"[PDAT])'
        params = {
            "db": "pubmed",
            "term": term,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
            "email": settings.ncbi_email,
            "api_key": settings.ncbi_api_key,
        }
        raw = cached_get(ESEARCH, freeze(params))
        if raw.startswith("TOOL_ERROR"):
            return raw
        try:
            import json

            ids = json.loads(raw)["esearchresult"]["idlist"]
        except (KeyError, ValueError) as exc:
            return f"TOOL_ERROR: could not parse PubMed response ({exc})"
        if not ids:
            return f"NO_RESULTS for query: {term}. Broaden the terms or drop a filter."
        return "\n".join([f"query: {term}", f"hits: {len(ids)}", "pmids: " + ", ".join(ids)])


class PubMedFetchInput(BaseModel):
    pmids: str = Field(description="Comma-separated PMIDs, e.g. '31234567,30987654'")


class PubMedFetchTool(BaseTool):
    name: str = "pubmed_fetch_abstracts"
    description: str = (
        "Fetch title, journal, year, authors and abstract for a list of PMIDs. "
        "Use this before judging a paper — never infer study design from the title alone."
    )
    args_schema: type[BaseModel] = PubMedFetchInput

    def _run(self, pmids: str) -> str:
        id_list = [p.strip() for p in pmids.replace(" ", ",").split(",") if p.strip().isdigit()]
        if not id_list:
            return "TOOL_ERROR: no valid PMIDs given."
        id_list = id_list[: settings.max_papers]
        params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml",
            "email": settings.ncbi_email,
            "api_key": settings.ncbi_api_key,
        }
        raw = cached_get(EFETCH, freeze(params))
        if raw.startswith("TOOL_ERROR"):
            return raw
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            return f"TOOL_ERROR: malformed XML from PubMed ({exc})"

        records: list[str] = []
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID", default="?")
            title = article.findtext(".//ArticleTitle", default="(no title)")
            journal = article.findtext(".//Journal/ISOAbbreviation", default="?")
            year = article.findtext(".//JournalIssue/PubDate/Year") or article.findtext(
                ".//JournalIssue/PubDate/MedlineDate", default="?"
            )
            doi = ""
            for aid in article.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text or ""
            abstract_parts = []
            for chunk in article.findall(".//Abstract/AbstractText"):
                label = chunk.get("Label")
                text = "".join(chunk.itertext()).strip()
                abstract_parts.append(f"{label}: {text}" if label else text)
            abstract = " ".join(abstract_parts) or "(no abstract available)"
            records.append(
                f"PMID {pmid} | {journal} {year} | doi:{doi or 'n/a'}\nTITLE: {title}\nABSTRACT: {abstract}"
            )
        if not records:
            return "NO_RESULTS: PubMed returned no parsable records for those PMIDs."
        return "\n\n---\n\n".join(records)
