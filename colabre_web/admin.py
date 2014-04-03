from models import *
from statistics.models import *
from django.contrib import admin


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = [
                     'user__email',
                     'user__first_name',
                     'user__last_name',
    ]
    list_display = ('id', 'user_', 'last_login', 'num_jobs', 'is_verified' )
    list_filter = ('is_verified', 'gender')
    
    def last_login(self, profile):
        return profile.user.last_login
    
    last_login.admin_order_field = 'user__last_login'
    
    def num_jobs(self, profile):
        return len(profile.jobs)
    
    num_jobs.short_description = u'n jobs'
    
    def user_(self, profile):
        return "%s - %s <%s>" % (profile.user.username, profile.user.first_name, profile.user.email)
    
    user_.admin_order_field = 'user__first_name'

class JobAdmin(admin.ModelAdmin):
    search_fields = [
                     'description', 
                     'contact_email', 
                     'job_title__segment__name',
                     'job_title__name',
                     'profile__user__email',
                     'profile__user__first_name',
                     'profile__user__last_name',
    ]
    readonly_fields = ('uuid',)
    list_filter = ('spam', 'active', 'job_title__segment')
    list_display = ('id', 'profile', 'segment', 'job_title',)
    
    def segment(self, job):
        return job.job_title.segment.name
    
    segment.admin_order_field  = 'job_title__segment__name'

admin.site.register(Country)
admin.site.register(Region)
admin.site.register(City)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Segment)
admin.site.register(JobTitle)
admin.site.register(Company)
admin.site.register(Resume)
admin.site.register(Job, JobAdmin)
admin.site.register(UserProfileVerification)
admin.site.register(JobStatistics)
admin.site.register(JobApplication)
admin.site.register(ResumeStatistics)
