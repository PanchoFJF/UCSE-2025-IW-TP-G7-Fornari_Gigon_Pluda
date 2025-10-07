from haystack import indexes
from sitio.models import Actividades
from django.utils import timezone
from django.db.models import Q

class ActividadIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)  
    titulo = indexes.CharField(model_attr='titulo')
    texto = indexes.CharField(model_attr='texto')
    categoria = indexes.CharField(model_attr='categoria', null=True)
    fechaVencimiento = indexes.DateTimeField(model_attr='fechaVencimiento', null=True)


    def get_model(self):
        return Actividades

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            Q(fechaVencimiento__gte=timezone.now()) | Q(fechaVencimiento__isnull=True)
        )