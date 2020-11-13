from django.views.generic import FormView
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from import_export.formats import base_formats
from import_export.forms import ImportForm, ConfirmImportForm
from import_export.resources import modelresource_factory
from django.http import HttpResponseRedirect

from import_export.tmp_storages import TempFolderStorage
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

from django.conf import settings

TMP_STORAGE_CLASS = getattr(settings, 'IMPORT_EXPORT_TMP_STORAGE_CLASS', TempFolderStorage)

DEFAULT_FORMATS = (
    base_formats.CSV,
    base_formats.XLS,
    base_formats.TSV,
    base_formats.ODS,
    base_formats.JSON,
    base_formats.YAML,
    base_formats.HTML,
)


class ImportView(FormView):
    """ Combines django.views.generic.FormView with
    import_export.admin.ImportExportMixin to reproduce, in a CBV, the
    Django admin import integration from Django-import-export.
    """
    import_resource_class = None
    resource_class = None
    form_class = ImportForm
    confirm_form_class = ConfirmImportForm
    model = None
    formats = DEFAULT_FORMATS
    from_encoding = "utf-8"
    tmp_storage_class = None
    success_url = None

    # NB serve .as_view(confirm=True) at a different URL to perform the import
    confirm = False

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        resource = self.get_import_resource_class()()
        return self.render_to_response(self.get_context_data(
            form=form,
            fields=[f.column_name for f in resource.get_fields()]
        ))

    def get_form_kwargs(self, import_formats=True):
        kwargs = super().get_form_kwargs()
        if import_formats is True:
            kwargs['import_formats'] = self.get_import_formats()
        return kwargs

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        if form_class is self.form_class:
            import_formats = True
        else:
            import_formats = False
        return form_class(**self.get_form_kwargs(import_formats=import_formats))

    def post(self, request, *args, **kwargs):
        if self.confirm is True:
            confirm_form = self.get_form(form_class=self.confirm_form_class)
            if confirm_form.is_valid():
                return self.process_import(confirm_form)
        return super().post(request, *args, **kwargs)

    def get_import_formats(self):
        """
        Returns available import formats.
        """
        return [f for f in self.formats if f().can_import()]

    def create_dataset(self, input_format, data):
        """ Separate, so that this is hookable for extra logic.
        """
        dataset = input_format.create_dataset(data)
        return dataset

    def get_resource_class(self):
        if not self.resource_class:
            return modelresource_factory(self.model)
        else:
            return self.resource_class

    def get_import_resource_class(self):
        """
        Returns ResourceClass to use for import.
        """
        return self.get_resource_class()

    def get_tmp_storage_class(self):
        if self.tmp_storage_class is None:
            return TMP_STORAGE_CLASS
        else:
            return self.tmp_storage_class

    def form_valid(self, form):
        """ This bit reproduces ImportMixin.import_action
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        """
        resource = self.get_import_resource_class()()
        context = {}
        import_formats = self.get_import_formats()
        input_format = import_formats[
            int(form.cleaned_data['input_format'])
        ]()
        import_file = form.cleaned_data['import_file']
        # first always write the uploaded file to disk as it may be a
        # memory file or else based on settings upload handlers
        tmp_storage = self.get_tmp_storage_class()()
        data = bytes()
        for chunk in import_file.chunks():
            data += chunk

        tmp_storage.save(data, input_format.get_read_mode())

        # then read the file, using the proper format-specific mode
        # warning, big files may exceed memory
        data = tmp_storage.read(input_format.get_read_mode())
        if not input_format.is_binary() and self.from_encoding:
            data = force_text(data, self.from_encoding)
        dataset = self.create_dataset(input_format, data)
        result = resource.import_data(dataset, dry_run=True,
                                      raise_errors=False,
                                      file_name=import_file.name,
                                      user=self.request.user)
        context['result'] = result

        if not result.has_errors():
            context['confirm_form'] = self.confirm_form_class(initial={
                'import_file_name': tmp_storage.name,
                'original_file_name': import_file.name,
                'input_format': form.cleaned_data['input_format'],
            })
        return self.render_to_response(self.get_context_data(
            form=form,
            fields=[f.column_name for f in resource.get_fields()],
            **context))

    def process_import(self, confirm_form):
        """ This bit reproduces ImportMixin.process_import
        """
        resource = self.get_import_resource_class()()
        import_formats = self.get_import_formats()
        input_format = import_formats[
            int(confirm_form.cleaned_data['input_format'])
        ]()
        tmp_storage = self.get_tmp_storage_class()(
            name=confirm_form.cleaned_data['import_file_name'])
        data = tmp_storage.read(input_format.get_read_mode())
        if not input_format.is_binary() and self.from_encoding:
            data = force_text(data, self.from_encoding)
        dataset = self.create_dataset(input_format, data)

        resource.import_data(
            dataset, dry_run=False, raise_errors=True,
            file_name=confirm_form.cleaned_data['original_file_name'],
            user=self.request.user)
        success_message = _('Import finished')
        messages.success(self.request, success_message)
        tmp_storage.remove()

        return HttpResponseRedirect(self.get_success_url())