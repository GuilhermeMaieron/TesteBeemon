import asyncio
import json
from django.views.generic import TemplateView
from django.http import JsonResponse

async def scrape_hacker_news(request):
    process = await asyncio.create_subprocess_exec(
        'scrapy', 'crawl', 'quotes', '-O', '-:json',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        return JsonResponse({'error': stderr.decode()}, status=500)

    data = json.loads(stdout.decode())
    return JsonResponse(data, safe=False)





class HomeView(TemplateView):
    template_name = "index.html"
