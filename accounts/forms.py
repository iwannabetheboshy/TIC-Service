from django import forms
from django.forms import ModelForm, TextInput, CheckboxInput
from .models import Contact

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder' :'username', 'class': 'form-control', 'aria-describedby': 'email-addon'}))
            
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder' :'password', 'class': 'form-control', 'aria-describedby': 'password-addon'}))
            

class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['trip_advisor', 'booking', 'vlru', 'gis', 'google',
                  'star1', 'star2', 'star3', 'star4', 'star5']

        widgets = {
            'trip_advisor': CheckboxInput(attrs={'class': 'form-check-input ms-auto',
                                           'style': 'width: 2.5em;',}),

            'booking': CheckboxInput(attrs={'class': 'form-check-input ms-auto',
                                           'style': 'width: 2.5em;',}),

            'vlru': CheckboxInput(attrs={'class': 'form-check-input ms-auto',
                                           'style': 'width: 2.5em;',}),

            'gis': CheckboxInput(attrs={'class': 'form-check-input ms-auto',
                                           'style': 'width: 2.5em;',}),

            'google': CheckboxInput(attrs={'class': 'form-check-input ms-auto',
                                           'style': 'width: 2.5em;',}),

            'star1': CheckboxInput(attrs={'class': 'form-check-input ms-auto',
                                           'style': 'width: 2.5em;',}),
            'star2': CheckboxInput(attrs={'class': 'form-check-input ms-auto',
                                           'style': 'width: 2.5em;',}),
            'star3': CheckboxInput(attrs={'class': 'form-check-input ms-auto',
                                           'style': 'width: 2.5em;',}),
            'star4': CheckboxInput(attrs={'class': 'form-check-input ms-auto',
                                           'style': 'width: 2.5em;',}),
            'star5': CheckboxInput(attrs={'class': 'form-check-input ms-auto',
                                           'style': 'width: 2.5em;',}),
        }



class SearchForm(forms.Form):
    blank_choice = [('', '---Выберите значение---'), ]

    CHOICES_WEB = [
        ('eat', 'ПОП'),
        ('hotel', 'КСР'),
        ('tourism', 'Туризм'),
        ('culture', 'Культура'),
        ('attr', 'Аттракции'),
    ]
    category = forms.ChoiceField(choices=blank_choice + CHOICES_WEB)


    CHOICES_PLAT = [
        ('gis', '2GIS'),
        ('vl', 'VL.ru'),
        ('trip', 'TripAdvisor'),
        ('gis;vl', '2GIS + VL.ru'),
        ('gis;trip', '2GIS + TripAdvisor'),
        ('vl;trip', 'VL.ru + TripAdvisor'),
        ('gis;vl;trip', '2GIS + VL.ru + TripAdvisor'),

    ]
    plat = forms.ChoiceField(choices=blank_choice + sorted(CHOICES_PLAT))


    CHOICES_CITIES = [
        ('Анучинский район', 'Анучинский район'),
        ('Арсеньевский городской округ', 'Арсеньевский городской округ'),
        ('Артёмовский городской округ', 'Артёмовский городской округ'),
        ('Барабашский район', 'Барабашский район'),
        ('Большой Камень городской округ', 'Большой Камень городской округ'),
        ('Владивостокский городской округ', 'Владивостокский городской округ'),
        ('Дальнереченский городской округ', 'Дальнереченский городской округ'),
        ('ЗАТО Фокино городской округ', 'ЗАТО Фокино городской округ'),
        ('Кавалеровский район', 'Кавалеровский район'),
        ('Кировский район', 'Кировский район'),
        ('Красноармейский район', 'Красноармейский район'),
        ('Лазовский район', 'Лазовский район'),
        ('Лесозаводский городской округ', 'Лесозаводский городской округ'),
        ('Михайловский район', 'Михайловский район'),
        ('Надеждинский район', 'Надеждинский район'),
        ('Находкинский городской округ', 'Находкинский городской округ'),
        ('Октябрьский район', 'Октябрьский район',),
        ('Ольгинский район', 'Ольгинский район'),
        ('Партизанский район', 'Партизанский район'),
        ('Пограничный район', 'Пограничный район'),
        ('Пожарский район', 'Пожарский район'),
        ('Спасск-Дальний городской округ', 'Спасск-Дальний городской округ'),
        ('Спасский район', 'Спасский район'),
        ('Тернейский район', 'Тернейский район'),
        ('Уссурийский городской округ', 'Уссурийский городской округ'),
        ('Ханкайский район', 'Ханкайский район'),
        ('Хасанский район', 'Хасанский район'),
        ('Хорольский район', 'Хорольский район'),
        ('Черниговский район', 'Черниговский район'),
        ('Чугуевский район', 'Чугуевский район'),
        ('Шкотовский район', 'Шкотовский район'),
        ('Яковлевский район', 'Яковлевский район'),
        ('Приморский край', 'Приморский край'),
    ]
    cities = forms.ChoiceField(choices=blank_choice + sorted(CHOICES_CITIES))

    CHOICES_RUBRIC = [
        ('Кафе', 'Кафе'),
        ('Рестораны', 'Рестораны'),
        ('Бары', 'Бары'),
        ('Доставка готовых блюд', 'Доставка готовых блюд'),
        ('Суши-бары','Суши-бары'),
        ('Быстрое питание', 'Быстрое питание'),
        ('Пиццерии', 'Пиццерии'),
        ('Столовые', 'Столовые'),
        ('Кофейни', 'Кофейни'),
        ('Точки кофе', 'Точки кофе'),
        ('Кафе-кондитерские', 'Кафе-кондитерские'),
        ('Кейтеринг', 'Кейтеринг'),
        ('Чайные клубы', 'Чайные клубы'),
        ('Рюмочные', 'Рюмочные'),
        ('Китайская кухня', 'Китайская кухня')
    ]
    rubrics = forms.ChoiceField(choices=sorted(CHOICES_RUBRIC))


    CHOICES_RUBRIC_HOTEL = [
        ('Базы отдыха', 'Базы отдыха'),
        ('Гостиницы, отели', 'Гостиницы, отели'),
        ('Санатории/Профилактории', 'Санатории'),
        ('Хостелы', 'Хостелы'),
    ]
    rubrics_hotel = forms.ChoiceField(choices=sorted(CHOICES_RUBRIC_HOTEL))

    CHOICES_TOUR = [
        ('Турфирмы', 'Турфирмы'),
        ('Оформление виз', 'Оформление виз'),
        ('Авиабилеты', 'Авиабилеты'),
        ('Организация экскурсий', 'Организация экскурсий'),
        ('Бронирование гостиниц', 'Бронирование гостиниц'),
        ('Железнодорожные билеты', 'Железнодорожные билеты'),
        ('Справочные службы', 'Справочные службы'),
    ]
    rubrics_tour = forms.ChoiceField(choices=sorted(CHOICES_TOUR))

    CHOICES_CULT = [
        ('Дома / дворцы культуры', 'Дома / дворцы культуры'),
        ('Художественные выставки / Галереи', 'Галереи'),
        ('Концертные залы', 'Концертные залы'),
        ('Музеи', 'Музеи'),
        ('Театры', 'Театры'),
        ('Городские оркестры', 'Городские оркестры'),
        ('Кинотеатры', 'Кинотеатры'),
        ('Ботанический сад / Дендрарий', 'Ботанический сад'),
        ('Океанариумы', 'Океанариумы'),
        ('Филармонии', 'Филармонии'),
        ('Дельфинарии', 'Дельфинарии'),
        ('Обсерватории', 'Обсерватории'),
        ('Цирки', 'Цирки'),
        ('Библиотеки', 'Библиотеки'),
    ]
    rubrics_cult = forms.ChoiceField(choices=sorted(CHOICES_CULT))

    CHOICES_ATTR = [
        ('Пляж', 'Пляж'),
        ('Сквер', 'Сквер'),
        ('Парк', 'Парк'),
        ('Площадь', 'Площадь'),
        ('Интересное здание', 'Интересное здание'),
        ('Смотровая площадка', 'Смотровая площадка'),
        ('Декоративный объект', 'Декоративный объект'),
        ('Стела, указатель', 'Стела, указатель'),
        ('Памятная доска', 'Памятная доска'),
        ('Стрит-арт', 'Стрит-арт'),
        ('Остров', 'Остров'),
        ('Сквер', 'Сквер'),
        ('Вершина горы', 'Вершина горы'),
        ('Памятник природы', 'Памятник природы'),
        ('Набережная', 'Набережная'),
        ('Культурные объекты и\xa0достопримечательности', 'Культурные объекты'),
        ('Водопад', 'Водопад'),
        ('Мост', 'Мост'),
    ]
    rubrics_attr = forms.ChoiceField(choices=sorted(CHOICES_ATTR))
