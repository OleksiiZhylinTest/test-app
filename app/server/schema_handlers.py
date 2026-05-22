"""Jira schema CRUD handler mixin — /api/schemas."""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


class SchemaHandlerMixin:
    @staticmethod
    def _slugify(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower().strip())
        slug = slug.strip("_")[:80]
        return slug or "schema"

    def _handle_get_schemas(self) -> None:
        """List schema names, or return a single schema when ?name= is provided."""
        from app.core import schema as schema_mod

        params = self._query_params()
        name_list = params.get("name")

        if name_list:
            name = name_list[0]
            schema = schema_mod.get_schema(name)
            if schema is None:
                self._send_json(404, {"ok": False, "error": f"Schema '{name}' not found"})
            else:
                self._send_json(200, {"ok": True, "schema": schema})
        else:
            schemas = schema_mod.load_schemas()
            names = [s.get("schema_name", "") for s in schemas]
            self._send_json(200, {"ok": True, "schemas": names})

    def _handle_post_schema(self) -> None:
        """Upsert a schema entry from a raw-JSON body: {schema: {...}}."""
        from app.core import schema as schema_mod

        body = self._read_json_body()
        if not isinstance(body, dict):
            self._send_json(400, {"ok": False, "error": "Invalid JSON body"})
            return

        schema = body.get("schema")
        if not isinstance(schema, dict):
            self._send_json(400, {"ok": False, "error": "Request must contain a 'schema' object"})
            return

        raw_name = schema.get("schema_name")
        if not isinstance(raw_name, str) or not raw_name.strip():
            self._send_json(400, {"ok": False, "error": "schema_name must be a non-empty string"})
            return
        name = raw_name.strip()

        if not isinstance(schema.get("fields"), dict):
            self._send_json(400, {"ok": False, "error": "fields must be an object"})
            return

        status_mapping = schema.get("status_mapping")
        excluded = (status_mapping or {}).get("excluded_statuses")
        if (
            not isinstance(status_mapping, dict)
            or not isinstance(status_mapping.get("done_statuses"), list)
            or not isinstance(status_mapping.get("in_progress_statuses"), list)
            or (excluded is not None and not isinstance(excluded, list))
        ):
            self._send_json(
                400,
                {
                    "ok": False,
                    "error": (
                        "status_mapping.done_statuses and status_mapping.in_progress_statuses must be lists; "
                        "status_mapping.excluded_statuses is optional but must be a list if present"
                    ),
                },
            )
            return

        schema["schema_name"] = name
        updated = schema_mod.get_schema(name) is not None
        schema_mod.save_schema(schema)
        self._send_json(200, {"ok": True, "updated": updated, "schema": schema})

    def _handle_delete_schema(self) -> None:
        """Delete a schema entry by ?name=."""
        from app.core import schema as schema_mod

        params = self._query_params()
        name_list = params.get("name")
        if not name_list:
            self._send_json(400, {"ok": False, "error": "Query parameter 'name' is required"})
            return

        name = name_list[0]
        if name == schema_mod.DEFAULT_SCHEMA_NAME:
            self._send_json(400, {"ok": False, "error": "Cannot delete the default schema"})
            return

        deleted = schema_mod.delete_schema(name)
        if deleted:
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"ok": False, "error": f"Schema '{name}' not found"})
