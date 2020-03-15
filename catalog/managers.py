from django.db import models


class CoreModelManager(models.Manager):
    # TODO make this compatible with related fields.
    # get_queryset returns all instances even that are not related
    # to base model.

    def get_queryset(self, show_hidden=False):
        qs = super().get_queryset()
        if not show_hidden:
            qs = qs.filter(deleted=False)
        return qs