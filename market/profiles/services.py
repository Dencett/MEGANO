from shops.models import Shop


def user_have_store(request):
    user = request.user.pk
    shop = Shop.objects.filter(user__pk=user)
    # if len(shop) > 0:
    #     return shop
    # else:
    return shop
