from django.db import models


class CoreQuerySet(models.query.QuerySet):
    """QuerySet whose delete() does not delete items, but instead marks the
    rows as not active, and updates the timestamps"""

    def delete(self):
        self.update(deleted=True)

    
class CoreModelManager(models.Manager):
    # TODO make this compatible with related fields.
    # get_queryset returns all instances even that are not related
    # to base model.

    def get_query_set(self):
        return CoreQuerySet(self.model, using=self._db)
    
    def get_queryset(self, show_hidden=False):
        qs = super().get_queryset()
        if not show_hidden:
            qs = qs.filter(deleted=False)
        return qs