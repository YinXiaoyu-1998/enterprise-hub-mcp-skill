import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "smedc-mcp"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(document: str, heading: str) -> str:
    marker = f"## {heading}\n"
    if marker not in document:
        raise AssertionError(f"Missing active section: {heading}")
    return document.split(marker, 1)[1].split("\n## ", 1)[0]


def launcher_versions(content: str) -> list[str]:
    # Explicit install references only; bare minimum/history versions are not pins.
    patterns = (
        r"""smedc-mcp-launcher@([^\s`"']+)""",
        r"""launcher[\\/]+versions[\\/]+([^\\/\s`"']+)""",
        r'''"launcherVersion"\s*:\s*"([^"]+)"''',
        r"this document pins launcher\s+(\S+?)(?=[.;]?(?:\s|$))",
    )
    return [
        match.group(1)
        for pattern in patterns
        for match in re.finditer(pattern, content)
    ]


class SmedcSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = read(SKILL_ROOT / "SKILL.md")
        cls.openai_yaml = read(SKILL_ROOT / "agents" / "openai.yaml")
        cls.update_guide = read(SKILL_ROOT / "references" / "update-skill.md")
        cls.readme_text = read(ROOT / "README.md")
        cls.readme_zh_text = read(ROOT / "README.zh.md")
        cls.current_text = "\n".join(
            [
                cls.skill_text,
                cls.openai_yaml,
                cls.update_guide,
                cls.readme_text,
                cls.readme_zh_text,
            ]
        )

    def test_current_smedc_contract_is_documented(self) -> None:
        expected_terms = [
            "smedc-mcp",
            "SMEDC_BASE_URL",
            "smedc",
            "smedc_login",
            "smedc_logout",
            "smedc_auth_status",
            "smedc_get_current_user",
            "smedc_list_skills",
            "smedc-business-analysis",
            "smedc-delivery-ledger",
            "YinXiaoyu-1998/smedc-companion-skills",
            "organizationName",
            "YinXiaoyu-1998/smedc-mcp-skill",
        ]

        for term in expected_terms:
            with self.subTest(term=term):
                self.assertIn(term, self.current_text)

    def test_every_active_launcher_reference_uses_the_exact_pin(self) -> None:
        active = {
            "Skill approved package": self.skill_text.split("\n## ", 1)[0],
            "Skill update pin": section(self.update_guide, "Continue Within The Requested Scope"),
            "README release status": self.readme_text.split("\n## ", 1)[0],
            "README.zh release status": self.readme_zh_text.split("\n## ", 1)[0],
            "README install": section(self.readme_text, "Official Launcher"),
            "README.zh install": section(self.readme_zh_text, "正式 Launcher"),
        }
        for heading in [
            "Official Install Or Update",
            "Device-Code Login Flow",
            "Configure The Invoking Agent",
            "Removal And Complete Uninstall",
        ]:
            active[heading] = section(self.skill_text, heading)
        for label, content in active.items():
            with self.subTest(section=label):
                versions = launcher_versions(content)
                self.assertTrue(versions, f"No launcher references in {label}")
                self.assertEqual({"0.6.0"}, set(versions))

    def test_install_guidance_uses_current_repository_and_skill_name(self) -> None:
        for document, install_heading, update_heading, launcher_heading in [
            (self.readme_text, "Install The Skill", "Update The Skill", "Official Launcher"),
            (self.readme_zh_text, "安装 Skill", "更新 Skill 本体", "正式 Launcher"),
        ]:
            with self.subTest(language=install_heading):
                install = section(document, install_heading)
                self.assertIn("YinXiaoyu-1998/smedc-mcp-skill", section(document, update_heading))
                self.assertIn("~/.agents/skills/smedc-mcp", install)
                self.assertIn("skills/smedc-mcp", install)
                self.assertIn(
                    "SMEDC_BASE_URL=https://api.smedatacenter.xyz",
                    section(document, launcher_heading),
                )

    def test_pending_archive_reference_cannot_change_install_pins(self) -> None:
        for path in sorted(SKILL_ROOT.rglob("*")):
            if path.suffix in {".md", ".yaml"}:
                with self.subTest(path=path.relative_to(SKILL_ROOT)):
                    self.assertTrue(set(launcher_versions(read(path))) <= {"0.6.0", "..."})
        reference = read(SKILL_ROOT / "references" / "ledger-pdf-tools.md")
        self.assertIn("0.7.0 once published", reference)
        self.assertIn("not published", reference)
        self.assertIn("service archive delivery", reference)
        self.assertIn("references/ledger-pdf-tools.md", self.skill_text)

    def test_archive_tool_table_exposes_only_frozen_public_inputs(self) -> None:
        reference = read(SKILL_ROOT / "references" / "ledger-pdf-tools.md")
        rows = [line for line in reference.splitlines() if line.startswith("| `")]
        self.assertEqual(rows, [
            "| `describe_ledger_pdf_coverage` | date selection | `storeNames`, `cursor` |",
            "| `refresh_ledger_pdfs` | `storeNames`, date selection, `idempotencyKey` | none |",
            "| `get_ledger_pdf_request_status` | `requestId` | `cursor` |",
            "| `prepare_ledger_pdf_download` | `storeNames`, date selection, `idempotencyKey` | none |",
            "| `get_ledger_pdf_download_url` | `requestId` | none |",
        ])

    def test_distributed_skill_has_no_retired_product_or_tenant_names(self) -> None:
        retired = re.compile(
            r"enterprise[- _]?hub|enterpricehub|maijia|麦家", re.IGNORECASE
        )
        for path in sorted(SKILL_ROOT.rglob("*")):
            if path.suffix not in {".md", ".yaml"}:
                continue
            with self.subTest(path=path.relative_to(SKILL_ROOT)):
                self.assertIsNone(retired.search(read(path)))


if __name__ == "__main__":
    unittest.main()
