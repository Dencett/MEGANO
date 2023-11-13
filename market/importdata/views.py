import os

from django.urls import reverse_lazy
from django.core import management
from django.core.cache import cache
from django.conf import settings
from django.views.generic.edit import FormView

from .forms import ImportForm


class ImportView(FormView):
    form_class = ImportForm
    template_name = "importdata/import.jinja2"
    success_url = reverse_lazy("importdata:importdata")

    def form_valid(self, form):
        responce = super().form_valid(form)
        cd = form.cleaned_data
        management.call_command("importdata", *cd["files"], email=cd["mail_to"])
        return responce

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "import_is_running": cache.get("import_is_running"),
                "import_files": [
                    file
                    for file in os.listdir(os.path.abspath(settings.IMPORT_FOLDER))
                    if os.path.isfile(os.path.join(settings.IMPORT_FOLDER, file))
                ],
            }
        )

        return context
