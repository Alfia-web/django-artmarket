from django.shortcuts import render
from django.http import HttpResponse
from auction.models import Image
from django.views import View
from django.views.generic import TemplateView
from typing import Any
# Create your views here.

class ShowImagesView(View):
    template_name = "images/show_image.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['auction'] = ShowImagesView.objects.all()
        return context