from tpb_mobile.forms import TorrentForm
from django.http import HttpResponse, HttpResponseRedirect
from tpb_mobile.models import Torrent, UserProfile
from django.contrib.auth import authenticate
import json
import tpb_mobile.settings as s

def create_torrent_record(request):
    '''
    adds a new torrent record to the database using form data from request
    '''
    form = TorrentForm(request.POST)
    if request.user.is_authenticated() and form.is_valid():
        try:
            new_torrent = Torrent.objects.get(magnet_link=form.cleaned_data['magnet_link'])   
        except:
            new_torrent = form.save(commit=False)
            new_torrent.save()
            
        # add torrent to user's queue
        try:
            profile = UserProfile.objects.get(user=request.user)
            profile.queue.add(new_torrent)
            profile.save()
        except:
            pass
    return HttpResponse("Torrent created successfully.")
        

def delete_torrent_record(request):
    '''
    removes the torrent with the magnet link matching the one in the POST dictionary from
    request.user's queue; DOES NOT actually delete the DB record for that torrent
    '''
    try:
        profile = UserProfile.objects.get(user=request.user)
        to_remove = Torrent.objects.get(magnet_link=request.POST.get('magnet_link'))
        profile.queue.remove(to_remove)
        profile.save()
    except:
        pass
    return HttpResponseRedirect('/queue/')

def register_client(request):
    '''
    attempts to authenticate using username and password. if successful, returns the user's uuid.
    if not, returns -1 to indicate error.
    '''
    username = request.POST('username', '')
    password = request.POST('password', '')
    
    user = authenticate(username=username, password=password)
    if user is not None:
        try:
            profile = UserProfile.objects.get(user=user)
            to_return = profile.uuid
        except:
            pass
    else:
        to_return = "-1"
    return HttpResponse(to_return, content_type="application/json")
        
        
def retrieve_queue(request, *args, **kwargs):
    '''
    runs a query to get all torrent records linked to user that matches user_id,
    then serializes the resulting queryset as json and returns it
    '''
    try:
        profile = UserProfile.objects.get(uuid=request.GET.get('uuid', ''))
        
        if profile.client_id == request.GET.get('client_id', ''):
            records = profile.queue.all()
            
            for i in records:
                i.status = s.DOWNLOADED
                i.save()
                
            response_data = records.values()
            response = json.dumps([dict(id=record) for record in response_data])
        else:
            response = "-1"
    except:
        response = "-1"
        
    return HttpResponse(response, content_type="application/json")