from django.shortcuts import render, get_object_or_404
from business.models import Business
from django.db.models import Q

# Create your views here.
def showbusiness(request):
    query = request.GET.get('q', '')  # default empty string
    businessList = Business.objects.all()

    if query:
        businessList = businessList.filter(
            Q(business_name__icontains=query) |
            Q(category__icontains=query) |   # if ForeignKey
            Q(city__icontains=query)
        )

    return render(request, 'business/showBusiness.html', {
        "businessList": businessList,
        "query": query
    })

def business(request, business_id):
    businessDetails = get_object_or_404(Business, id=business_id)
    return render(request, 'business/business.html', {'businessDetails': businessDetails})