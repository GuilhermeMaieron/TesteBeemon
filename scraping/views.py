import asyncio
import json
from scraping import models
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from asgiref.sync import sync_to_async
import logging
logger = logging.getLogger('scraper')
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from asgiref.sync import async_to_sync

async def scrape_quotes(page, tag):
    urls_to_scrape = "https://quotes.toscrape.com"

    if tag:
        urls_to_scrape += f"/tag/{tag}"
    if page:
        urls_to_scrape += f"/page/{page}/"

    logger.info('Iniciando scraping...')

    logger.info(urls_to_scrape)

    process = await asyncio.create_subprocess_exec(
        'scrapy', 'crawl', 'quotes',
        '-a', f'urls={urls_to_scrape}',
        '-O', '-:json',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        return JsonResponse({'error': stderr.decode()}, status=500)

    data = json.loads(stdout.decode())

    logger.info(f"Total de: {len(data)} Quotes Carregadas...") 

    logger.info(f"Salvando quotes no banco de dados...")
    for quote in data:
        author = quote["author"]
        author_obj, created = await sync_to_async(models.Author.objects.get_or_create)(name=author)
        if created:
            logger.info(f"Fazendo scraping de autor: {author}...")
            author_data = await scrape_author(author)
            logger.info(f"Scraping de {author} concluído...")
            if author_data:
                author_data = author_data[0]
            author_obj.name = author_data["name"]
            author_obj.born = author_data["born"]
            author_obj.description = author_data["description"]
            await sync_to_async(author_obj.save)()
        
        quote_obj = models.Quote(text=quote["text"], author=author_obj)
        await sync_to_async(quote_obj.save)()

        tags = quote["tags"]
        for tag in tags:
            tag_obj, created = await sync_to_async(models.Tag.objects.get_or_create)(name=tag)
            await sync_to_async(quote_obj.tags.add)(tag_obj)
            await sync_to_async(quote_obj.save)()

    logger.info(f"Quotes salvas...")

    return JsonResponse(data, safe=False)



async def scrape_author(name):
    name = name.replace(" ","-")

    urls_to_scrape = f"https://quotes.toscrape.com/author/{name}"
    process = await asyncio.create_subprocess_exec(
        'scrapy', 'crawl', 'author',
        '-a', f'urls={urls_to_scrape}',
        '-O', '-:json',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        return JsonResponse({'error': stderr.decode()}, status=500)

    data = json.loads(stdout.decode())
    
    return data



from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tag = self.request.GET.get('tag')  # Get the tag from the URL

        if tag:
            quotes = models.Quote.objects.filter(tags__name=tag)
            context['selected_tag'] = tag
        else:
            quotes = models.Quote.objects.all()

        context['quotes'] = quotes.order_by("-id")
        context['quotes_count'] = quotes.count()
        context['authors'] = models.Author.objects.all()
        context['tags'] = models.Tag.objects.all()

        return context

    def post(self, request, *args, **kwargs):
        page = request.POST.get('page', None)
        tag = request.POST.get('tag', None)
        if page or tag:
            async_to_sync(scrape_quotes)(page, tag)
        return redirect('home_view') 


class AuthorDetailView(View):
    def get(self, request, name):
        author = get_object_or_404(models.Author, name=name)
        quotes = models.Quote.objects.filter(author=author)
        context = {
            'author': author,
            'quotes': quotes
        }
        return render(request, 'author_detail.html', context)