from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/profile/', auth_views.LoginView.as_view(), name='login'),
    path('logout', views.log_out, name='logout'),
    path('home', views.home, name='home'),
    path('ingredient/list', views.IngredientListView.as_view(), name='ingredientlist'),
    path('ingredient/create', views.IngredientCreateView.as_view(), name='ingredientcreate'),
    path('ingredient/<pk>/update', views.IngredientUpdateView.as_view(), name='ingredientupdate'),
    path('ingredient/<pk>/delete', views.IngredientDeleteView.as_view(), name='ingredientdelete'),
    path('ingredient/<pk>/add', views.add_amount, name='ingredientadd'),
    path('menuitem/list', views.MenuItemListView.as_view(), name='menuitemlist'),
    path('menuitem/create', views.MenuItemCreateView.as_view(), name='menuitemcreate'),
    path('menuitem/<pk>/update', views.MenuItemUpdateView.as_view(), name='menuitemupdate'),
    path('menuitem/<pk>/delete', views.MenuItemDeleteView.as_view(), name='menuitemdelete'),
    path('menuitem/<pk>/detail', views.menuitemdetail, name='menuitemdetail'),
    path('menuitem/<pk>/detail/add', views.add_recipe_requirments, name='addrecipe'),
    path('purchases/list', views.PurchaseListView.as_view(), name='purchases'),
    path('purchases/add', views.PurchaseAddView.as_view(), name='addpurchase'),
    path('purchases/<pk>/delete', views.purchase_delete, name='purchasedelete'),
    path('reports', views.ReportView.as_view(), name='reports'),
]