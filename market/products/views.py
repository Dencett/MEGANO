from django.http import HttpRequest, HttpResponse
from django.shortcuts import render  # noqa F401
from django.views import View
from django.views.generic import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView

from .models import Product
from .services.review_services import ReviewServices
from .forms import ProductReviewForm
from django.urls import reverse


class HomeView(View):
    """Главная страница магазина"""

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "base.jinja2")


class ProductDetailView(DetailView):
    """
    Отображение детальной информации о товаре (описание, характеристики, продавцы, отзывы и др), а также
    отображение формы для добавления комментариев к товару.
    """

    model = Product
    template_name = "products/product_details.jinja2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = ReviewServices(self.request, self.object)
        offers = self.object.offer_set.all()

        context["min_price"] = min(offers, key=lambda x: x.price).price
        context["form"] = ProductReviewForm()
        context["reviews"] = review.get_reviews()
        context["page_obj"] = review.listing(context["reviews"])

        return context


class ProductReviewFormView(SingleObjectMixin, FormView):
    """Валидация формы и дальнейшие действия по созданию экземпляра класса "Review"
    c примесью SingleObjectMixin для получения и использования 'object' в get_success_url() при переадресации.
    """

    template_name = "products/product_details.jinja2"
    form_class = ProductReviewForm
    model = Product

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """Получение валидных данных с последующим созданием экземпляра класса "Review"""
        response = super().form_valid(form)
        review = ReviewServices(self.request, self.object)
        review.add_review(text=form.cleaned_data["review_content"])

        return response

    def get_success_url(self):
        return reverse("products:product-detail", kwargs={"pk": self.object.pk})


class ProductView(View):
    """
    Представление в котором:
        - при полечении "GET" запроса возвращается ProductDetailView.as_view
        - при полечении "POST" запроса возвращается ProductReviewFormView.as_view
    doc: https://docs.djangoproject.com/en/3.2/topics/class-based-views/mixins/#using-formmixin-with-detailview
    """

    def get(self, request, *args, **kwargs):
        view = ProductDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProductReviewFormView.as_view()
        return view(request, *args, **kwargs)
