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
import numpy as np
import pandas as pd
import json
from pandas.io.json import json_normalize
from rake_nltk import Rake
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import mean_squared_error
from math import sqrt
pd.set_option('display.max_columns', 100)
from sklearn.metrics.pairwise import cosine_similarity
import operator
import statistics

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
    
   
class PharmacyGet(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request):
        queryset = Pharmacy.objects.filter(owner=request.user)
        serializer_class = PharmacySer(queryset.first())
        return Response(serializer_class.data)
   

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


class PharmacyCheck(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        p = Pharmacy.objects.filter(owner=request.user)
        if p.exists():
            return Response({'status': 'true'})
        else:
            return Response({'status': 'false'})
       



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







def preparationData():
    p = list(Product.objects.all().values())
    rp = list(ReviewProduct.objects.all().values())
    pdf1 = pd.DataFrame(p)
    pdf2 = pd.DataFrame(rp)
    pdf1=pdf1.rename(columns={'id':'productId'}, inplace=False)
    pdf2=pdf2.rename(columns={'product_id':'productId'}, inplace=False)
    result = pd.merge(pdf1, pdf2, on="productId", how="left")
    result=result.drop(columns=['composition','category_id','created_date', 'photo', 'description', 'id', 'manufacturer_id'])
    missing_pivot = result.pivot_table(values='rating', index='author_id', columns='name')
    return {
      'rating_df': pdf2,
      'rating_df2': pdf1,
      'result': result,
      'missing_pivot': missing_pivot
    }


def getTopRecs(result, missing_pivot):
    rate={}
    rows_indexes={}
    for i, row in missing_pivot.iterrows():
        rows= [x for x in range(0,len(missing_pivot.columns))]
        combine= list(zip(row.index, row.values, rows))
        rated= [(x,z) for x,y,z in combine if str(y) !='nan']
        index = [i[1] for i in rated]
        row_names = [i[0] for i in rated]
        rows_indexes[i] = index
        rate[i] = row_names
    missing_pivot = missing_pivot.fillna(0)
    missing_pivot = missing_pivot.apply(np.sign)

    n=5
    cosine_knn = NearestNeighbors(n_neighbors=n, algorithm='brute', metric='cosine')
    item_cosine_knn_fit = cosine_knn.fit(missing_pivot.T.values)
    item_distances, item_indices = item_cosine_knn_fit.kneighbors(missing_pivot.T.values)
    topRecs = {}
    for k,v in rows_indexes.items():
        item_idx = [j for i in item_indices[v] for j in i]
        item_dist = [j for i in item_distances[v] for j in i]
        combine = list(zip(item_dist,item_idx))
        diction = {i:d for d,i in combine if i not in v}
        zipped = list(zip(diction.keys(), diction.values()))
        sort = sorted(zipped, key = lambda x: x[1])
        recommendations = [(missing_pivot.columns[i],d) for i,d in sort]
        topRecs[k] = recommendations
    return topRecs


def similar_users(authorId, matrix, k=3):
  # create a df of just the current user
  user = matrix[matrix.index == authorId]
  
  # and a df of all other users
  other_users = matrix[matrix.index != authorId]
  
  # calc cosine similarity between user and each other user
  similarities = cosine_similarity(user,other_users)[0].tolist()
  
  # create list of indices of these users
  indices = other_users.index.tolist()
  
  # create key/values pairs of user index and their similarity
  index_similarity = dict(zip(indices, similarities))
  
  # sort by similarity
  index_similarity_sorted = sorted(index_similarity.items(), key=operator.itemgetter(1))
  index_similarity_sorted.reverse()
  # grab k users off the top
  top_users_similarities = index_similarity_sorted[:k]
  users = [u[0] for u in top_users_similarities]
  
  return users


def recommend_item(user_index, similar_user_indices, matrix, desc_df, items=5):
    
    # load vectors for similar users
    similar_users = matrix[matrix.index.isin(similar_user_indices)]
    # calc avg ratings across the 3 similar users
    similar_users = similar_users.mean(axis=0)
    # convert to dataframe so its easy to sort and filter
    similar_users_df = pd.DataFrame(similar_users, columns=['mean'])
    
    
    # load vector for the current user
    user_df = matrix[matrix.index == user_index]
    # transpose it so its easier to filter
    user_df_transposed = user_df.transpose()
    # rename the column as 'rating'
    user_df_transposed.columns = ['rating']
    # remove any rows without a 0 value. Anime not watched yet
    user_df_transposed = user_df_transposed[user_df_transposed['rating']==0]
    # generate a list of animes the user has not seen
    products_unseen = user_df_transposed.index.tolist()
    # filter avg ratings of similar users for only anime the current user has not seen
    similar_users_df_filtered = similar_users_df[similar_users_df.index.isin(products_unseen)]
    # order the dataframe
    similar_users_df_ordered = similar_users_df.sort_values(by=['mean'], ascending=False)
    # grab the top n anime   
    top_n_products = similar_users_df_ordered.head(items)
    top_n_products_indices = top_n_products.index.tolist()
    # lookup these anime in the other dataframe to find names
    product_information = desc_df[desc_df['productId'].isin(top_n_products_indices)]
    return product_information #items


def getUserBased(desc_df, rating_df):
    ratings_per_prod = rating_df.groupby('productId')['rating'].count()
    statistics.mean(ratings_per_prod.tolist())

    ratings_per_user = rating_df.groupby('author_id')['rating'].count()
    statistics.mean(ratings_per_user.tolist())

    rating_per_prod_df = pd.DataFrame (ratings_per_prod)
    # удалить, если <1000 оценок 
    filter_ratings_per_prod_df = rating_per_prod_df [rating_per_prod_df.rating>=2]
    # создать список anime_id, чтобы сохранить 
    Popular_prod = filter_ratings_per_prod_df.index.tolist ()
    # считает оценки на пользователя как df 
    rating_per_user_df = pd.DataFrame (ratings_per_user)
    # remove if <500 
    filter_ratings_per_user_df = rating_per_user_df [rating_per_user_df.rating>=5]
    # создать список user_ids, чтобы сохранить 
    prolific_users = filter_ratings_per_user_df.index.tolist ()
    filtered_ratings = rating_df[rating_df.productId.isin(Popular_prod)]
    iltered_ratings = rating_df[rating_df.author_id.isin(prolific_users)]

    rating_matrix = filtered_ratings.pivot_table(index='author_id', columns='productId', values='rating')
    # replace NaN values with 0
    rating_matrix = rating_matrix.fillna(0)
    current_user = 9.0
    similar_user_indices = similar_users(current_user, rating_matrix)
    r = recommend_item(current_user, similar_user_indices, rating_matrix, desc_df)
    return r

class getSimilarProduct(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        queryset = []
        a = preparationData()
        rating_df = a['rating_df']
        desc_df = a['rating_df2']
        result = a['result']
        missing_pivot = a['missing_pivot']
        topr = getTopRecs(result, missing_pivot)
        sim = getUserBased(desc_df, rating_df)
        for i in sim.index:
          # print(sim['productId'][i])
          p = Product.objects.get(id=sim['productId'][i])
          queryset.append(p)
        if float(request.user.id) in topr:
          for i in topr[float(request.user.id)][:30]:
            p = Product.objects.get(name=i[0])
            queryset.append(p)
        s = ProductSer(queryset, many=True, context={'request': request})
        return Response(s.data)
