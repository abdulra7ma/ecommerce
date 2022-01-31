from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Category, Product


class AllProducts(ListView):
    """ "Return products that are in stock"""

    template_name = "store/index.html"
    queryset = (
        Product.objects.all().prefetch_related("product_image").filter(is_active=True)
    )

    # some_product = queryset.first()
    # some_product.product_image.filter(is_active=True)
    context_object_name = "products"


class CategoryList(DetailView):
    """Return all the products of the selected category."""

    template_name = "store/category.html"

    def get_object(self):
        category_slug = self.kwargs.get("category_slug")
        return get_object_or_404(Category, slug=category_slug)

    def get_queryset(self):
        c_node = Category.objects.get(name=self.kwargs["category_slug"]).is_child_node()
        query_set = Product.objects.filter(
            category__in=Category.objects.get(
                name=self.kwargs["category_slug"]
            ).get_family()
            if not c_node
            else c_node
        )
        print(query_set)
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.get_object
        context["products"] = self.get_queryset
        return context


class ProductDetail(DetailView):
    template_name = "store/single.html"
    context_object_name = "product"

    def get_object(self):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Product, slug=slug, is_active=True)

    def get_queryset(self):
        query_set = Product.objects.filter(
            category__in=Category.objects.get(name="django").get_descendants(
                include_self=True
            )
        )
        return query_set
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wishlist"] = list(Product.objects.filter(users_wishlist=self.request.user))
        print(context['wishlist'])
        return context
