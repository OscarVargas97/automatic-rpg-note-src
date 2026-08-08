from django.contrib import admin

from .models import CampaignProject, TranscriptionJob, UploadedAudio

admin.site.register(CampaignProject)
admin.site.register(TranscriptionJob)
admin.site.register(UploadedAudio)
