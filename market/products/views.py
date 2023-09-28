import random

from django.shortcuts import render  # noqa F401
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from django.urls import reverse

from shops.models import Offer
from .models import Product, Category, Banner
from .services.review_services import ReviewServices
from .services.product_price import product_min_price
from profiles.services.products_history import make_record_in_history
from .forms import ProductReviewForm


class HomeView(TemplateView):
    """Главная страница магазина"""

    template_name = "products/home-page.jinja2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offers"] = Offer.objects.order_by("?")[:8]
        context["min_price_product"] = Offer.objects.all().order_by("price").first()
        min_offers = []
        categories = Category.objects.filter(foreground=True).order_by("?")[:3]
        if len(categories) > 3:
            categories = random.choices(categories, k=3)
        for category in categories:
            min_product = Offer.objects.filter(product__pk=category.pk).order_by("price").first()
            min_offers.append(min_product)
        context["min_offers"] = min_offers
        context["limited_products"] = Offer.objects.all().order_by("quantity")[:8]
        banners = Banner.objects.filter(archived=False).order_by("?")[:3]
        context["banners"] = banners
        return context


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
        context["min_price"] = product_min_price(product=self.object, product_offers=offers)
        context["form"] = ProductReviewForm()
        context["reviews"] = review.get_reviews()
        context["page_obj"] = review.listing(context["reviews"])
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not request.user.is_anonymous:
            make_record_in_history(user=request.user, product=self.object)
        return response


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
