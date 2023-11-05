from django.urls import reverse_lazy
from django.core import management
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


# class ImportView(FormMixin, View):
#     form_class = ImportForm
#     def get(self, request, *args, **kwargs):
#
#         management.call_command("upload", f"fixtures/04-shops.json")
#         return render(request, "import_app/import_app.jinja2")
#
#     def post(self, request, *args, **kwargs):
#         return redirect("import_app:import_app")
