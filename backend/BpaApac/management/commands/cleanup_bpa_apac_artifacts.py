from django.core.management.base import BaseCommand

from BpaApac.details_storage import cleanup_artifacts, compress_legacy_plain_json


class Command(BaseCommand):
    help = "Remove detalhes/arquivos BPA/APAC antigos e compacta JSONs legados."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Dias de retenção. Use 0 para apenas compactar JSONs legados sem apagar.",
        )
        parser.add_argument(
            "--compress-only",
            action="store_true",
            help="Apenas converte *.json legados para *.json.gz.",
        )

    def handle(self, *args, **options):
        if options["compress_only"]:
            converted = compress_legacy_plain_json()
            self.stdout.write(self.style.SUCCESS(f"JSONs compactados: {converted}"))
            return

        summary = cleanup_artifacts(retention_days=options["days"])
        self.stdout.write(
            self.style.SUCCESS(
                "Limpeza concluida | "
                f"detalhes removidos: {summary['details_removed']} | "
                f"outputs removidos: {summary['outputs_removed']} | "
                f"legados compactados: {summary['compressed_legacy']} | "
                f"retencao: {summary.get('retention_days', 'n/a')} dias"
            )
        )
