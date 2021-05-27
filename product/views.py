from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from .serializers import *
import random
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from users.models import User
from categories.models import Category
from .models import *
from django.db.models import Count

class getProduct(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny,]
    queryset = Product.objects.all()
    serializer_class = ProductSer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ('name', 'description')
    filter_fields = ('category', )
    

class PharmacyS(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny,]
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ('name',)
   


class createProduct(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        s = CreateProductSer(data=request.data)
        if s.is_valid():
            p = Product.objects.create(
                name = s.validated_data['name'],
                manufacturer = Manufacture.objects.get(id=s.validated_data['manufacturer']),
                description = s.validated_data['description'],
                composition = s.validated_data['composition'],
                category = Category.objects.get(id = s.validated_data['category']),
                photo = s.validated_data['photo']
            )
            c = CountProduct.objects.create(
                product = p,
                pharmacy = request.user.my_pharmacy.all()[0],
                price = s.validated_data['price'],
                count = s.validated_data['count']
            )
            return Response({'status': 'ok'})
        else:
            return Response(s.errors)



class PharmacyApi(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        s = PharmacySer(data=request.data)
        if s.is_valid():
            p = Pharmacy.objects.create(
                name = s.validated_data['name'],
                owner = request.user,
                address = s.validated_data['address'],
                working_hours = s.validated_data['working_hours'],
                city = s.validated_data['city'],
                phone = s.validated_data['phone'],
                photo = s.validated_data['photo']
            )
            return Response({'status': 'ok'})
        else:
             return Response(s.errors)



class Accounting(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = Pharmacy.objects.get(owner=request.user)
        queryset = CountProduct.objects.filter(pharmacy = user)
        s = CountProductSer3(queryset, many=True, context={'request': request})
        return Response(s.data)


class ReviewApi(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        queryset = Review.objects.filter(pharmacy__id = id)
        s = ReviewSer(queryset, many=True)
        return Response(s.data)


class CreateReview(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        s = CreateReviewSer(data=request.data)
        if s.is_valid():
            Review.objects.create(
                text = s.validated_data['text'],
                author = request.user,
                pharmacy = s.validated_data['pharmacy'],
                rating = s.validated_data['rating']
            )
            return Response({'status': 'ok'})
        else:
            return Response(s.errors)

    
class ReviewProductApi(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        queryset = ReviewProduct.objects.filter(product__id = id)
        s = ReviewProductSer(queryset, many=True)
        return Response(s.data)


class CreateProductReview(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        s = CreateReviewProductSer(data=request.data)
        if s.is_valid():
            ReviewProduct.objects.create(
                text = s.validated_data['text'],
                author = request.user,
                product = s.validated_data['product'],
                rating = s.validated_data['rating']
            )
            return Response({'status': 'ok'})
        else:
            return Response(s.errors)


class Recomendation(APIView):
    permission_classes = [permissions.AllowAny,]
    
    def get(self, request):
        q = Product.objects.annotate(num_comment=Count('review_product')).order_by('-num_comment')[:10]
        s = ProductSer(q, many=True, context={'request': request})
        return Response(s.data)


class favorites(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        queryset = request.user.favorites.all()
        s = ProductSer(queryset, many = True, context={'request': request})
        return Response(s.data)

    def post(self, request):
        s = productIdSer(data=request.data)
        if s.is_valid():
            product = Product.objects.get(id=s.validated_data['id'])
            if product in request.user.favorites.all():
                request.user.favorites.remove(product)
            else:
                request.user.favorites.add(product)
            return Response({'status': 'ok'})
        else:
            return Response(s.errors)



# import numpy as np
# import pandas as pd
# import json
# from pandas.io.json import json_normalize
# from rake_nltk import Rake
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.neighbors import NearestNeighbors
# from sklearn.metrics import mean_squared_error
# from math import sqrt
# pd.set_option('display.max_columns', 100)
# f = open(r'../agregator.json',encoding='UTF8')
# data = json.load(f)
# df = pd.io.json.json_normalize(data)

def preparationData():
    rating_df=rating_df.rename(columns={'fields.author':'authorId', 'fields.rating':'Rating', 'fields.text':'Review','fields.product':'productId'}, inplace=False)
    rating_df=rating_df.loc[rating_df['model'] == 'product.reviewproduct']
    desc_df=df[['model', 'pk', 'fields.name']]
    desc_df=desc_df.loc[desc_df['model'] == 'product.product']
    desc_df=desc_df.rename(columns={'pk':'productId', 'fields.name':'title'}, inplace=False)
    result = pd.merge(rating_df, desc_df, on="productId", how="left")
    result=result.drop(columns=['pk','model_x','model_y'])
    missing_pivot = result.pivot_table(values='Rating', index='authorId', columns='title')
    return {
        'missing_pivot': missing_pivot,
        'result': result
    }


def getRate():
    rate={}
    missing_pivot = preparationData()['missing_pivot']
    rows_indexes={}
    for i, row in missing_pivot.iterrows():
        rows= [x for x in range(0,len(missing_pivot.columns))]
        combine= list(zip(row.index, row.values, rows))
        rated= [(x,z) for x,y,z in combine if str(y) !='nan']
        index = [i[1] for i in rated]
        row_names = [i[0] for i in rated]
        rows_indexes[i] = index
        rate[i] = row_names
    return {
        'rate': rate,
        'rows_indexes': rows_indexes
    }

def topRecs():
    result = preparationData()['result']
    pivot_table = result.pivot_table(values= 'Rating', index='authorId', columns='title').fillna(0)
    pivot_table = pivot_table.apply(np.sign)
    n=5
    cosine_knn = NearestNeighbors(n_neighbors=n, algorithm='brute', metric='cosine')
    item_cosine_knn_fit = cosine_knn.fit(pivot_table.T.values)
    item_distances, item_indices = item_cosine_knn_fit.kneighbors(pivot_table.T.values)

    items_dic = {}
    for i in range(len(pivot_table.T.index)):
        item_idx = item_indices[i]
        col_names = pivot_table.T.index[item_idx].tolist()
        items_dic[pivot_table.T.index[i]] = col_names
    topRecs = {}
    for k,v in preparationData()['rows_indexes'].items():
        item_idx = [j for i in item_indices[v] for j in i]
        item_dist = [j for i in item_distances[v] for j in i]
        combine = list(zip(item_dist,item_idx))
        diction = {i:d for d,i in combine if i not in v}
        zipped = list(zip(diction.keys(), diction.values()))
        sort = sorted(zipped, key = lambda x: x[1])
        recommendations = [(pivot_table.columns[i],d) for i,d in sort]
        topRecs[k] = recommendations
    return topRecs

def getrecommendations(user, number_of_recs = 30):
    print("Сіз өткенде бұрында көрген өнім: \n\n{}".format('\n'.join(rate[user])))
    print()
    print("Мына өнімдерді де қараңыз:\n")
    for k,v in topRecs().items():
        if user == k:
            for i in v[:number_of_recs]:
                print('{} ұқсастық: {:.4f}'.format(i[0], 1-i[1]))