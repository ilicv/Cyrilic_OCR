from django.urls import path
from django.views.generic import RedirectView
from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    #path(r'^home/?$', views.index, name='index'),
    path('', views.index, name='index'),

    #url(r'^favicon\.ico$',RedirectView.as_view(url='/Cyrilic_OCR/img/favicon.ico')),

    #path('process_scan/', views.process_scan, name='process_scan'),
    path('show_result/', views.show_result, name='show_result'),
    #path('show_result_modified/', views.show_result_modified, name='show_result_modified'),

    
    path('start_ocr/', views.start_ocr, name='start_ocr'),
    path('save_corrections/', views.save_corrections, name='save_corrections'),
    path('show_paragraph/', views.show_paragraph, name='show_paragraph'),
    path('not_processed_pages/', views.not_processed_pages, name='not_processed_pages'),
    path('ocr_not_processed_pages/', views.ocr_not_processed_pages, name='ocr_not_processed_pages'),
    path('compare/', views.compare, name='compare'),
    path('save_compare/', views.save_compare, name='save_compare'),
    path('restore_ocr_text/', views.restore_ocr_text, name='restore_ocr_text'),
    
    
]

urlpatterns += staticfiles_urlpatterns()
