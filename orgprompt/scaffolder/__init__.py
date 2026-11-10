"""Instant Scaffolder CLI and APIs for Canonical Roles and Enterprises."""

from orgprompt.scaffolder.company_scaffolder import CompanyScaffolder, CompanyScaffoldingPackage
from orgprompt.scaffolder.formatter import (
    format_company_json,
    format_company_markdown,
    format_role_json,
    format_role_markdown,
)
from orgprompt.scaffolder.role_scaffolder import RoleScaffolder, RoleScaffoldingPackage

__all__ = [
    "RoleScaffolder",
    "RoleScaffoldingPackage",
    "CompanyScaffolder",
    "CompanyScaffoldingPackage",
    "format_role_json",
    "format_role_markdown",
    "format_company_json",
    "format_company_markdown",
]
