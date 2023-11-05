from django.core.management import BaseCommand
from importdata.tasks import load_files
from django.conf import settings


class Command(BaseCommand):
    help = (
        "Import products data into the database from json"
        "file(s) located at '%s' folder. *If no files are selected,"
        "the import will be initiated from all files in the directory." % settings.IMPORT_FOLDER
    )
    # missing_args_message = 'No files'

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            metavar="file",
            nargs="*",
            help="File(s) label(s).",
        )

        parser.add_argument(
            "-e",
            "--email",
            default=[],
            help="Address(es) to mail a report to.",
        )

    def handle(self, *files, **options):
        self.stdout.write(
            "Команда 'Importdata' поставлена в очередь задач на выполнение. "
            "По завершению будет отправлен отчет на почту."
        )
        load_files.delay(files, options["email"])
