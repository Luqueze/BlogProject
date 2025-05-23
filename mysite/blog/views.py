from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import CommentForm, EmailPostForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count

from .models import Post

def post_share(request, post_id):
    # Recupera o post pelo ID
    post = get_object_or_404(
        Post,id=post_id,
        status=Post.Status.PUBLISHED
    )
    sent = False
    if request.method == 'POST':
        # O formulário foi enviado
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Campos do formulário passaram na validação
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = (
 f"{cd['name']} ({cd['email']}) "
 f"recommends you read {post.title}"
            )
            message = (
 f"Read {post.title} at {post_url}\n\n"
 f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )

            sent = True

            # ... enviar email
    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )


class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request,tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = []
    except PageNotAnInteger:
        posts = paginator.page(1)
            

    return render(request,'blog/post/list.html',{'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    
    comments = post.comments.filter(active=True)
 
    form = CommentForm()

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form
        }
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,id=post_id,
        status=Post.Status.PUBLISHED
    )
    
    comment = None
    form = CommentForm(data=request.POST)
    
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )

