import asyncio
import json
from scraping import models
from django.views.generic import TemplateView
from django.http import JsonResponse
from asgiref.sync import sync_to_async

async def scrape_quotes(request):
    urls_to_scrape = "https://quotes.toscrape.com"

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

    quote = data[0]

    author = quote["author"]
    author_obj, created = await sync_to_async(models.Author.objects.get_or_create)(name=author)
    if created:
        author_data = await scrape_author(author)
        if author_data:
            author_data = author_data[0]
        author_obj.name = author_data["name"]
        author_obj.born = author_data["born"]
        author_obj.description = author_data["description"]
        await sync_to_async(author_obj.save)()
    
    quote_obj = models.Quote()
    quote_obj.text = quote["text"]
    quote_obj.author = author_obj
    await sync_to_async(quote_obj.save)()

    tags = quote["tags"]
    for tag in tags:
        tag_obj, created = await sync_to_async(models.Tag.objects.get_or_create)(name=tag)
        await sync_to_async(quote_obj.tags.add)(tag_obj)
        await sync_to_async(quote_obj.save)()
        
    return JsonResponse(quote, safe=False)



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


# 





class HomeView(TemplateView):
    template_name = "index.html"
