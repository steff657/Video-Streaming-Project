from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    help = "Verify deploy health: no pending migrations and required tables exist."

    def handle(self, *args, **options):
        connection = connections[DEFAULT_DB_ALIAS]
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        pending_plan = executor.migration_plan(targets)

        if pending_plan:
            pending = [
                f"{migration.app_label}.{migration.name}"
                for migration, backward in pending_plan
                if not backward
            ]
            raise CommandError(
                "Unapplied migrations detected: " + ", ".join(pending)
            )

        required_tables = (
            "core_profile",
            "core_video",
            "core_report",
        )
        existing_tables = set(connection.introspection.table_names())
        missing_tables = [
            table for table in required_tables if table not in existing_tables
        ]
        if missing_tables:
            raise CommandError(
                "Missing critical database tables: "
                + ", ".join(missing_tables)
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Deployment health check passed: migrations and tables are healthy."
            )
        )
