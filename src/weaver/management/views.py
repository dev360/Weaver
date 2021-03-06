#coding=utf-8

from django import http
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext_lazy, ugettext as _
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext

from management.models import EC2Helper, ServerImage, KeyPairManager, Site, Server
from management.forms import ServerImageForm, SiteForm, ServerForm

from boto.ec2.connection import EC2Connection

def index(request):
    return render_to_response('management/index.html', {}, context_instance=RequestContext(request))


def serverimage_index(request):
    images = ServerImage.objects.get_all()
    return render_to_response('management/serverimage_index.html', {'images': images}, context_instance=RequestContext(request))
    

def serverimage_manage(request, ami_id):
    # Get some stuff
    try:
        ami = EC2Helper.get_image(ami_id)
    except:
        raise Exception('The AMI you entered is invalid.')
    
    try:
        image = ServerImage.objects.get(ami_id=ami_id)
        image.ami = ami
        image.ami_id = ami.id
    except ServerImage.DoesNotExist:
        image = ServerImage(ami=ami)
        image.ami_id = ami.id
        image.name = ami.name if ami.name else ""
        image.save()
    
    form = ServerImageForm(instance=image)
    
    if request.method == 'POST':
        
        form = ServerImageForm(data=request.POST, instance=image)
        
        if form.is_valid():    
            image = form.save()
            return HttpResponseRedirect(reverse('management:serverimage-index'))
    
    return render_to_response('management/serverimage_manage.html', { 'form': form, 'image': image, }, context_instance=RequestContext(request))




def keypairs_index(request):
    ec2_keypairs = KeyPairManager.get_ec2_public_keys()
    local_keypairs = KeyPairManager.get_local_private_keys()
    return render_to_response('management/keypairs_index.html', { 'ec2_keypairs': ec2_keypairs, 'local_keypairs': local_keypairs }, context_instance=RequestContext(request))
    
    
def site_index(request):
    sites = Site.objects.all()
    return render_to_response('management/site_index.html', { 'sites': sites }, context_instance=RequestContext(request))
        

def site_add(request):
    form = SiteForm()

    if request.method == 'POST':
        form = SiteForm(request.POST)
        
        if form.is_valid():
            config = form.save()
            return HttpResponseRedirect(reverse('management:site-edit', args=(config.slug,)))
    
    return render_to_response('management/site_add.html', { 'form': form }, context_instance=RequestContext(request))


def site_edit(request, site_slug):
    site = get_object_or_404(Site, slug=site_slug)
    form = SiteForm(instance=site)

    if request.method == 'POST':
        form = SiteForm(request.POST, request.FILES, instance=site)

        if form.is_valid():
            site = form.save()
            return HttpResponseRedirect(reverse('management:site-edit', args=(site.slug,)))

    return render_to_response('management/site_edit.html', { 'form': form, 'site': site }, context_instance=RequestContext(request))


def site_delete(request, site_slug):
    site = get_object_or_404(Site, slug=site_slug)

    if request.method == 'POST':
        if request.POST.get('delete', '0') == '1':
            site.delete()
            return HttpResponseRedirect(reverse('management:site-index'))

    return render_to_response('management/site_delete.html', { 'site': site }, context_instance=RequestContext(request))


def server_index(request):
    servers = Server.objects.get_all()
    return render_to_response('management/server_index.html', { 'servers': servers }, context_instance=RequestContext(request))
    
    
def server_manage(request, instance_id):
    # Get some stuff
    try:
        instance = EC2Helper.get_instance(instance_id)
    except:
        raise Exception('The instance id you entered is invalid.')
    
    try:
        server = Server.objects.get(instance_id=instance_id)
        server.instance = instance
        server.instance_id = instance.id
    except Server.DoesNotExist:
        server = Server(instance=instance)
        server.instance_id = instance.id
        server.save()
    
    form = ServerForm(instance=server)
    
    if request.method == 'POST':
        form = ServerForm(data=request.POST, instance=server)
        
        if form.is_valid():    
            server = form.save()
            return HttpResponseRedirect(reverse('management:server-index'))
    
    return render_to_response('management/server_manage.html', { 'form': form, 'server': server, }, context_instance=RequestContext(request))
    