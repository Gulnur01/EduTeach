from django import template
from statistics import mean

register = template.Library()

@register.filter
def average_grade(grades_data):
    grades = [grade['grade'] for grade in grades_data]
    return round(mean(grades), 2) if grades else 0

@register.filter
def max_grade(grades_data):
    grades = [grade['grade'] for grade in grades_data]
    return max(grades) if grades else 0

@register.filter
def min_grade(grades_data):
    grades = [grade['grade'] for grade in grades_data]
    return min(grades) if grades else 0
