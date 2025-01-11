from django.shortcuts import render,redirect

from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import InventoryItem
from .forms import InventoryItemForm, CustomUserCreationForm



from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from .models import CustomUser
from django.views.generic.edit import UpdateView, DeleteView




def home(request):
    return render(request, 'pages/home.html')

@login_required
def dashboard(request):
    return render(request, 'stockapp/dashboard.html')


def registration(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
            
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'registration/register.html', {"form": form})

def logout_success(request):
    logout(request)
    return redirect('home')



class InventoryItemListView(LoginRequiredMixin,ListView):
    model = InventoryItem
    template_name = 'pages/item_list.html'
    context_object_name = 'items'
    
    def get_queryset(self):
        # Ensure to fetch only inventory items that belong to the logged-in user
        return InventoryItem.objects.filter(owner=self.request.user)
    
# Create view for inventory items
class InventoryItemCreateView(LoginRequiredMixin,CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'pages/item_form.html'
    success_url = reverse_lazy('inventory-levels')
    def form_valid(self, form):
        # Set the owner of the inventory item to the logged-in user
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    
# Update view for inventory items

class InventoryItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'pages/item_form.html'
    success_url = reverse_lazy('inventory-levels')

    def test_func(self):
        inventory = self.get_object()
        return inventory.owner == self.request.user  # Allow update only for own items



    
class InventoryItemDeleteView(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    model = InventoryItem
    template_name = 'pages/item_confirm_delete.html'
    success_url = reverse_lazy('inventory-levels')
    def test_func(self):
        # Only allow the owner of the inventory to delete it
        inventory = self.get_object()
        return inventory.owner == self.request.user
    
    
    
    
#check for stock level:
from django.views.generic import ListView
from django.db.models import Q
from .models import InventoryItem




from django.views.generic import ListView
from django.core.paginator import Paginator
from .models import InventoryItem


#handling filters
class InventoryLevelsView(ListView):
   
    model = InventoryItem
    template_name = "pages/inventory_levels.html"  # Template to render
    context_object_name = "items"  # Context name in the template
    paginate_by = 10  # Number of items per page

    def get_queryset(self):
       
        # Start with user's own inventory items
        queryset = InventoryItem.objects.filter(owner=self.request.user)

        # Filters from GET request
        category = self.request.GET.get('category')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        low_stock = self.request.GET.get('low_stock')
        order_by = self.request.GET.get('order_by', 'name')  # Default to sorting by Name

        # Apply filters if provided
        if category:
            queryset = queryset.filter(category__icontains=category)
        if price_min:
            queryset = queryset.filter(price__gte=float(price_min))
        if price_max:
            queryset = queryset.filter(price__lte=float(price_max))
        if low_stock:
            try:
                threshold = int(low_stock)
                queryset = queryset.filter(quantity__lt=threshold)
            except ValueError:
                pass  # Ignore invalid low_stock values

        # Apply sorting if the "order_by" parameter is provided
        if order_by == 'name':
            queryset = queryset.order_by('name')
        elif order_by == 'quantity':
            queryset = queryset.order_by('quantity')
        elif order_by == 'price':
            queryset = queryset.order_by('price')
        elif order_by == 'date_added':
            queryset = queryset.order_by('date_added')

        return queryset

    def get_context_data(self, **kwargs):
        """
        Pass extra context to the template, including pagination data and filter options.
        """
        context = super().get_context_data(**kwargs)
        context['filters'] = {
            'category': self.request.GET.get('category', ''),
            'price_min': self.request.GET.get('price_min', ''),
            'price_max': self.request.GET.get('price_max', ''),
            'low_stock': self.request.GET.get('low_stock', ''),
            'order_by': self.request.GET.get('order_by', 'name'),
        }
        return context





from django.shortcuts import get_object_or_404, render

from django.views import View
from .models import InventoryItem, InventoryChangeLog





#changelogs tracking
from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import InventoryChangeLog, InventoryItem

class InventoryChangeLogView(View):
    def get(self, request, item_id):
       
        # Get the specific inventory item and ensure it's owned by the user
        item = get_object_or_404(InventoryItem, pk=item_id, owner=request.user)

        # Get all the change logs related to that item
        change_logs = InventoryChangeLog.objects.filter(inventory_item=item).order_by('-created_at')

        return render(
            request, 
            'pages/inventory_change_log.html',
            {'item': item, 'change_logs': change_logs}
        )




#handling restocking
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import InventoryItem, InventoryChangeLog

class RestockItemView(View):
    def get(self, request):
        items = InventoryItem.objects.filter(owner=request.user)  # Ensure user can only see their own items
        return render(request, 'pages/restock_item.html', {'items': items})

    def post(self, request):
        item_id = request.POST.get('item')
        quantity = request.POST.get('quantity')

        try:
            item = InventoryItem.objects.get(id=item_id, owner=request.user)  # Ensures ownership
            item.quantity += int(quantity)
            item.save()

            # Log the restock change
            InventoryChangeLog.objects.create(
                inventory_item=item,
                action="restock",
                change_quantity=+int(quantity),
                user=request.user
            )
            messages.success(request, f"{item.name} restocked successfully.")
        except (InventoryItem.DoesNotExist, ValueError):
            messages.error(request, "Failed to restock item. Ensure valid input.")

        return redirect('inventory-levels')

#handling selling
class SellItemView(View):
    def get(self, request):
        items = InventoryItem.objects.filter(owner=request.user)
        return render(request, 'pages/sell_item.html', {'items': items})

    def post(self, request):
        item_id = request.POST.get('item')
        quantity = request.POST.get('quantity')

        try:
            item = InventoryItem.objects.get(id=item_id, owner=request.user)
            quantity_to_sell = int(quantity)
            
            if quantity_to_sell > item.quantity:
                messages.error(request, f"Not enough stock for {item.name}.")
            else:
                item.quantity -= quantity_to_sell
                item.save()

                # Log the sale action
                InventoryChangeLog.objects.create(
                    inventory_item=item,
                    action="sale",
                    change_quantity=-quantity_to_sell,
                    user=request.user
                )
                messages.success(request, f"{quantity} of {item.name} sold successfully.")
        except (InventoryItem.DoesNotExist, ValueError):
            messages.error(request, "Failed to sell item. Ensure valid input.")

        return redirect('inventory-levels')


from django.views.generic.base import TemplateView


#handling template to connect manage item sections

class InventoryActionView(TemplateView):
    
    
    template_name = "pages/select_action.html"
    
    


#view for changelog history 



from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import InventoryItem, InventoryChangeLog
from .serializers import InventoryChangeLogSerializer

class InventoryChangeLogByNameTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Fetch and render change logs for an inventory item by name.
        """
        product_name = request.GET.get("product_name", "").strip()

        # Check if product_name is provided
        if not product_name:
            return render(
                request,
                "pages/change_logs.html",
                {"error": "Please provide a valid product name.", "change_logs": None},
            )

        # Fetch the product by name
        
        product = get_object_or_404(InventoryItem, name__iexact=product_name, owner=request.user)

        # Fetch related change logs
        change_logs = InventoryChangeLog.objects.filter(inventory_item=product).order_by("-created_at")
        

        # Serialize logs for template context
        serialized_data = InventoryChangeLogSerializer(change_logs, many=True).data

        # Render template
        return render(
            request,
            "pages/change_logs.html",
            {
                "product": product,
                "change_logs": serialized_data,
            },
        )



#handling templates to check the change logs
class ChangelogsCheckView(TemplateView):
    
    
    template_name = "pages/product_searchlog.html"