from django.shortcuts import render

def legal(request):
	return render(request, 'legal.html')
