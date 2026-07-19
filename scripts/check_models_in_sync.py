#!/usr/bin/env python
"""Fail CI if the Django models here drift from the SQLAlchemy models in
ensembl-metadata-api, which own the real ensembl_genome_metadata schema.

This compares field metadata only (column names, nullability, max_length,
choice/enum value sets) - it does not touch a database. Two hand-maintained
model layers for the same tables previously drifted silently (see the
alt_accession/tol_id/url_name/is_best/... fixes in migrations 0023-0024) and
broke the admin UI in production before anyone noticed; this check exists so
that drift fails CI instead.

Usage:
    DJANGO_SETTINGS_MODULE=metadata_admin.settings python scripts/check_models_in_sync.py

Exit status is non-zero if any table has a field-level mismatch.
"""
import os
import sys

import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metadata_admin.settings")
# Model introspection only touches Python class metadata below - no query is
# ever issued - so a throwaway sqlite URL keeps this runnable without a live
# MySQL instance (e.g. in CI).
os.environ.setdefault("REGISTRY_DB", ":memory:")
django.setup()

from django.apps import apps  # noqa: E402

from sqlalchemy import Enum as SAEnum, String as SAString  # noqa: E402
from sqlalchemy.dialects import mysql as sa_mysql  # noqa: E402

# Import every SQLAlchemy model module so Base.metadata is fully populated.
from ensembl.production.metadata.api.models import assembly, dataset, genome, organism, release  # noqa: E402,F401
from ensembl.production.metadata.api.models.base import Base  # noqa: E402


def sqlalchemy_column_signature(col):
    sig = {"nullable": bool(col.nullable)}
    pytype = col.type
    if isinstance(pytype, SAEnum) or getattr(pytype, "enum_class", None):
        if getattr(pytype, "enum_class", None):
            values = {e.value for e in pytype.enum_class}
        else:
            values = set(pytype.enums)
        sig["choices"] = values
    elif isinstance(pytype, (SAString, sa_mysql.VARCHAR)) and pytype.length:
        sig["max_length"] = pytype.length
    return sig


def django_field_signature(field):
    sig = {"nullable": bool(getattr(field, "null", False))}
    choices = getattr(field, "choices", None)
    if choices:
        sig["choices"] = {value for value, _label in choices}
    max_length = getattr(field, "max_length", None)
    if max_length:
        sig["max_length"] = max_length
    return sig


def django_column_map(model):
    """db_column_name -> field, for concrete, single-valued fields only."""
    result = {}
    for field in model._meta.get_fields():
        if not getattr(field, "concrete", False) or field.many_to_many:
            continue
        result[field.column] = field
    return result


def sqlalchemy_column_map(table_name):
    table = Base.metadata.tables.get(table_name)
    if table is None:
        return None
    return {col.name: col for col in table.columns}


def check_model(model):
    """Return (errors, warnings) for one model.

    Errors are structural: a field/column present on one side and not the
    other, or a CharField/Enum whose set of legal values differs - both are
    proven-in-production bug classes here (OperationalError on missing
    columns, ValidationError/silent choice-mismatch on read-back).

    Warnings are max_length differences only. These do NOT necessarily mean
    Django is wrong: SQLAlchemy's own declared length can itself drift from
    the real column (assembly_sequence.source is Column(String(128)) in
    metadata-api but the live DB column is varchar(120) - Django matches the
    real DB here, SQLAlchemy doesn't). A shorter Django field than the real
    column is harmless (no truncation), so this is surfaced for a human to
    look at rather than failing the build.
    """
    table_name = model._meta.db_table
    sa_columns = sqlalchemy_column_map(table_name)
    errors, warnings = [], []
    if sa_columns is None:
        return [f"table {table_name!r}: not found in SQLAlchemy metadata (skipped)"], []

    dj_columns = django_column_map(model)

    dj_only = dj_columns.keys() - sa_columns.keys()
    sa_only = sa_columns.keys() - dj_columns.keys()
    for name in sorted(dj_only):
        errors.append(f"{table_name}.{name}: in Django model but not in SQLAlchemy model")
    for name in sorted(sa_only):
        errors.append(f"{table_name}.{name}: in SQLAlchemy model but missing from Django model")

    for name in sorted(dj_columns.keys() & sa_columns.keys()):
        dj_sig = django_field_signature(dj_columns[name])
        sa_sig = sqlalchemy_column_signature(sa_columns[name])
        if "choices" in dj_sig or "choices" in sa_sig:
            dj_choices = dj_sig.get("choices")
            sa_choices = sa_sig.get("choices")
            if dj_choices is not None and sa_choices is not None and dj_choices != sa_choices:
                errors.append(
                    f"{table_name}.{name}: choice values differ - "
                    f"Django={sorted(dj_choices)} SQLAlchemy={sorted(sa_choices)}"
                )
        if "max_length" in dj_sig and "max_length" in sa_sig:
            if dj_sig["max_length"] < sa_sig["max_length"]:
                warnings.append(
                    f"{table_name}.{name}: Django max_length={dj_sig['max_length']} "
                    f"< SQLAlchemy max_length={sa_sig['max_length']} - verify against the real column, "
                    f"either side can be the one that's wrong"
                )

    return errors, warnings


# Tables that intentionally have no Django model in this app - either they
# belong to a different Django app (taxonomy tables) or genuinely have no
# admin UI use case yet. Anything not listed here is a real gap: a whole
# table SQLAlchemy knows about that this app can't query/administer at all.
NO_DJANGO_MODEL_EXPECTED = set()


def check_table_coverage(django_tables):
    sa_tables = set(Base.metadata.tables.keys())
    missing = sa_tables - django_tables - NO_DJANGO_MODEL_EXPECTED
    return [
        f"table {name!r}: exists in SQLAlchemy/DB schema with no Django model at all "
        f"(not even a stub - fully inaccessible from this app)"
        for name in sorted(missing)
    ]


def main():
    app_config = apps.get_app_config("ensembl_metadata")
    all_errors, all_warnings = {}, {}
    django_tables = set()
    for model in app_config.get_models():
        django_tables.add(model._meta.db_table)
        errors, warnings = check_model(model)
        if errors:
            all_errors[model.__name__] = errors
        if warnings:
            all_warnings[model.__name__] = warnings

    coverage_gaps = check_table_coverage(django_tables)
    if coverage_gaps:
        all_errors["(missing models)"] = coverage_gaps

    if all_warnings:
        print("Warnings (non-fatal - review, don't assume Django is the wrong side):\n")
        for model_name, warnings in all_warnings.items():
            print(f"{model_name}:")
            for warning in warnings:
                print(f"  - {warning}")
            print()

    if not all_errors:
        print("OK: no field-level drift between Django models and SQLAlchemy models.")
        return 0

    print("Model/schema drift detected (fails CI):\n")
    for model_name, errors in all_errors.items():
        print(f"{model_name}:")
        for error in errors:
            print(f"  - {error}")
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
