from django.db import models

class Crop(models.Model): #Similar to a table/models Hey
    name = models.CharField(max_length=100, unique=True)
    image = models.CharField(max_length=200, default="default.jpg")  # Path to the image in static folder

    def __str__(self):
        return self.name

class GAPSection(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="gap_sections")
    section_name = models.CharField(max_length=100)  #soil Requiremets, planting etc
    description = models.TextField()  # GAP details

    def __str__(self):
        return f"{self.crop.name} - {self.section_name}"

    class Meta:
        unique_together = ('crop', 'section_name')  # a crop cant have two similar sections