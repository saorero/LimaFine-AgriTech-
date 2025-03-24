from django.shortcuts import render

# Create your views here.

def main(request):
    context = {'message': 'Market Place'}
    return render(request, 'market.html', context)