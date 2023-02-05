from django.db import models


class Contact(models.Model):
    trip_advisor = models.BooleanField(default=True)
    booking = models.BooleanField(default=True)
    vlru = models.BooleanField(default=True)
    gis = models.BooleanField(default=True)
    google = models.BooleanField(default=False)


    star1 = models.BooleanField(default=True)
    star2 = models.BooleanField(default=True)
    star3 = models.BooleanField(default=True)
    star4 = models.BooleanField(default=True)
    star5 = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.phone}"
        
        
        



