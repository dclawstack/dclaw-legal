"""Add document templates

Revision ID: 2026_05_09_0002
Revises: 2026_05_08_0001
Create Date: 2026-05-09 00:00:00.000000

"""
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2026_05_09_0002"
down_revision: Union[str, None] = "2026_05_08_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_NDA_TEXT = """MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement ("Agreement") is entered into on {{effective_date}} by and between {{party_a}} and {{party_b}} (each a "Party").

1. CONFIDENTIAL INFORMATION
Each Party may disclose confidential information to the other relating to {{purpose}}.

2. OBLIGATIONS
Each Party shall hold the other's confidential information in strict confidence for {{term_years}} years.

3. GOVERNING LAW
This Agreement shall be governed by the laws of {{governing_law}}.

Signed:
{{party_a}}: ____________________
{{party_b}}: ____________________
"""

_NDA_VARS = {
    "effective_date": {"label": "Effective date", "type": "date", "required": True},
    "party_a": {"label": "Party A (your company)", "type": "text", "required": True},
    "party_b": {"label": "Party B (counterparty)", "type": "text", "required": True},
    "purpose": {"label": "Purpose of disclosure", "type": "textarea", "required": True},
    "term_years": {"label": "Confidentiality term (years)", "type": "number", "required": True},
    "governing_law": {"label": "Governing law jurisdiction", "type": "text", "required": True},
}

_MSA_TEXT = """MASTER SERVICES AGREEMENT

This Master Services Agreement ("Agreement") is between {{client_name}} ("Client") and {{provider_name}} ("Provider"), effective {{effective_date}}.

1. SERVICES
Provider shall perform the services described in one or more Statements of Work ("SOWs") executed under this Agreement.

2. PAYMENT TERMS
Client shall pay Provider within {{payment_terms_days}} days of invoice receipt.

3. TERM AND TERMINATION
This Agreement begins on the Effective Date and continues until terminated by either Party with {{notice_days}} days' written notice.

4. CONFIDENTIALITY
Each Party shall protect the other's Confidential Information.

5. GOVERNING LAW
This Agreement is governed by {{governing_law}}.
"""

_MSA_VARS = {
    "client_name": {"label": "Client name", "type": "text", "required": True},
    "provider_name": {"label": "Provider name", "type": "text", "required": True},
    "effective_date": {"label": "Effective date", "type": "date", "required": True},
    "payment_terms_days": {"label": "Payment terms (days)", "type": "number", "required": True},
    "notice_days": {"label": "Termination notice (days)", "type": "number", "required": True},
    "governing_law": {"label": "Governing law", "type": "text", "required": True},
}

_SOW_TEXT = """STATEMENT OF WORK

This Statement of Work ("SOW") is issued under the Master Services Agreement between {{client_name}} and {{provider_name}}, dated {{msa_date}}.

PROJECT: {{project_name}}

SCOPE OF WORK
{{scope}}

DELIVERABLES
{{deliverables}}

TIMELINE
Start date: {{start_date}}
End date: {{end_date}}

FEES
Total fixed fee: {{total_fee}}
"""

_SOW_VARS = {
    "client_name": {"label": "Client name", "type": "text", "required": True},
    "provider_name": {"label": "Provider name", "type": "text", "required": True},
    "msa_date": {"label": "MSA date", "type": "date", "required": True},
    "project_name": {"label": "Project name", "type": "text", "required": True},
    "scope": {"label": "Scope of work", "type": "textarea", "required": True},
    "deliverables": {"label": "Deliverables", "type": "textarea", "required": True},
    "start_date": {"label": "Start date", "type": "date", "required": True},
    "end_date": {"label": "End date", "type": "date", "required": True},
    "total_fee": {"label": "Total fee", "type": "text", "required": True},
}

_EMPLOYMENT_TEXT = """EMPLOYMENT AGREEMENT

This Employment Agreement is entered into on {{start_date}} between {{employer_name}} ("Employer") and {{employee_name}} ("Employee").

1. POSITION
Employee will serve as {{job_title}}, reporting to {{reports_to}}.

2. COMPENSATION
Annual salary: {{annual_salary}}, paid in accordance with Employer's standard payroll schedule.

3. AT-WILL EMPLOYMENT
Employment is at-will and may be terminated by either Party at any time.

4. CONFIDENTIALITY AND IP
Employee agrees to protect Employer's Confidential Information and assigns to Employer all work-product IP created during employment.

5. GOVERNING LAW
This Agreement is governed by the laws of {{governing_law}}.
"""

_EMPLOYMENT_VARS = {
    "employer_name": {"label": "Employer name", "type": "text", "required": True},
    "employee_name": {"label": "Employee name", "type": "text", "required": True},
    "job_title": {"label": "Job title", "type": "text", "required": True},
    "reports_to": {"label": "Reports to", "type": "text", "required": True},
    "annual_salary": {"label": "Annual salary", "type": "text", "required": True},
    "start_date": {"label": "Start date", "type": "date", "required": True},
    "governing_law": {"label": "Governing law", "type": "text", "required": True},
}


def upgrade() -> None:
    op.create_table(
        "document_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False, server_default="general"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("template_text", sa.Text(), nullable=False),
        sa.Column(
            "variables",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_templates")),
    )
    op.create_index(
        op.f("ix_document_templates_category"),
        "document_templates",
        ["category"],
    )

    templates_table = sa.table(
        "document_templates",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("category", sa.String),
        sa.column("description", sa.Text),
        sa.column("template_text", sa.Text),
        sa.column("variables", postgresql.JSONB),
    )

    op.bulk_insert(
        templates_table,
        [
            {
                "id": uuid.uuid4(),
                "name": "Mutual Non-Disclosure Agreement",
                "category": "NDA",
                "description": "Standard mutual NDA between two parties.",
                "template_text": _NDA_TEXT,
                "variables": _NDA_VARS,
            },
            {
                "id": uuid.uuid4(),
                "name": "Master Services Agreement",
                "category": "MSA",
                "description": "Master agreement governing recurring services and SOWs.",
                "template_text": _MSA_TEXT,
                "variables": _MSA_VARS,
            },
            {
                "id": uuid.uuid4(),
                "name": "Statement of Work",
                "category": "SOW",
                "description": "SOW issued under an existing MSA.",
                "template_text": _SOW_TEXT,
                "variables": _SOW_VARS,
            },
            {
                "id": uuid.uuid4(),
                "name": "Employment Agreement",
                "category": "Employment",
                "description": "At-will employment agreement.",
                "template_text": _EMPLOYMENT_TEXT,
                "variables": _EMPLOYMENT_VARS,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_document_templates_category"), table_name="document_templates")
    op.drop_table("document_templates")
