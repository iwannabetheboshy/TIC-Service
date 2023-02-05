from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm
from django.http import HttpResponseRedirect
import sqlite3
import math
import mimetypes
import os
from .forms import ContactForm, SearchForm
from collections import Counter


def download_file(request):
    filename = request.GET['filename']
    if filename != '':
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = BASE_DIR + '/' + filename
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    else:
        return render(request, 'accounts/login.html')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('ce')#, {'username': username, })
                else:
                    return HttpResponse('Disabled account')
            else:
                messages.error(request, 'Неверный логин и/или пароль.')
                return render(request, 'accounts/login.html', {'form': form})
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})
    
def index(request):
    if request.user.is_authenticated == True:
    
        form = ContactForm(request.POST)
        if form.is_valid():
            trip_advisor = form.cleaned_data['trip_advisor']
            booking = form.cleaned_data['booking']
            vlru = form.cleaned_data['vlru']
            gis = form.cleaned_data['gis']
            google = form.cleaned_data['google']
            
            print(google)

        form = ContactForm()
        
        connection = sqlite3.connect('eat.db')
        cursor = connection.cursor()

        #----------------
        # Общее количество Компаний
        # ----------------
        cursor.execute("SELECT Count() FROM vl")
        vl_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM gis")
        gis_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM trip")
        trip_count = cursor.fetchone()[0]
        total_count = vl_count + gis_count + trip_count
        total_count = [(gis_count * 100) // total_count, (vl_count * 100) // total_count, (trip_count * 100) // total_count]

        # ----------------
        # Рубрики
        # ----------------
        cursor.execute("SELECT rubric FROM gis")
        rubrics_gis = cursor.fetchall()
        cursor.execute("SELECT rubric FROM vl")
        rubrics_vl = cursor.fetchall()
        cursor.execute("SELECT rubric FROM trip")
        rubrics_trip = cursor.fetchall()

        def sum_rubrics(db_rubrics):
            rubrics = {
                               'Кафе': [0, 0], 'Рестораны': [0, 0], 'Бары': [0, 0],
                               'Доставка готовых блюд': [0, 0], 'Суши-бары': [0, 0], 'Быстрое питание': [0, 0],
                               'Пиццерии': [0, 0], 'Столовые': [0, 0], 'Кофейни': [0, 0],
                               'Точки кофе': [0, 0], 'Кафе-кондитерские': [0, 0], 'Кейтеринг': [0, 0],
                               'Чайные клубы': [0, 0], 'Рюмочные': [0, 0], 'Китайская кухня': [0, 0],
                           }
            
            rubrics_count = 0
            for item in db_rubrics:
                for i in item[0].split('; '):
                    for j in rubrics:
                        if i == j:
                            rubrics[j][0] += 1
                            rubrics_count += 1
                            break
            for item in rubrics:
                rubrics[item][1] = '%.2f' %((rubrics[item][0] * 100) / rubrics_count)

            return rubrics

        rubrics_all = sum_rubrics(rubrics_gis + rubrics_vl + rubrics_trip)
        rubrics_gis = sum_rubrics(rubrics_gis)
        rubrics_vl = sum_rubrics(rubrics_vl)
        rubrics_trip = sum_rubrics(rubrics_trip)


        # ----------------
        # АТЕ Компаний
        # ----------------
        cursor.execute("SELECT city FROM gis")
        city_gis = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_gis)):
            if 'городской' in city_gis[i]:
                city_gis[i] = city_gis[i].replace(' городской', '')        
        city_gis = Counter(city_gis)
        
        cursor.execute("SELECT city FROM vl")
        city_vl = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_vl)):
            if 'городской' in city_vl[i]:
                city_vl[i] = city_vl[i].replace(' городской', '')
        city_vl = Counter(city_vl)
        
        cursor.execute("SELECT city FROM trip")
        city_trip = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_trip)):
            if 'городской' in city_trip[i]:
                city_trip[i] = city_trip[i].replace(' городской', '')
        city_trip = Counter(city_trip)
        
        city_all = city_gis + city_vl + city_trip
        city_all = dict(Counter(city_all))

        for i in city_all:
            city_all[i] = [city_all[i], '%.2f' %((city_all[i] * 100) / (gis_count + vl_count + trip_count))]
            
        city_gis = dict(city_gis)
        for i in city_gis:
            city_gis[i] = [city_gis[i], '%.2f' %((city_gis[i] * 100) / gis_count)]
        
        city_vl = dict(city_vl)
        for i in city_vl:
            city_vl[i] = [city_vl[i], '%.2f' %((city_vl[i] * 100) / vl_count)]

        
        city_trip = dict(city_trip)
        for i in city_trip:
            city_trip[i] = [city_trip[i], '%.2f' %((city_trip[i] * 100) / trip_count)]
            
        sorted_city_gis = sorted(city_gis.items(), key=lambda item: item[1][0])
        sorted_city_gis = {k: v for k, v in sorted_city_gis[-5:]}
        count_other_city = 0
        for i in sorted_city_gis:
            count_other_city += sorted_city_gis[i][0]
        sorted_city_gis['Остальное'] = [gis_count - count_other_city]
        
        sorted_city_vl = sorted(city_vl.items(), key=lambda item: item[1][0])
        sorted_city_vl = {k: v for k, v in sorted_city_vl[-5:]}
        count_other_city = 0
        for i in sorted_city_vl:
            count_other_city += sorted_city_vl[i][0]
        sorted_city_vl['Остальное'] = [vl_count - count_other_city]
        
        sorted_city_trip = sorted(city_trip.items(), key=lambda item: item[1][0])
        sorted_city_trip = {k: v for k, v in sorted_city_trip[-5:]}
        count_other_city = 0
        for i in sorted_city_trip:
            count_other_city += sorted_city_trip[i][0]
        sorted_city_trip['Остальное'] = [trip_count - count_other_city]
        
        sorted_city_all = sorted(city_all.items(), key=lambda item: item[1][0])
        sorted_city_all = {k: v for k, v in sorted_city_all[-5:]}
        count_other_city = 0
        for i in sorted_city_all:
            count_other_city += sorted_city_all[i][0]
        sorted_city_all['Остальное'] = [gis_count + vl_count + trip_count - count_other_city]
        

        connection.close()

        # ----------------
        # Общее количество Отзывов
        # ----------------
        connection = sqlite3.connect('reviews_eat.db')
        cursor = connection.cursor()
        cursor.execute("SELECT Count() FROM vl")
        vl_reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM gis")
        gis_reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM trip")
        trip_reviews_count = cursor.fetchone()[0]
        
        total_reviews_count = vl_reviews_count + gis_reviews_count + trip_reviews_count
        total_reviews_count = [(gis_reviews_count * 100) // total_reviews_count, (vl_reviews_count * 100) // total_reviews_count, (trip_reviews_count * 100) // total_reviews_count]

        cursor.execute("SELECT rating FROM gis")
        rating_gis = sorted([str(i[0]) for i in cursor.fetchall()])
        rating_gis = Counter(rating_gis)

        cursor.execute("SELECT rating FROM vl")
        rating_vl = sorted([str(i[0]) for i in cursor.fetchall() if str(i[0]) != '1.2'])
        rating_vl = Counter(rating_vl)
        
        cursor.execute("SELECT rating FROM trip")
        rating_trip = sorted([str(i[0]) for i in cursor.fetchall()])
        rating_trip = Counter(rating_trip)
        
        rating_all = Counter(rating_gis + rating_vl + rating_trip)
        rating_all = dict(rating_all)
        for i in rating_all:
            rating_all[i] = [rating_all[i], '%.2f' %((rating_all[i] * 100) / (gis_reviews_count+vl_reviews_count+trip_reviews_count))]


        rating_gis = dict(rating_gis)
        for i in rating_gis:
            rating_gis[i] = [rating_gis[i], '%.2f' %((rating_gis[i] * 100) / gis_reviews_count)]

        
        rating_vl = dict(rating_vl)
        for i in rating_vl:
            rating_vl[i] = [rating_vl[i], '%.2f' %((rating_vl[i] * 100) / vl_reviews_count)]

       
        rating_trip = dict(rating_trip)
        for i in rating_trip:
            rating_trip[i] = [rating_trip[i], '%.2f' %((rating_trip[i] * 100) / trip_reviews_count)]
        
        cursor.execute("SELECT date FROM gis")
        year_gis = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_gis = Counter(year_gis)
        
        cursor.execute("SELECT date FROM vl")
        year_vl = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_vl = Counter(year_vl)
        
        cursor.execute("SELECT date FROM trip")
        year_trip = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_trip = Counter(year_trip)
        
        year_all = Counter(year_gis + year_vl + year_trip)
        year_all = year_all.most_common()
        year_all = dict(year_all)
        
        for i in year_all:
            year_all[i] = [year_all[i], '%.2f' % ((year_all[i] * 100) / (gis_reviews_count + vl_reviews_count + trip_reviews_count))]

        year_gis = dict(year_gis)
        for i in year_gis:
            year_gis[i] = [year_gis[i], '%.2f' %((year_gis[i] * 100) / gis_reviews_count)]
        
        year_vl = dict(year_vl)
        for i in year_vl:
            year_vl[i] = [year_vl[i], '%.2f' % ((year_vl[i] * 100) / vl_reviews_count)]

        year_trip = dict(year_trip)
        for i in year_trip:
            year_trip[i] = [year_trip[i], '%.2f' % ((year_trip[i] * 100) / trip_reviews_count)]


        connection.close()

        return render(request, 'accounts/index.html', {'companies': 
                                                        {
                                                            'gis': [gis_count, total_count[0], round(total_count[0] / 10) * 10],
                                                            'vl': [vl_count, total_count[1], round(total_count[1] / 10) * 10],
                                                            'trip': [trip_count, total_count[2], round(total_count[2] / 10) * 10],
                                                        },
                                                        
                                                       'reviews': 
                                                        {
                                                            'gis': [gis_reviews_count, total_reviews_count[0], round(total_reviews_count[0] / 10) * 10],
                                                            'vl': [vl_reviews_count, total_reviews_count[1], round(total_reviews_count[1] / 10) * 10],
                                                            'trip': [trip_reviews_count, total_reviews_count[2], round(total_reviews_count[2] / 10) * 10],
                                                        },
                                                       'city':
                                                           {
                                                               'all': city_all,
                                                               'gis': city_gis,
                                                               'vl': city_vl,
                                                               'trip': city_trip,
                                                           },
                                                        'sorted_city':
                                                           {
                                                               'all': sorted_city_all,
                                                               'gis': sorted_city_gis,
                                                               'vl': sorted_city_vl,
                                                               'trip': sorted_city_trip,
                                                           },
                                                       'rubrics' :
                                                           {
                                                               'all': rubrics_all,
                                                               'gis': rubrics_gis,
                                                               'vl': rubrics_vl,
                                                               'trip': rubrics_trip
                                                           },
                                                       'rating' :
                                                           {
                                                               'all': rating_all,
                                                               'gis': rating_gis,
                                                               'vl': rating_vl,
                                                               'trip': rating_trip,
                                                           },
                                                       'years' :
                                                           {
                                                               'all': year_all,
                                                               'gis': year_gis,
                                                               'vl': year_vl,
                                                               'trip': year_trip,
                                                           },
                                                       'db_nane': 'eat',
                                                       'page_name': 'Предприятия общественного питания',

                                                       'user_name': request.user.username,
                                                       'form': form,
                                                      }
                      )
    
    else:
        return HttpResponseRedirect('')


def caf(request):
    if request.user.is_authenticated == True:
    
        form = ContactForm(request.POST)
        if form.is_valid():
            trip_advisor = form.cleaned_data['trip_advisor']
            booking = form.cleaned_data['booking']
            vlru = form.cleaned_data['vlru']
            gis = form.cleaned_data['gis']
            google = form.cleaned_data['google']
            
            print(google)

        form = ContactForm()
        
        connection = sqlite3.connect('hotel.db')
        cursor = connection.cursor()

        #----------------
        # Общее количество Компаний
        # ----------------
        cursor.execute("SELECT Count() FROM vl")
        vl_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM gis")
        gis_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM trip")
        trip_count = cursor.fetchone()[0]
        total_count = vl_count + gis_count + trip_count
        total_count = [(gis_count * 100) // total_count, (vl_count * 100) // total_count, (trip_count * 100) // total_count]

        # ----------------
        # Рубрики
        # ----------------
        cursor.execute("SELECT rubric FROM gis")
        rubrics_gis = cursor.fetchall()
        cursor.execute("SELECT rubric FROM vl")
        rubrics_vl = cursor.fetchall()
        cursor.execute("SELECT rubric FROM trip")
        rubrics_trip = cursor.fetchall()

        def sum_rubrics(db_rubrics):
            rubrics = {
                'Базы отдыха': [0, 0], 'Гостиницы, отели': [0, 0], 'Санатории/Профилактории': [0, 0], 'Хостелы': [0, 0],
            }            

            rubrics_count = 0
            for item in db_rubrics:
                for i in item[0].split('; '):
                    for j in rubrics:
                        if i == j:
                            rubrics[j][0] += 1
                            rubrics_count += 1
                            break
            for item in rubrics:
                rubrics[item][1] = '%.2f' %((rubrics[item][0] * 100) / rubrics_count)

            return rubrics

        rubrics_all = sum_rubrics(rubrics_gis + rubrics_vl + rubrics_trip)
        rubrics_gis = sum_rubrics(rubrics_gis)
        rubrics_vl = sum_rubrics(rubrics_vl)
        rubrics_trip = sum_rubrics(rubrics_trip)


        # ----------------
        # АТЕ Компаний
        # ----------------
        cursor.execute("SELECT city FROM gis")
        city_gis = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_gis)):
            if 'городской' in city_gis[i]:
                city_gis[i] = city_gis[i].replace(' городской', '')        
        city_gis = Counter(city_gis)
        
        cursor.execute("SELECT city FROM vl")
        city_vl = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_vl)):
            if 'городской' in city_vl[i]:
                city_vl[i] = city_vl[i].replace(' городской', '')
        city_vl = Counter(city_vl)
        
        cursor.execute("SELECT city FROM trip")
        city_trip = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_trip)):
            if 'городской' in city_trip[i]:
                city_trip[i] = city_trip[i].replace(' городской', '')
        city_trip = Counter(city_trip)
        
        city_all = city_gis + city_vl + city_trip
        city_all = dict(Counter(city_all))

        for i in city_all:
            city_all[i] = [city_all[i], '%.2f' %((city_all[i] * 100) / (gis_count + vl_count + trip_count))]
            
        city_gis = dict(city_gis)
        for i in city_gis:
            city_gis[i] = [city_gis[i], '%.2f' %((city_gis[i] * 100) / gis_count)]
        
        city_vl = dict(city_vl)
        for i in city_vl:
            city_vl[i] = [city_vl[i], '%.2f' %((city_vl[i] * 100) / vl_count)]

        
        city_trip = dict(city_trip)
        for i in city_trip:
            city_trip[i] = [city_trip[i], '%.2f' %((city_trip[i] * 100) / trip_count)]
            
        sorted_city_gis = sorted(city_gis.items(), key=lambda item: item[1][0])
        sorted_city_gis = {k: v for k, v in sorted_city_gis[-5:]}
        count_other_city = 0
        for i in sorted_city_gis:
            count_other_city += sorted_city_gis[i][0]
        sorted_city_gis['Остальное'] = [gis_count - count_other_city]
        
        sorted_city_vl = sorted(city_vl.items(), key=lambda item: item[1][0])
        sorted_city_vl = {k: v for k, v in sorted_city_vl[-5:]}
        count_other_city = 0
        for i in sorted_city_vl:
            count_other_city += sorted_city_vl[i][0]
        sorted_city_vl['Остальное'] = [vl_count - count_other_city]
        
        sorted_city_trip = sorted(city_trip.items(), key=lambda item: item[1][0])
        sorted_city_trip = {k: v for k, v in sorted_city_trip[-5:]}
        count_other_city = 0
        for i in sorted_city_trip:
            count_other_city += sorted_city_trip[i][0]
        sorted_city_trip['Остальное'] = [trip_count - count_other_city]
        
        sorted_city_all = sorted(city_all.items(), key=lambda item: item[1][0])
        sorted_city_all = {k: v for k, v in sorted_city_all[-5:]}
        count_other_city = 0
        for i in sorted_city_all:
            count_other_city += sorted_city_all[i][0]
        sorted_city_all['Остальное'] = [gis_count + vl_count + trip_count - count_other_city]
        

        connection.close()

        # ----------------
        # Общее количество Отзывов
        # ----------------
        connection = sqlite3.connect('reviews_hotel.db')
        cursor = connection.cursor()
        cursor.execute("SELECT Count() FROM vl")
        vl_reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM gis")
        gis_reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM trip")
        trip_reviews_count = cursor.fetchone()[0]
        
        total_reviews_count = vl_reviews_count + gis_reviews_count + trip_reviews_count
        total_reviews_count = [(gis_reviews_count * 100) // total_reviews_count, (vl_reviews_count * 100) // total_reviews_count, (trip_reviews_count * 100) // total_reviews_count]

        cursor.execute("SELECT rating FROM gis")
        rating_gis = sorted([str(i[0]) for i in cursor.fetchall()])
        rating_gis = Counter(rating_gis)

        cursor.execute("SELECT rating FROM vl")
        rating_vl = sorted([str(i[0]) for i in cursor.fetchall() if str(i[0]) != '1.2'])
        rating_vl = Counter(rating_vl)
        
        cursor.execute("SELECT rating FROM trip")
        rating_trip = sorted([str(i[0]) for i in cursor.fetchall()])
        rating_trip = Counter(rating_trip)
        
        rating_all = Counter(rating_gis + rating_vl + rating_trip)
        rating_all = dict(rating_all)
        for i in rating_all:
            rating_all[i] = [rating_all[i], '%.2f' %((rating_all[i] * 100) / (gis_reviews_count+vl_reviews_count+trip_reviews_count))]


        rating_gis = dict(rating_gis)
        for i in rating_gis:
            rating_gis[i] = [rating_gis[i], '%.2f' %((rating_gis[i] * 100) / gis_reviews_count)]

        
        rating_vl = dict(rating_vl)
        for i in rating_vl:
            rating_vl[i] = [rating_vl[i], '%.2f' %((rating_vl[i] * 100) / vl_reviews_count)]

       
        rating_trip = dict(rating_trip)
        for i in rating_trip:
            rating_trip[i] = [rating_trip[i], '%.2f' %((rating_trip[i] * 100) / trip_reviews_count)]
        
        cursor.execute("SELECT date FROM gis")
        year_gis = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_gis = Counter(year_gis)
        
        cursor.execute("SELECT date FROM vl")
        year_vl = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_vl = Counter(year_vl)
        
        cursor.execute("SELECT date FROM trip")
        year_trip = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_trip = Counter(year_trip)
        
        year_all = Counter(year_gis + year_vl + year_trip)
        year_all = year_all.most_common()
        year_all = dict(year_all)
        
        for i in year_all:
            year_all[i] = [year_all[i], '%.2f' % ((year_all[i] * 100) / (gis_reviews_count + vl_reviews_count + trip_reviews_count))]

        year_gis = dict(year_gis)
        for i in year_gis:
            year_gis[i] = [year_gis[i], '%.2f' %((year_gis[i] * 100) / gis_reviews_count)]
        
        year_vl = dict(year_vl)
        for i in year_vl:
            year_vl[i] = [year_vl[i], '%.2f' % ((year_vl[i] * 100) / vl_reviews_count)]

        year_trip = dict(year_trip)
        for i in year_trip:
            year_trip[i] = [year_trip[i], '%.2f' % ((year_trip[i] * 100) / trip_reviews_count)]


        connection.close()

        return render(request, 'accounts/index.html', {'companies': 
                                                        {
                                                            'gis': [gis_count, total_count[0], round(total_count[0] / 10) * 10],
                                                            'vl': [vl_count, total_count[1], round(total_count[1] / 10) * 10],
                                                            'trip': [trip_count, total_count[2], round(total_count[2] / 10) * 10],
                                                        },
                                                        
                                                       'reviews': 
                                                        {
                                                            'gis': [gis_reviews_count, total_reviews_count[0], round(total_reviews_count[0] / 10) * 10],
                                                            'vl': [vl_reviews_count, total_reviews_count[1], round(total_reviews_count[1] / 10) * 10],
                                                            'trip': [trip_reviews_count, total_reviews_count[2], round(total_reviews_count[2] / 10) * 10],
                                                        },
                                                       'city':
                                                           {
                                                               'all': city_all,
                                                               'gis': city_gis,
                                                               'vl': city_vl,
                                                               'trip': city_trip,
                                                           },
                                                        'sorted_city':
                                                           {
                                                               'all': sorted_city_all,
                                                               'gis': sorted_city_gis,
                                                               'vl': sorted_city_vl,
                                                               'trip': sorted_city_trip,
                                                           },
                                                       'rubrics' :
                                                           {
                                                               'all': rubrics_all,
                                                               'gis': rubrics_gis,
                                                               'vl': rubrics_vl,
                                                               'trip': rubrics_trip
                                                           },
                                                       'rating' :
                                                           {
                                                               'all': rating_all,
                                                               'gis': rating_gis,
                                                               'vl': rating_vl,
                                                               'trip': rating_trip,
                                                           },
                                                       'years' :
                                                           {
                                                               'all': year_all,
                                                               'gis': year_gis,
                                                               'vl': year_vl,
                                                               'trip': year_trip,
                                                           },

                                                       'user_name': request.user.username,
                                                       'db_nane': 'hotel',
                                                       'page_name': 'Коллективные средства размещения',
                                                       'form': form,
                                                      }
                      )
    
    else:
        return HttpResponseRedirect('')


def tour(request):
    if request.user.is_authenticated == True:
    
        form = ContactForm(request.POST)
        if form.is_valid():
            trip_advisor = form.cleaned_data['trip_advisor']
            booking = form.cleaned_data['booking']
            vlru = form.cleaned_data['vlru']
            gis = form.cleaned_data['gis']
            google = form.cleaned_data['google']
            
            print(google)

        form = ContactForm()
        
        connection = sqlite3.connect('tourism.db')
        cursor = connection.cursor()

        #----------------
        # Общее количество Компаний
        # ----------------
        cursor.execute("SELECT Count() FROM vl")
        vl_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM gis")
        gis_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM trip")
        trip_count = cursor.fetchone()[0]
        total_count = vl_count + gis_count + trip_count
        total_count = [(gis_count * 100) // total_count, (vl_count * 100) // total_count, (trip_count * 100) // total_count]

        # ----------------
        # Рубрики
        # ----------------
        cursor.execute("SELECT rubric FROM gis")
        rubrics_gis = cursor.fetchall()
        cursor.execute("SELECT rubric FROM vl")
        rubrics_vl = cursor.fetchall()
        cursor.execute("SELECT rubric FROM trip")
        rubrics_trip = cursor.fetchall()

        def sum_rubrics(db_rubrics):
            rubrics = {
                'Турфирмы': [0, 0], 'Оформление виз': [0, 0], 'Авиабилеты': [0, 0], 
                'Организация экскурсий': [0, 0], 'Бронирование гостиниц': [0, 0], 'Железнодорожные билеты': [0, 0], 
                'Справочные службы': [0, 0], 
            }          

            rubrics_count = 0
            for item in db_rubrics:
                for i in item[0].split('; '):
                    for j in rubrics:
                        if i == j:
                            rubrics[j][0] += 1
                            rubrics_count += 1
                            break
            for item in rubrics:
                rubrics[item][1] = '%.2f' %((rubrics[item][0] * 100) / rubrics_count)

            return rubrics

        rubrics_all = sum_rubrics(rubrics_gis + rubrics_vl + rubrics_trip)
        rubrics_gis = sum_rubrics(rubrics_gis)
        rubrics_vl = sum_rubrics(rubrics_vl)
        rubrics_trip = sum_rubrics(rubrics_trip)


        # ----------------
        # АТЕ Компаний
        # ----------------
        cursor.execute("SELECT city FROM gis")
        city_gis = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_gis)):
            if 'городской' in city_gis[i]:
                city_gis[i] = city_gis[i].replace(' городской', '')        
        city_gis = Counter(city_gis)
        
        cursor.execute("SELECT city FROM vl")
        city_vl = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_vl)):
            if 'городской' in city_vl[i]:
                city_vl[i] = city_vl[i].replace(' городской', '')
        city_vl = Counter(city_vl)
        
        cursor.execute("SELECT city FROM trip")
        city_trip = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_trip)):
            if 'городской' in city_trip[i]:
                city_trip[i] = city_trip[i].replace(' городской', '')
        city_trip = Counter(city_trip)
        
        city_all = city_gis + city_vl + city_trip
        city_all = dict(Counter(city_all))

        for i in city_all:
            city_all[i] = [city_all[i], '%.2f' %((city_all[i] * 100) / (gis_count + vl_count + trip_count))]
            
        city_gis = dict(city_gis)
        for i in city_gis:
            city_gis[i] = [city_gis[i], '%.2f' %((city_gis[i] * 100) / gis_count)]
        
        city_vl = dict(city_vl)
        for i in city_vl:
            city_vl[i] = [city_vl[i], '%.2f' %((city_vl[i] * 100) / vl_count)]

        
        city_trip = dict(city_trip)
        for i in city_trip:
            city_trip[i] = [city_trip[i], '%.2f' %((city_trip[i] * 100) / trip_count)]
            
        sorted_city_gis = sorted(city_gis.items(), key=lambda item: item[1][0])
        sorted_city_gis = {k: v for k, v in sorted_city_gis[-5:]}
        count_other_city = 0
        for i in sorted_city_gis:
            count_other_city += sorted_city_gis[i][0]
        sorted_city_gis['Остальное'] = [gis_count - count_other_city]
        
        sorted_city_vl = sorted(city_vl.items(), key=lambda item: item[1][0])
        sorted_city_vl = {k: v for k, v in sorted_city_vl[-5:]}
        count_other_city = 0
        for i in sorted_city_vl:
            count_other_city += sorted_city_vl[i][0]
        sorted_city_vl['Остальное'] = [vl_count - count_other_city]
        
        sorted_city_trip = sorted(city_trip.items(), key=lambda item: item[1][0])
        sorted_city_trip = {k: v for k, v in sorted_city_trip[-5:]}
        count_other_city = 0
        for i in sorted_city_trip:
            count_other_city += sorted_city_trip[i][0]
        sorted_city_trip['Остальное'] = [trip_count - count_other_city]
        
        sorted_city_all = sorted(city_all.items(), key=lambda item: item[1][0])
        sorted_city_all = {k: v for k, v in sorted_city_all[-5:]}
        count_other_city = 0
        for i in sorted_city_all:
            count_other_city += sorted_city_all[i][0]
        sorted_city_all['Остальное'] = [gis_count + vl_count + trip_count - count_other_city]
        

        connection.close()

        # ----------------
        # Общее количество Отзывов
        # ----------------
        connection = sqlite3.connect('reviews_tourism.db')
        cursor = connection.cursor()
        cursor.execute("SELECT Count() FROM vl")
        vl_reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM gis")
        gis_reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM trip")
        trip_reviews_count = cursor.fetchone()[0]
        
        total_reviews_count = vl_reviews_count + gis_reviews_count + trip_reviews_count
        total_reviews_count = [(gis_reviews_count * 100) // total_reviews_count, (vl_reviews_count * 100) // total_reviews_count, (trip_reviews_count * 100) // total_reviews_count]

        cursor.execute("SELECT rating FROM gis")
        rating_gis = sorted([str(i[0]) for i in cursor.fetchall()])
        rating_gis = Counter(rating_gis)

        cursor.execute("SELECT rating FROM vl")
        rating_vl = sorted([str(i[0]) for i in cursor.fetchall() if str(i[0]) != '1.2'])
        rating_vl = Counter(rating_vl)
        
        cursor.execute("SELECT rating FROM trip")
        rating_trip = sorted([str(i[0]) for i in cursor.fetchall()])
        rating_trip = Counter(rating_trip)
        
        rating_all = Counter(rating_gis + rating_vl + rating_trip)
        rating_all = dict(rating_all)
        for i in rating_all:
            rating_all[i] = [rating_all[i], '%.2f' %((rating_all[i] * 100) / (gis_reviews_count+vl_reviews_count+trip_reviews_count))]


        rating_gis = dict(rating_gis)
        for i in rating_gis:
            rating_gis[i] = [rating_gis[i], '%.2f' %((rating_gis[i] * 100) / gis_reviews_count)]

        
        rating_vl = dict(rating_vl)
        for i in rating_vl:
            rating_vl[i] = [rating_vl[i], '%.2f' %((rating_vl[i] * 100) / vl_reviews_count)]

       
        rating_trip = dict(rating_trip)
        for i in rating_trip:
            rating_trip[i] = [rating_trip[i], '%.2f' %((rating_trip[i] * 100) / trip_reviews_count)]
        
        cursor.execute("SELECT date FROM gis")
        year_gis = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_gis = Counter(year_gis)
        
        cursor.execute("SELECT date FROM vl")
        year_vl = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_vl = Counter(year_vl)
        
        cursor.execute("SELECT date FROM trip")
        year_trip = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_trip = Counter(year_trip)
        
        year_all = Counter(year_gis + year_vl + year_trip)
        year_all = year_all.most_common()
        year_all = dict(year_all)
        
        for i in year_all:
            year_all[i] = [year_all[i], '%.2f' % ((year_all[i] * 100) / (gis_reviews_count + vl_reviews_count + trip_reviews_count))]

        year_gis = dict(year_gis)
        for i in year_gis:
            year_gis[i] = [year_gis[i], '%.2f' %((year_gis[i] * 100) / gis_reviews_count)]
        
        year_vl = dict(year_vl)
        for i in year_vl:
            year_vl[i] = [year_vl[i], '%.2f' % ((year_vl[i] * 100) / vl_reviews_count)]

        year_trip = dict(year_trip)
        for i in year_trip:
            year_trip[i] = [year_trip[i], '%.2f' % ((year_trip[i] * 100) / trip_reviews_count)]


        connection.close()

        return render(request, 'accounts/index.html', {'companies': 
                                                        {
                                                            'gis': [gis_count, total_count[0], round(total_count[0] / 10) * 10],
                                                            'vl': [vl_count, total_count[1], round(total_count[1] / 10) * 10],
                                                            'trip': [trip_count, total_count[2], round(total_count[2] / 10) * 10],
                                                        },
                                                        
                                                       'reviews': 
                                                        {
                                                            'gis': [gis_reviews_count, total_reviews_count[0], round(total_reviews_count[0] / 10) * 10],
                                                            'vl': [vl_reviews_count, total_reviews_count[1], round(total_reviews_count[1] / 10) * 10],
                                                            'trip': [trip_reviews_count, total_reviews_count[2], round(total_reviews_count[2] / 10) * 10],
                                                        },
                                                       'city':
                                                           {
                                                               'all': city_all,
                                                               'gis': city_gis,
                                                               'vl': city_vl,
                                                               'trip': city_trip,
                                                           },
                                                        'sorted_city':
                                                           {
                                                               'all': sorted_city_all,
                                                               'gis': sorted_city_gis,
                                                               'vl': sorted_city_vl,
                                                               'trip': sorted_city_trip,
                                                           },
                                                       'rubrics' :
                                                           {
                                                               'all': rubrics_all,
                                                               'gis': rubrics_gis,
                                                               'vl': rubrics_vl,
                                                               'trip': rubrics_trip
                                                           },
                                                       'rating' :
                                                           {
                                                               'all': rating_all,
                                                               'gis': rating_gis,
                                                               'vl': rating_vl,
                                                               'trip': rating_trip,
                                                           },
                                                       'years' :
                                                           {
                                                               'all': year_all,
                                                               'gis': year_gis,
                                                               'vl': year_vl,
                                                               'trip': year_trip,
                                                           },

                                                       'user_name': request.user.username,
                                                       'db_nane': 'tourism',
                                                       'page_name': 'Организация туризма',
                                                       'form': form,
                                                      }
                      )
    
    else:
        return HttpResponseRedirect('')

def culture(request):
    if request.user.is_authenticated == True:
    
        form = ContactForm(request.POST)
        if form.is_valid():
            trip_advisor = form.cleaned_data['trip_advisor']
            booking = form.cleaned_data['booking']
            vlru = form.cleaned_data['vlru']
            gis = form.cleaned_data['gis']
            google = form.cleaned_data['google']
            
            print(google)

        form = ContactForm()
        
        connection = sqlite3.connect('culture.db')
        cursor = connection.cursor()

        #----------------
        # Общее количество Компаний
        # ----------------
        cursor.execute("SELECT Count() FROM vl")
        vl_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM gis")
        gis_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM trip")
        trip_count = cursor.fetchone()[0]
        total_count = vl_count + gis_count + trip_count
        total_count = [(gis_count * 100) // total_count, (vl_count * 100) // total_count, (trip_count * 100) // total_count]

        # ----------------
        # Рубрики
        # ----------------
        cursor.execute("SELECT rubric FROM gis")
        rubrics_gis = cursor.fetchall()
        cursor.execute("SELECT rubric FROM vl")
        rubrics_vl = cursor.fetchall()
        cursor.execute("SELECT rubric FROM trip")
        rubrics_trip = cursor.fetchall()

        def sum_rubrics(db_rubrics):
            #rubrics = {
            #    'Турфирмы': [0, 0], 'Оформление виз': [0, 0], 'Авиабилеты': [0, 0], 
            #    'Организация экскурсий': [0, 0], 'Бронирование гостиниц': [0, 0], 'Железнодорожные билеты': [0, 0], 
            #    'Справочные службы': [0, 0], 
            #}  

            rubrics = {
                'Дома / дворцы культуры': [0, 0], 'Художественные выставки / Галереи': [0, 0], 'Концертные залы': [0, 0], 
                'Музеи': [0, 0], 'Театры': [0, 0], 'Городские оркестры': [0, 0], 
                'Кинотеатры': [0, 0], 'Ботанический сад / Дендрарий': [0, 0], 'Океанариумы': [0, 0],
                'Филармонии': [0, 0], 'Дельфинарии': [0, 0], 'Обсерватории': [0, 0],
                'Цирки': [0, 0], 'Библиотеки': [0, 0],
            }            

            rubrics_count = 0
            for item in db_rubrics:
                for i in item[0].split('; '):
                    for j in rubrics:
                        if i == j:
                            rubrics[j][0] += 1
                            rubrics_count += 1
                            break
            for item in rubrics:
                rubrics[item][1] = '%.2f' %((rubrics[item][0] * 100) / rubrics_count)

            return rubrics

        rubrics_all = sum_rubrics(rubrics_gis + rubrics_vl + rubrics_trip)
        rubrics_gis = sum_rubrics(rubrics_gis)
        rubrics_vl = sum_rubrics(rubrics_vl)
        rubrics_trip = sum_rubrics(rubrics_trip)


        # ----------------
        # АТЕ Компаний
        # ----------------
        cursor.execute("SELECT city FROM gis")
        city_gis = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_gis)):
            if 'городской' in city_gis[i]:
                city_gis[i] = city_gis[i].replace(' городской', '')        
        city_gis = Counter(city_gis)
        
        cursor.execute("SELECT city FROM vl")
        city_vl = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_vl)):
            if 'городской' in city_vl[i]:
                city_vl[i] = city_vl[i].replace(' городской', '')
        city_vl = Counter(city_vl)
        
        cursor.execute("SELECT city FROM trip")
        city_trip = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_trip)):
            if 'городской' in city_trip[i]:
                city_trip[i] = city_trip[i].replace(' городской', '')
        city_trip = Counter(city_trip)
        
        city_all = city_gis + city_vl + city_trip
        city_all = dict(Counter(city_all))

        for i in city_all:
            city_all[i] = [city_all[i], '%.2f' %((city_all[i] * 100) / (gis_count + vl_count + trip_count))]
            
        city_gis = dict(city_gis)
        for i in city_gis:
            city_gis[i] = [city_gis[i], '%.2f' %((city_gis[i] * 100) / gis_count)]
        
        city_vl = dict(city_vl)
        for i in city_vl:
            city_vl[i] = [city_vl[i], '%.2f' %((city_vl[i] * 100) / vl_count)]

        
        city_trip = dict(city_trip)
        for i in city_trip:
            city_trip[i] = [city_trip[i], '%.2f' %((city_trip[i] * 100) / trip_count)]
            
        sorted_city_gis = sorted(city_gis.items(), key=lambda item: item[1][0])
        sorted_city_gis = {k: v for k, v in sorted_city_gis[-5:]}
        count_other_city = 0
        for i in sorted_city_gis:
            count_other_city += sorted_city_gis[i][0]
        sorted_city_gis['Остальное'] = [gis_count - count_other_city]
        
        sorted_city_vl = sorted(city_vl.items(), key=lambda item: item[1][0])
        sorted_city_vl = {k: v for k, v in sorted_city_vl[-5:]}
        count_other_city = 0
        for i in sorted_city_vl:
            count_other_city += sorted_city_vl[i][0]
        sorted_city_vl['Остальное'] = [vl_count - count_other_city]
        
        sorted_city_trip = sorted(city_trip.items(), key=lambda item: item[1][0])
        sorted_city_trip = {k: v for k, v in sorted_city_trip[-5:]}
        count_other_city = 0
        for i in sorted_city_trip:
            count_other_city += sorted_city_trip[i][0]
        sorted_city_trip['Остальное'] = [trip_count - count_other_city]
        
        sorted_city_all = sorted(city_all.items(), key=lambda item: item[1][0])
        sorted_city_all = {k: v for k, v in sorted_city_all[-5:]}
        count_other_city = 0
        for i in sorted_city_all:
            count_other_city += sorted_city_all[i][0]
        sorted_city_all['Остальное'] = [gis_count + vl_count + trip_count - count_other_city]
        

        connection.close()

        # ----------------
        # Общее количество Отзывов
        # ----------------
        connection = sqlite3.connect('reviews_culture.db')
        cursor = connection.cursor()
        cursor.execute("SELECT Count() FROM vl")
        vl_reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM gis")
        gis_reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM trip")
        trip_reviews_count = cursor.fetchone()[0]
        
        total_reviews_count = vl_reviews_count + gis_reviews_count + trip_reviews_count
        total_reviews_count = [(gis_reviews_count * 100) // total_reviews_count, (vl_reviews_count * 100) // total_reviews_count, (trip_reviews_count * 100) // total_reviews_count]

        cursor.execute("SELECT rating FROM gis")
        rating_gis = sorted([str(i[0]) for i in cursor.fetchall()])
        rating_gis = Counter(rating_gis)

        cursor.execute("SELECT rating FROM vl")
        rating_vl = sorted([str(i[0]) for i in cursor.fetchall() if str(i[0]) != '1.2'])
        rating_vl = Counter(rating_vl)
        
        cursor.execute("SELECT rating FROM trip")
        rating_trip = sorted([str(i[0]) for i in cursor.fetchall()])
        rating_trip = Counter(rating_trip)
        
        rating_all = Counter(rating_gis + rating_vl + rating_trip)
        rating_all = dict(rating_all)
        for i in rating_all:
            rating_all[i] = [rating_all[i], '%.2f' %((rating_all[i] * 100) / (gis_reviews_count+vl_reviews_count+trip_reviews_count))]


        rating_gis = dict(rating_gis)
        for i in rating_gis:
            rating_gis[i] = [rating_gis[i], '%.2f' %((rating_gis[i] * 100) / gis_reviews_count)]

        
        rating_vl = dict(rating_vl)
        for i in rating_vl:
            rating_vl[i] = [rating_vl[i], '%.2f' %((rating_vl[i] * 100) / vl_reviews_count)]

       
        rating_trip = dict(rating_trip)
        for i in rating_trip:
            rating_trip[i] = [rating_trip[i], '%.2f' %((rating_trip[i] * 100) / trip_reviews_count)]
        
        cursor.execute("SELECT date FROM gis")
        year_gis = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_gis = Counter(year_gis)
        
        cursor.execute("SELECT date FROM vl")
        year_vl = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_vl = Counter(year_vl)
        
        cursor.execute("SELECT date FROM trip")
        year_trip = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_trip = Counter(year_trip)
        
        year_all = Counter(year_gis + year_vl + year_trip)
        year_all = year_all.most_common()
        year_all = dict(year_all)
        
        for i in year_all:
            year_all[i] = [year_all[i], '%.2f' % ((year_all[i] * 100) / (gis_reviews_count + vl_reviews_count + trip_reviews_count))]

        year_gis = dict(year_gis)
        for i in year_gis:
            year_gis[i] = [year_gis[i], '%.2f' %((year_gis[i] * 100) / gis_reviews_count)]
        
        year_vl = dict(year_vl)
        for i in year_vl:
            year_vl[i] = [year_vl[i], '%.2f' % ((year_vl[i] * 100) / vl_reviews_count)]

        year_trip = dict(year_trip)
        for i in year_trip:
            year_trip[i] = [year_trip[i], '%.2f' % ((year_trip[i] * 100) / trip_reviews_count)]


        connection.close()

        return render(request, 'accounts/index.html', {'companies': 
                                                        {
                                                            'gis': [gis_count, total_count[0], round(total_count[0] / 10) * 10],
                                                            'vl': [vl_count, total_count[1], round(total_count[1] / 10) * 10],
                                                            'trip': [trip_count, total_count[2], round(total_count[2] / 10) * 10],
                                                        },
                                                        
                                                       'reviews': 
                                                        {
                                                            'gis': [gis_reviews_count, total_reviews_count[0], round(total_reviews_count[0] / 10) * 10],
                                                            'vl': [vl_reviews_count, total_reviews_count[1], round(total_reviews_count[1] / 10) * 10],
                                                            'trip': [trip_reviews_count, total_reviews_count[2], round(total_reviews_count[2] / 10) * 10],
                                                        },
                                                       'city':
                                                           {
                                                               'all': city_all,
                                                               'gis': city_gis,
                                                               'vl': city_vl,
                                                               'trip': city_trip,
                                                           },
                                                        'sorted_city':
                                                           {
                                                               'all': sorted_city_all,
                                                               'gis': sorted_city_gis,
                                                               'vl': sorted_city_vl,
                                                               'trip': sorted_city_trip,
                                                           },
                                                       'rubrics' :
                                                           {
                                                               'all': rubrics_all,
                                                               'gis': rubrics_gis,
                                                               'vl': rubrics_vl,
                                                               'trip': rubrics_trip
                                                           },
                                                       'rating' :
                                                           {
                                                               'all': rating_all,
                                                               'gis': rating_gis,
                                                               'vl': rating_vl,
                                                               'trip': rating_trip,
                                                           },
                                                       'years' :
                                                           {
                                                               'all': year_all,
                                                               'gis': year_gis,
                                                               'vl': year_vl,
                                                               'trip': year_trip,
                                                           },

                                                       'user_name': request.user.username,
                                                       'db_nane': 'culture',
                                                       'page_name': 'Культурный отдых',
                                                       'form': form,
                                                      }
                      )
    
    else:
        return HttpResponseRedirect('')
        

def attr(request):
    if request.user.is_authenticated == True:
    
        form = ContactForm(request.POST)
        if form.is_valid():
            trip_advisor = form.cleaned_data['trip_advisor']
            booking = form.cleaned_data['booking']
            vlru = form.cleaned_data['vlru']
            gis = form.cleaned_data['gis']
            google = form.cleaned_data['google']
            
            print(google)

        form = ContactForm()
        
        connection = sqlite3.connect('attr.db')
        cursor = connection.cursor()

        #----------------
        # Общее количество Компаний
        # ----------------
        cursor.execute("SELECT Count() FROM vl")
        vl_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM gis")
        gis_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM trip")
        trip_count = cursor.fetchone()[0]
        total_count = vl_count + gis_count + trip_count
        total_count = [(gis_count * 100) // total_count, (vl_count * 100) // total_count, (trip_count * 100) // total_count]

        # ----------------
        # Рубрики
        # ----------------
        cursor.execute("SELECT rubric FROM gis")
        rubrics_gis = cursor.fetchall()
        cursor.execute("SELECT rubric FROM vl")
        rubrics_vl = cursor.fetchall()
        cursor.execute("SELECT rubric FROM trip")
        rubrics_trip = cursor.fetchall()

        def sum_rubrics(db_rubrics):
            rubrics = {
                'Пляж': [0, 0], 'Сквер': [0, 0], 'Парк': [0, 0], 'Площадь': [0, 0],
                'Интересное здание': [0, 0], 'Смотровая площадка': [0, 0], 'Декоративный объект': [0, 0], 'Стела, указатель': [0, 0],
                'Памятная доска': [0, 0], 'Стрит-арт': [0, 0], 'Остров': [0, 0], 'Вершина горы': [0, 0],
                'Памятник природы': [0, 0], 'Набережная': [0, 0], 'Культурные объекты и\xa0достопримечательности': [0, 0], 'Водопад': [0, 0],
                'Мост': [0, 0]
            
            }         

            rubrics_count = 0
            for item in db_rubrics:
                for i in item[0].split('; '):
                    for j in rubrics:
                        if i == j:
                            rubrics[j][0] += 1
                            rubrics_count += 1
                            break
            for item in rubrics:
                rubrics[item][1] = '%.2f' %((rubrics[item][0] * 100) / rubrics_count)

            return rubrics

        rubrics_all = sum_rubrics(rubrics_gis + rubrics_vl + rubrics_trip)
        rubrics_gis = sum_rubrics(rubrics_gis)
        rubrics_vl = sum_rubrics(rubrics_vl)
        rubrics_trip = sum_rubrics(rubrics_trip)


        # ----------------
        # АТЕ Компаний
        # ----------------
        cursor.execute("SELECT city FROM gis")
        city_gis = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_gis)):
            if 'городской' in city_gis[i]:
                city_gis[i] = city_gis[i].replace(' городской', '')        
        city_gis = Counter(city_gis)
        
        cursor.execute("SELECT city FROM vl")
        city_vl = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_vl)):
            if 'городской' in city_vl[i]:
                city_vl[i] = city_vl[i].replace(' городской', '')
        city_vl = Counter(city_vl)
        
        cursor.execute("SELECT city FROM trip")
        city_trip = sorted([i[0] for i in cursor.fetchall()])
        for i in range(len(city_trip)):
            if 'городской' in city_trip[i]:
                city_trip[i] = city_trip[i].replace(' городской', '')
        city_trip = Counter(city_trip)
        
        city_all = city_gis + city_vl + city_trip
        city_all = dict(Counter(city_all))

        for i in city_all:
            city_all[i] = [city_all[i], '%.2f' %((city_all[i] * 100) / (gis_count + vl_count + trip_count))]
            
        city_gis = dict(city_gis)
        for i in city_gis:
            city_gis[i] = [city_gis[i], '%.2f' %((city_gis[i] * 100) / gis_count)]
        
        city_vl = dict(city_vl)
        for i in city_vl:
            city_vl[i] = [city_vl[i], '%.2f' %((city_vl[i] * 100) / vl_count)]

        
        city_trip = dict(city_trip)
        for i in city_trip:
            city_trip[i] = [city_trip[i], '%.2f' %((city_trip[i] * 100) / trip_count)]
            
        sorted_city_gis = sorted(city_gis.items(), key=lambda item: item[1][0])
        sorted_city_gis = {k: v for k, v in sorted_city_gis[-5:]}
        count_other_city = 0
        for i in sorted_city_gis:
            count_other_city += sorted_city_gis[i][0]
        sorted_city_gis['Остальное'] = [gis_count - count_other_city]
        
        sorted_city_vl = sorted(city_vl.items(), key=lambda item: item[1][0])
        sorted_city_vl = {k: v for k, v in sorted_city_vl[-5:]}
        count_other_city = 0
        for i in sorted_city_vl:
            count_other_city += sorted_city_vl[i][0]
        sorted_city_vl['Остальное'] = [vl_count - count_other_city]
        
        sorted_city_trip = sorted(city_trip.items(), key=lambda item: item[1][0])
        sorted_city_trip = {k: v for k, v in sorted_city_trip[-5:]}
        count_other_city = 0
        for i in sorted_city_trip:
            count_other_city += sorted_city_trip[i][0]
        sorted_city_trip['Остальное'] = [trip_count - count_other_city]
        
        sorted_city_all = sorted(city_all.items(), key=lambda item: item[1][0])
        sorted_city_all = {k: v for k, v in sorted_city_all[-5:]}
        count_other_city = 0
        for i in sorted_city_all:
            count_other_city += sorted_city_all[i][0]
        sorted_city_all['Остальное'] = [gis_count + vl_count + trip_count - count_other_city]
        

        connection.close()

        # ----------------
        # Общее количество Отзывов
        # ----------------
        connection = sqlite3.connect('reviews_attr.db')
        cursor = connection.cursor()
        cursor.execute("SELECT Count() FROM vl")
        vl_reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM gis")
        gis_reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT Count() FROM trip")
        trip_reviews_count = cursor.fetchone()[0]
        
        total_reviews_count = vl_reviews_count + gis_reviews_count + trip_reviews_count
        total_reviews_count = [(gis_reviews_count * 100) // total_reviews_count, (vl_reviews_count * 100) // total_reviews_count, (trip_reviews_count * 100) // total_reviews_count]

        cursor.execute("SELECT rating FROM gis")
        rating_gis = sorted([str(i[0]) for i in cursor.fetchall()])
        rating_gis = Counter(rating_gis)

        cursor.execute("SELECT rating FROM vl")
        rating_vl = sorted([str(i[0]) for i in cursor.fetchall() if str(i[0]) != '1.2'])
        rating_vl = Counter(rating_vl)
        
        cursor.execute("SELECT rating FROM trip")
        rating_trip = sorted([str(i[0]) for i in cursor.fetchall()])
        rating_trip = Counter(rating_trip)
        
        rating_all = Counter(rating_gis + rating_vl + rating_trip)
        rating_all = dict(rating_all)
        for i in rating_all:
            rating_all[i] = [rating_all[i], '%.2f' %((rating_all[i] * 100) / (gis_reviews_count+vl_reviews_count+trip_reviews_count))]


        rating_gis = dict(rating_gis)
        for i in rating_gis:
            rating_gis[i] = [rating_gis[i], '%.2f' %((rating_gis[i] * 100) / gis_reviews_count)]

        
        rating_vl = dict(rating_vl)
        for i in rating_vl:
            rating_vl[i] = [rating_vl[i], '%.2f' %((rating_vl[i] * 100) / vl_reviews_count)]

       
        rating_trip = dict(rating_trip)
        for i in rating_trip:
            rating_trip[i] = [rating_trip[i], '%.2f' %((rating_trip[i] * 100) / trip_reviews_count)]
        
        cursor.execute("SELECT date FROM gis")
        year_gis = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_gis = Counter(year_gis)
        
        cursor.execute("SELECT date FROM vl")
        year_vl = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_vl = Counter(year_vl)
        
        cursor.execute("SELECT date FROM trip")
        year_trip = sorted([i[0].split('-')[0] for i in cursor.fetchall()])
        year_trip = Counter(year_trip)
        
        year_all = Counter(year_gis + year_vl + year_trip)
        year_all = year_all.most_common()
        year_all = dict(year_all)
        
        for i in year_all:
            year_all[i] = [year_all[i], '%.2f' % ((year_all[i] * 100) / (gis_reviews_count + vl_reviews_count + trip_reviews_count))]

        year_gis = dict(year_gis)
        for i in year_gis:
            year_gis[i] = [year_gis[i], '%.2f' %((year_gis[i] * 100) / gis_reviews_count)]
        
        year_vl = dict(year_vl)
        for i in year_vl:
            year_vl[i] = [year_vl[i], '%.2f' % ((year_vl[i] * 100) / vl_reviews_count)]

        year_trip = dict(year_trip)
        for i in year_trip:
            year_trip[i] = [year_trip[i], '%.2f' % ((year_trip[i] * 100) / trip_reviews_count)]


        connection.close()

        return render(request, 'accounts/index.html', {'companies': 
                                                        {
                                                            'gis': [gis_count, total_count[0], round(total_count[0] / 10) * 10],
                                                            'vl': [vl_count, total_count[1], round(total_count[1] / 10) * 10],
                                                            'trip': [trip_count, total_count[2], round(total_count[2] / 10) * 10],
                                                        },
                                                        
                                                       'reviews': 
                                                        {
                                                            'gis': [gis_reviews_count, total_reviews_count[0], round(total_reviews_count[0] / 10) * 10],
                                                            'vl': [vl_reviews_count, total_reviews_count[1], round(total_reviews_count[1] / 10) * 10],
                                                            'trip': [trip_reviews_count, total_reviews_count[2], round(total_reviews_count[2] / 10) * 10],
                                                        },
                                                       'city':
                                                           {
                                                               'all': city_all,
                                                               'gis': city_gis,
                                                               'vl': city_vl,
                                                               'trip': city_trip,
                                                           },
                                                        'sorted_city':
                                                           {
                                                               'all': sorted_city_all,
                                                               'gis': sorted_city_gis,
                                                               'vl': sorted_city_vl,
                                                               'trip': sorted_city_trip,
                                                           },
                                                       'rubrics' :
                                                           {
                                                               'all': rubrics_all,
                                                               'gis': rubrics_gis,
                                                               'vl': rubrics_vl,
                                                               'trip': rubrics_trip
                                                           },
                                                       'rating' :
                                                           {
                                                               'all': rating_all,
                                                               'gis': rating_gis,
                                                               'vl': rating_vl,
                                                               'trip': rating_trip,
                                                           },
                                                       'years' :
                                                           {
                                                               'all': year_all,
                                                               'gis': year_gis,
                                                               'vl': year_vl,
                                                               'trip': year_trip,
                                                           },

                                                       'user_name': request.user.username,
                                                       'db_nane': 'attr',
                                                       'page_name': 'Туристические аттракции',
                                                       'form': form,
                                                      }
                      )
    
    else:
        return HttpResponseRedirect('')
        
        
def search(request):
    if request.user.is_authenticated == True:
    
        form = SearchForm(request.POST)
        if form.is_valid():
            get_result = form.cleaned_data
            print(get_result)

            if get_result['category'] == 'hotel':
                get_result['rubrics'] = get_result['rubrics_hotel']
            elif get_result['category'] == 'tourism':
                get_result['rubrics'] = get_result['rubrics_tour']
            elif get_result['category'] == 'culture':
                get_result['rubrics'] = get_result['rubrics_cult']
            elif get_result['category'] == 'attr':
                get_result['rubrics'] = get_result['rubrics_attr']

            try:
                conn = sqlite3.connect(str(request.user) + '_searching.db')
                cursor_conn = conn.cursor()
                cursor_conn.execute('DROP TABLE search')
                conn.commit()
                conn.close()
            except Exception as e:
                print('COM = ', e)
                pass

            try:
                conn_review = sqlite3.connect(str(request.user) + '_searching_reviews.db')
                cursor_review = conn_review.cursor()
                cursor_review.execute('DROP TABLE search')
                conn_review.commit()
                conn_review.close()
            except Exception as e:
                print('REV = ', e)
                pass

            connection = sqlite3.connect(str(request.user) + '_searching.db')
            cursor = connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS search
                                              (rubric TEXT, company TEXT, city TEXT, address TEXT, webSite TEXT, url TEXT NOT NULL UNIQUE)''')
            connection.commit()
            connection.close()

            connection_review = sqlite3.connect(str(request.user) + '_searching_reviews.db')
            cursor_review = connection_review.cursor()
            cursor_review.execute('''CREATE TABLE IF NOT EXISTS search
                                              (rubric TEXT, company TEXT, city TEXT, webSite TEXT, review TEXT, rating REAL, date TEXT, url TEXT NOT NULL)''')
            connection_review.commit()
            connection_review.close()


            connection = sqlite3.connect('{}.db'.format(get_result['category']))
            cursor = connection.cursor()

            connection_review = sqlite3.connect('reviews_{}.db'.format(get_result['category']))
            cursor_review = connection_review.cursor()

            tmp_data = 0
            if get_result['plat'] == 'gis':
                cursor.execute("SELECT * FROM gis WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data = [[i[0], i[1], i[2], i[3], '2GIS', i[5]] for i in cursor.fetchall()]

                tmp_data_review = []
                for item in tmp_data:
                    cursor_review.execute("SELECT * FROM gis WHERE URL=?", (item[5],))
                    tmp_data_review.extend([[item[0], i[3], item[2], '2GIS', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

            elif get_result['plat'] == 'vl':
                cursor.execute("SELECT * FROM vl WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data = [[i[0], i[1], i[2], i[3], 'VL', i[5]] for i in cursor.fetchall()]

                tmp_data_review = []
                for item in tmp_data:
                    cursor_review.execute("SELECT * FROM vl WHERE URL=?", (item[5],))
                    tmp_data_review.extend(
                        [[item[0], i[3], item[2], 'VL', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

            elif get_result['plat'] == 'trip':
                cursor.execute("SELECT * FROM trip WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data = [[i[0], i[1], i[2], i[3], 'TripAdvisor', i[5]] for i in cursor.fetchall()]

                tmp_data_review = []
                for item in tmp_data:
                    cursor_review.execute("SELECT * FROM trip WHERE URL=?", (item[5],))
                    tmp_data_review.extend(
                        [[item[0], i[3], item[2], 'TripAdvisor', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

            elif get_result['plat'] == 'gis;vl':
                cursor.execute("SELECT * FROM gis WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data_gis = [[i[0], i[1], i[2], i[3], '2GIS', i[5]] for i in cursor.fetchall()]

                tmp_data_review_gis = []
                for item in tmp_data_gis:
                    cursor_review.execute("SELECT * FROM gis WHERE URL=?", (item[5],))
                    tmp_data_review_gis.extend(
                        [[item[0], i[3], item[2], '2GIS', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

                cursor.execute("SELECT * FROM vl WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data_vl = [[i[0], i[1], i[2], i[3], 'VL', i[5]] for i in cursor.fetchall()]

                tmp_data_review_vl = []
                for item in tmp_data_vl:
                    cursor_review.execute("SELECT * FROM vl WHERE URL=?", (item[5],))
                    tmp_data_review_vl.extend(
                        [[item[0], i[3], item[2], 'VL', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

                tmp_data = tmp_data_gis + tmp_data_vl
                tmp_data_review = tmp_data_review_gis + tmp_data_review_vl

            elif get_result['plat'] == 'gis;trip':
                cursor.execute("SELECT * FROM gis WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data_gis = [[i[0], i[1], i[2], i[3], '2GIS', i[5]] for i in cursor.fetchall()]

                tmp_data_review_gis = []
                for item in tmp_data_gis:
                    cursor_review.execute("SELECT * FROM gis WHERE URL=?", (item[5],))
                    tmp_data_review_gis.extend(
                        [[item[0], i[3], item[2], '2GIS', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

                cursor.execute("SELECT * FROM trip WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data_trip = [[i[0], i[1], i[2], i[3], 'TripAdvisor', i[5]] for i in cursor.fetchall()]

                tmp_data_review_trip = []
                for item in tmp_data_trip:
                    cursor_review.execute("SELECT * FROM trip WHERE URL=?", (item[5],))
                    tmp_data_review_trip.extend(
                        [[item[0], i[3], item[2], 'TripAdvisor', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

                tmp_data = tmp_data_gis + tmp_data_trip
                tmp_data_review = tmp_data_review_gis + tmp_data_review_trip


            elif get_result['plat'] == 'vl;trip':
                cursor.execute("SELECT * FROM vl WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data_vl = [[i[0], i[1], i[2], i[3], 'VL', i[5]] for i in cursor.fetchall()]

                tmp_data_review_vl = []
                for item in tmp_data_vl:
                    cursor_review.execute("SELECT * FROM vl WHERE URL=?", (item[5],))
                    tmp_data_review_vl.extend(
                        [[item[0], i[3], item[2], 'VL', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

                cursor.execute("SELECT * FROM trip WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data_trip = [[i[0], i[1], i[2], i[3], 'TripAdvisor', i[5]] for i in cursor.fetchall()]

                tmp_data_review_trip = []
                for item in tmp_data_trip:
                    cursor_review.execute("SELECT * FROM trip WHERE URL=?", (item[5],))
                    tmp_data_review_trip.extend(
                        [[item[0], i[3], item[2], 'TripAdvisor', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

                tmp_data = tmp_data_vl + tmp_data_trip
                tmp_data_review = tmp_data_review_vl + tmp_data_review_trip

            elif get_result['plat'] == 'gis;vl;trip':
                cursor.execute("SELECT * FROM gis WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data_gis = [[i[0], i[1], i[2], i[3], '2GIS', i[5]] for i in cursor.fetchall()]

                tmp_data_review_gis = []
                for item in tmp_data_gis:
                    cursor_review.execute("SELECT * FROM gis WHERE URL=?", (item[5],))
                    tmp_data_review_gis.extend(
                        [[item[0], i[3], item[2], '2GIS', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

                cursor.execute("SELECT * FROM vl WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data_vl = [[i[0], i[1], i[2], i[3], 'VL', i[5]] for i in cursor.fetchall()]

                tmp_data_review_vl = []
                for item in tmp_data_vl:
                    cursor_review.execute("SELECT * FROM vl WHERE URL=?", (item[5],))
                    tmp_data_review_vl.extend(
                        [[item[0], i[3], item[2], 'VL', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

                cursor.execute("SELECT * FROM trip WHERE rubric LIKE ? AND city=?",
                               ("%"+get_result['rubrics']+"%", get_result['cities']))
                tmp_data_trip = [[i[0], i[1], i[2], i[3], 'TripAdvisor', i[5]] for i in cursor.fetchall()]

                tmp_data_review_trip = []
                for item in tmp_data_trip:
                    cursor_review.execute("SELECT * FROM trip WHERE URL=?", (item[5],))
                    tmp_data_review_trip.extend(
                        [[item[0], i[3], item[2], 'TripAdvisor', i[0], i[1], i[2], i[4]] for i in cursor_review.fetchall()])

                tmp_data = tmp_data_gis + tmp_data_vl + tmp_data_trip
                tmp_data_review = tmp_data_review_gis + tmp_data_review_vl + tmp_data_review_trip


            search_data = tmp_data
            connection.close()

            search_data_review = tmp_data_review
            connection_review.close()




            connection = sqlite3.connect(str(request.user)+'_searching.db')
            cursor = connection.cursor()

            for item in search_data:
                cursor.execute('INSERT INTO search VALUES (?, ?, ?, ?, ?, ?)',
                               (item[0], item[1], item[2], item[3], item[4], item[5]))
            connection.commit()
            connection.close()

            connection_review = sqlite3.connect(str(request.user)+'_searching_reviews.db')
            cursor_review = connection_review.cursor()

            for item in search_data_review:
                cursor_review.execute('INSERT INTO search VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                     (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]))
            connection_review.commit()
            connection_review.close()

            with open(str(request.user) + '.txt', 'w', encoding='Windows-1251') as f:
                f.write(get_result['cities'].replace('городской ', '')+'\n' + get_result['rubrics'])


            return HttpResponseRedirect("./search")


        form = SearchForm()






        #----------------
        # Общее количество Компаний
        # ----------------
        connection = sqlite3.connect(str(request.user)+'_searching.db')
        cursor = connection.cursor()
        cursor.execute("SELECT Count() FROM search WHERE webSite='2GIS'")
        gis_count = cursor.fetchone()[0]

        cursor.execute("SELECT Count() FROM search WHERE webSite='VL'")
        vl_count = cursor.fetchone()[0]

        cursor.execute("SELECT Count() FROM search WHERE webSite='TripAdvisor'")
        trip_count = cursor.fetchone()[0]

        print(vl_count)
        print(gis_count)
        print(trip_count)

        total_count = vl_count + gis_count + trip_count

        if total_count != 0:
            total_count = [(gis_count * 100) // total_count, (vl_count * 100) // total_count, (trip_count * 100) // total_count]
        else:
            total_count = [0, 0, 0]


        # ----------------
        # Общее количество Отзывов
        # ----------------
        connection_review = sqlite3.connect(str(request.user)+'_searching_reviews.db')
        cursor_review = connection_review.cursor()
        cursor_review.execute("SELECT Count() FROM search WHERE webSite='2GIS'")
        gis_reviews_count = cursor_review.fetchone()[0]

        cursor_review.execute("SELECT Count() FROM search WHERE webSite='VL'")
        vl_reviews_count = cursor_review.fetchone()[0]

        cursor_review.execute("SELECT Count() FROM search WHERE webSite='TripAdvisor'")
        trip_reviews_count = cursor_review.fetchone()[0]

        print(gis_reviews_count)
        print(vl_reviews_count)
        print(trip_reviews_count)

        total_reviews_count = gis_reviews_count + vl_reviews_count + trip_reviews_count

        if total_reviews_count != 0:
            total_reviews_count = [(gis_reviews_count * 100) // total_reviews_count, (vl_reviews_count * 100) // total_reviews_count,
                           (trip_reviews_count * 100) // total_reviews_count]
        else:
            total_reviews_count = [0, 0, 0]


        cursor_review.execute("SELECT rating FROM search WHERE webSite='2GIS'")
        rating_gis = sorted([str(i[0]) for i in cursor_review.fetchall()])
        rating_gis = Counter(rating_gis)

        cursor_review.execute("SELECT rating FROM search WHERE webSite='VL'")
        rating_vl = sorted([str(i[0]) for i in cursor_review.fetchall() if str(i[0]) != '1.2'])
        rating_vl = Counter(rating_vl)

        cursor_review.execute("SELECT rating FROM search WHERE webSite='TripAdvisor'")
        rating_trip = sorted([str(i[0]) for i in cursor_review.fetchall()])
        rating_trip = Counter(rating_trip)

        rating_all = Counter(rating_gis + rating_vl + rating_trip)
        rating_all = dict(rating_all)
        for i in rating_all:
            rating_all[i] = [rating_all[i], '%.2f' %((rating_all[i] * 100) / (gis_reviews_count+vl_reviews_count+trip_reviews_count))]


        rating_gis = dict(rating_gis)
        for i in rating_gis:
            rating_gis[i] = [rating_gis[i], '%.2f' %((rating_gis[i] * 100) / gis_reviews_count)]


        rating_vl = dict(rating_vl)
        for i in rating_vl:
            rating_vl[i] = [rating_vl[i], '%.2f' %((rating_vl[i] * 100) / vl_reviews_count)]


        rating_trip = dict(rating_trip)
        for i in rating_trip:
            rating_trip[i] = [rating_trip[i], '%.2f' %((rating_trip[i] * 100) / trip_reviews_count)]


        cursor_review.execute("SELECT date FROM search WHERE webSite='2GIS'")
        year_gis = sorted([i[0].split('-')[0] for i in cursor_review.fetchall()])
        year_gis = Counter(year_gis)

        cursor_review.execute("SELECT date FROM search WHERE webSite='VL'")
        year_vl = sorted([i[0].split('-')[0] for i in cursor_review.fetchall()])
        year_vl = Counter(year_vl)

        cursor_review.execute("SELECT date FROM search WHERE webSite='TripAdvisor'")
        year_trip = sorted([i[0].split('-')[0] for i in cursor_review.fetchall()])
        year_trip = Counter(year_trip)

        year_all = Counter(year_gis + year_vl + year_trip)
        year_all = year_all.most_common()
        year_all = dict(year_all)

        for i in year_all:
            year_all[i] = [year_all[i], '%.2f' % ((year_all[i] * 100) / (gis_reviews_count + vl_reviews_count + trip_reviews_count))]

        year_gis = dict(year_gis)
        for i in year_gis:
            year_gis[i] = [year_gis[i], '%.2f' %((year_gis[i] * 100) / gis_reviews_count)]

        year_vl = dict(year_vl)
        for i in year_vl:
            year_vl[i] = [year_vl[i], '%.2f' % ((year_vl[i] * 100) / vl_reviews_count)]

        year_trip = dict(year_trip)
        for i in year_trip:
            year_trip[i] = [year_trip[i], '%.2f' % ((year_trip[i] * 100) / trip_reviews_count)]


        connection_review.close()

        with open(str(request.user) + '.txt', 'r', encoding='Windows-1251') as f:
            get_get_result = [i.strip() for i in f.readlines()]

        return render(request, 'accounts/search.html', {'companies': 
                                                        {
                                                            'gis': [gis_count, total_count[0], round(total_count[0] / 10) * 10],
                                                            'vl': [vl_count, total_count[1], round(total_count[1] / 10) * 10],
                                                            'trip': [trip_count, total_count[2], round(total_count[2] / 10) * 10],
                                                        },
                                                        
                                                       'reviews':
                                                        {
                                                            'gis': [gis_reviews_count, total_reviews_count[0], round(total_reviews_count[0] / 10) * 10],
                                                            'vl': [vl_reviews_count, total_reviews_count[1], round(total_reviews_count[1] / 10) * 10],
                                                            'trip': [trip_reviews_count, total_reviews_count[2], round(total_reviews_count[2] / 10) * 10],
                                                        },
                                                       'rating' :
                                                           {
                                                               'all': rating_all,
                                                               'gis': rating_gis,
                                                               'vl': rating_vl,
                                                               'trip': rating_trip,
                                                           },
                                                       'years' :
                                                           {
                                                               'all': year_all,
                                                               'gis': year_gis,
                                                               'vl': year_vl,
                                                               'trip': year_trip,
                                                           },

                                                       'user_name': request.user.username,
                                                       'db_nane': str(request.user)+'_searching',
                                                       'page_name': 'Поисковой фильтр',

                                                       'get_result': get_get_result,
                                                       'form': form,
                                                      }
                      )
    
    else:
        return HttpResponseRedirect('')