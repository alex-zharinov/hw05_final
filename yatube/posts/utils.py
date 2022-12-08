from django.core.paginator import Paginator


def paginator(request, post_list, k_post):
    paginator = Paginator(post_list, k_post)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
