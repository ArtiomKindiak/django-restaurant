from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Ingredient, MenuItem, RecipeRequirement, Purchase
from .forms import IngredientCreateForm, IngredientAddAmountForm, MenuItemCreateForm, PurchaseForm
from django.forms import inlineformset_factory, formset_factory
from django.urls import reverse_lazy
import datetime
from django.http import HttpResponseRedirect
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, 'Inventory/index.html')

@login_required
def home(request):
    today = datetime.date.today()
    ingredients = Ingredient.objects.filter(quantity__lte=1)
    monthly_sales = Purchase.objects.filter(timestamp__month=today.month).values("menu_item__title", "menu_item__price").annotate(sales_by_item=Sum("quantity")).annotate(price=ExpressionWrapper(Sum(F("quantity")) * F("menu_item__price"), output_field=FloatField()))
    yearly_sales = Purchase.objects.filter(timestamp__year=today.year).values("menu_item__title", "menu_item__price").annotate(sales_by_item_yearly=Sum("quantity")).annotate(y_price=ExpressionWrapper(Sum(F("quantity")) * F("menu_item__price"), output_field=FloatField()))

    monthly_revenue = 0
    for item in Purchase.objects.filter(timestamp__month=today.month):
        monthly_revenue += item.total_sum()

    monthly_cost = 0
    for purchase in Purchase.objects.filter(timestamp__month=today.month):
        for recipe_requirement in purchase.menu_item.reciperequirement_set.all():
            monthly_cost += recipe_requirement.ingredient.unit_price * recipe_requirement.quantity * purchase.quantity

    try:
        monthly_profit = monthly_revenue - monthly_cost
    except:
        monthly_profit = 0

    yearly_revenue = 0
    for item in Purchase.objects.filter(timestamp__year=today.year):
        yearly_revenue += item.total_sum()

    yearly_cost = 0
    for purchase in Purchase.objects.filter(timestamp__year=today.year):
        for recipe_requirement in purchase.menu_item.reciperequirement_set.all():
            yearly_cost += recipe_requirement.ingredient.unit_price * recipe_requirement.quantity * purchase.quantity

    try:
        yearly_profit = monthly_revenue - monthly_cost
    except:
        yearly_profit = 0

    context = {"ingredients": ingredients,
               "monthly_sales": monthly_sales,
               "yearly_sales": yearly_sales,
               "current_date": today,
               "monthly_revenue": monthly_revenue,
               "monthly_cost": monthly_cost,
               "monthly_profit": monthly_profit,
               "yearly_revenue": yearly_revenue,
               "yearly_cost": yearly_cost,
               "yearly_profit": yearly_profit}

    return render(request, 'Inventory/home.html', context)


class IngredientListView(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = "Inventory/ingredient_list.html"
    ordering = ['-last_update']

class IngredientCreateView(LoginRequiredMixin, CreateView):
    model = Ingredient
    template_name = "Inventory/ingredient_create.html"
    form_class = IngredientCreateForm
    success_url = reverse_lazy('ingredientlist')

class IngredientDeleteView(LoginRequiredMixin, DeleteView):
    model = Ingredient
    template_name = "Inventory/ingredient_delete.html"
    success_url = reverse_lazy('ingredientlist')

class IngredientUpdateView(LoginRequiredMixin, UpdateView):
    model = Ingredient
    template_name = "Inventory/ingredient_update.html"
    form_class = IngredientCreateForm
    success_url = reverse_lazy('ingredientlist')

@login_required
def add_amount(request, pk):
    queryset = Ingredient.objects.get(id=pk)
    form = IngredientAddAmountForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        if instance.update_price:
            instance.unit_price = (instance.unit_price + instance.update_price) / 2
        instance.quantity += instance.amount_to_add
        instance.save()
        return redirect('ingredientlist')

    context = {
        "queryset": queryset,
        "form": form
    }
    return render(request, "Inventory/ingredient_add.html", context)

class MenuItemListView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = "Inventory/menuitem_list.html"
    ordering = ["-pk"]


class MenuItemCreateView(LoginRequiredMixin, CreateView):
    model = MenuItem
    template_name = "Inventory/menuitem_create.html"
    success_url = reverse_lazy('menuitemlist')
    form_class = MenuItemCreateForm

class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    template_name = "Inventory/menuitem_update.html"
    success_url = reverse_lazy('menuitemlist')
    form_class = MenuItemCreateForm

class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = "Inventory/menuitem_delete.html"
    success_url = reverse_lazy('menuitemlist')

@login_required
def menuitemdetail(request, pk):
    obj = MenuItem.objects.get(id=pk)
    queryset = obj.reciperequirement_set.all()
    total_quantity = 0
    total_cost = 0

    for i in queryset:
        total_quantity += i.quantity
        total_cost += i.cost()

    context = {
        "queryset": queryset,
        "obj": obj,
        "total_quantity": total_quantity,
        "total_cost": total_cost
    }
    return render(request, "Inventory/menuitem_detail.html", context)

@login_required
def add_recipe_requirments(request, pk):
    RecipeRequirementFormSet = inlineformset_factory(MenuItem, RecipeRequirement, fields="__all__", extra=5)
    obj = MenuItem.objects.get(id=pk)
    formset = RecipeRequirementFormSet(instance=obj)
    if request.method == "POST":
        formset = RecipeRequirementFormSet(request.POST, instance=obj)
        if formset.is_valid():
            formset.save()
            return redirect("menuitemdetail", pk=pk)

    context = {"formset": formset}
    return render(request, "Inventory/add_recipe.html", context)

class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = "Inventory/purchase.html"
    ordering = ['-timestamp']

class PurchaseAddView(LoginRequiredMixin, TemplateView):
    template_name = "Inventory/make_purchase.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["menu_items"] = [x for x in MenuItem.objects.all() if x.available()]
        return context

    def post(self, request):
        menu_item_id = request.POST["menu_item"]
        menu_item = MenuItem.objects.get(pk=menu_item_id)
        quantity_p = int(request.POST["quantity"])
        requirements = menu_item.reciperequirement_set
        purchase = Purchase(menu_item=menu_item, quantity=quantity_p)
        for i in range(int(quantity_p)):
            for requirement in requirements.all():
                required_ingredient = requirement.ingredient
                required_ingredient.quantity -= requirement.quantity
                required_ingredient.save()

        purchase.save()
        return redirect(reverse_lazy("purchases"))


@login_required
def purchase_delete(request, pk):
    object = Purchase.objects.get(pk=pk)
    menu_item = MenuItem.objects.get(pk=object.menu_item_id)
    requirements = menu_item.reciperequirement_set
    if request.method == "POST":
        for i in range(object.quantity):
            for requirement in requirements.all():
                required_ingredient = requirement.ingredient
                required_ingredient.quantity += requirement.quantity
                required_ingredient.save()

        object.delete()
        return redirect(reverse_lazy("purchases"))
    context = {"object": object}

    return render(request, "Inventory/purchase_delete.html", context)




class ReportView(LoginRequiredMixin, TemplateView):
    template_name = "Inventory/reports.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.date.today()
        context["purchases"] = Purchase.objects.filter(timestamp__day=today.day)
        total_cost = 0
        for purchase in Purchase.objects.filter(timestamp__day=today.day):
            for recipe_requirement in purchase.menu_item.reciperequirement_set.all():
                total_cost += recipe_requirement.ingredient.unit_price * recipe_requirement.quantity * purchase.quantity

        revenue = 0
        for purchase in Purchase.objects.filter(timestamp__day=today.day):
            revenue += purchase.total_sum()

        context["date"] = today
        context["revenue"] = revenue
        context["total_cost"] = total_cost
        try:
            context["profit"] = revenue - total_cost
        except:
            context["profit"] = 0

        return context


def log_out(request):
    logout(request)
    return redirect("index")