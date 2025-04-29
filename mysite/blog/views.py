from django.shortcuts import get_object_or_404, render

from .models import Post
def post_detail(request, id):
    post = get_object_or_404(
        Post,
 id=id,
        status=Post.Status.PUBLISHED
    )
    return render(
        request,
        'blog/post/list.html',
        {'posts': post}
    )
