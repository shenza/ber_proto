# -*- coding: latin-1 -*-

from flask import Flask, request, Response, render_template
from twilio.rest import Client
from twilio.jwt.taskrouter.capabilities import WorkerCapabilityToken
from twilio.twiml.voice_response import VoiceResponse
from flask_cors import CORS, cross_origin
import json

app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "ACf15ddc5bc9a07dee31e1f4e79d92e411"
auth_token  = "aa6457976b61becc24cbf586352f1f95"
auth_token = "714a4405dddcacb8368bd083dc11d5c7"
workspace_sid = "WS8acb2feb114eebf1ca9d6697dc9cc27e"
workflow_sid = "WW8b5df83260c846f8904b368ffe9dcfe5"
task_queue_sid = "WQ1b7d7243fa2ee3bdf6c6a87aedb45ebf"

#test
#account_sid = "SK44117cae0af7e1b95ba5f25e9d36d60b"
#auth_token  = "AFOHa42tZRiNmSVeaE7dxotxjmv0AJc6"

client = Client(account_sid, auth_token)

@app.route("/assignment_callback", methods=['GET', 'POST'])
def assignment_callback():
    """Respond to assignment callbacks with an acceptance and 200 response"""

    ret = '{"instruction": "dequeue", "from"="+15556667777"}' # a verified phone number from your twilio account
    resp = Response(response=ret, status=200, mimetype='application/json')
    return resp

@app.route("/create_task", methods=['GET', 'POST'])
def create_task():
    data_in = '{"type":"support"}'
    data_in = request.data
    print (data_in)
    #print (request.json())
    
    """Creating a Task"""
    task = client.taskrouter.workspaces(workspace_sid) \
                 .tasks.create(workflow_sid=workflow_sid, attributes=data_in)

    print (task)
    print(task.attributes)
    print ('1111111111111111111111111111')
    print (dir(task))
    print ('22222222222222222222222222')
    print (task.sid)
    print (task.links)

    #resp = Response({}, status=200, mimetype='application/json')
    data = {"taskSid":task.sid}
    resp = Response(json.dumps({'success':True, "payload":data}), status=200, mimetype='application/json')
    return resp

@app.route("/check_reservation", methods=['GET', 'POST'])
def check_reservation():
    """ get list of current reservations - used to get the worker sid """
    #https://www.twilio.com/docs/taskrouter/api/reservations#reservations-list-resource
    #GET /v1/Workspaces/{WorkspaceSid}/Tasks/{TaskSid}/Reservations
    print (request.json['taskSid'])
    taskSid = request.json['taskSid']
    #taskSid = request.args.get('taskSid')

    client = Client(account_sid, auth_token)

    reservations = client.taskrouter \
                        .workspaces(workspace_sid) \
                        .tasks(taskSid) \
                        .reservations \
                        .list(limit=20)

    data = {}
    for record in reservations:

        #print (dir(record))
        #print(record.sid)
        if (record.reservation_status in ('accepted')):
            print (record.worker_sid)
            #print (record.reservation_status)
            data.update({'workerSid':record.worker_sid})
            #no need to continue 
            break

    resp = Response(json.dumps({'success':True, "payload":data}), status=200, mimetype='application/json')
    return resp

@app.route("/accept_reservation", methods=['GET', 'POST'])
def accept_reservation():
    """Accepting a Reservation"""

    task_sid = request.json['taskSid']
    reservation_sid = request.json['reservationSid']
 

    #return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    reservation = client.taskrouter.workspaces(workspace_sid) \
                        .tasks(task_sid) \
                        .reservations(reservation_sid) \
                        .update(reservation_status='accepted')

    print(reservation.reservation_status)
    print(reservation.worker_name)

    resp = Response(json.dumps({'success':True}), status=200, mimetype='application/json')
    return resp


@app.route("/get_worker_details", methods=['GET', 'POST'])
def get_worker_details():
    """ get worker details """
    #https://www.twilio.com/docs/taskrouter/api/worker#fetch-a-worker-resource
    #https://taskrouter.twilio.com/v1/Workspaces/{WorkspaceSid}/Workers/{Sid}

    print (request.json['workerSid'])
    workerSid = request.json['workerSid']
    #taskSid = request.args.get('taskSid')

    client = Client(account_sid, auth_token)

    worker = client.taskrouter \
                .workspaces(workspace_sid) \
                .workers(workerSid) \
                .fetch()

    #print (worker.__dict__)
    #print(worker.activity_name)
    print (worker.friendly_name)
    
    print ('----------------------------------')
    #convert to dict
    #print (json.loads(worker.attributes))
    data = {"friendly_name":worker.friendly_name}
    #flatlining it to make it easier on the javascript side
    data.update(json.loads(worker.attributes))


    resp = Response(json.dumps({'success':True, "payload":data}), status=200, mimetype='application/json')
    return resp

@app.route("/get_worker_stats", methods=['GET', 'POST'])
def get_worker_stats():
    """ get worker details """
    #https://www.twilio.com/docs/taskrouter/api/worker#fetch-a-worker-resource
    #https://taskrouter.twilio.com/v1/Workspaces/{WorkspaceSid}/Workers/{Sid}

    print (request.json['workerSid'])
    workerSid = request.json['workerSid']
    #taskSid = request.args.get('taskSid')

    client = Client(account_sid, auth_token)

    worker = client.taskrouter \
                .workspaces(workspace_sid) \
                .workers(workerSid) \
                .fetch()

    #print (worker.__dict__)
    #print(worker.activity_name)
    print (worker.friendly_name)
    
    print ('----------------------------------')
    #convert to dict
    #print (json.loads(worker.attributes))
    data = {"friendly_name":worker.friendly_name}
    #flatlining it to make it easier on the javascript side
    data.update(json.loads(worker.attributes))


    resp = Response(json.dumps({'success':True, "payload":data}), status=200, mimetype='application/json')
    return resp


from flask import make_response

@app.route("/agents", methods=['GET', 'POST'])
#@cross_origin(origin='*')
def generate_view():
    worker_sid = request.args.get('WorkerSid')

    worker_capability = WorkerCapabilityToken(account_sid, auth_token, workspace_sid, worker_sid)
    worker_capability.allow_update_activities()
    worker_capability.allow_update_reservations()
    worker_capability.allow_fetch_subresources()
    worker_capability.allow_update_activities()
    worker_capability.allow_update_reservations()
    worker_capability.allow_fetch_subresources()
    worker_capability.allow_update_subresources()
    worker_capability.allow_delete_subresources()

    worker_capability.allow_fetch_activities()
    worker_capability.allow_fetch_worker_reservations()
    worker_capability.allow_web_sockets()
    worker_capability.allow_fetch_self()
    

    worker_token = worker_capability.to_jwt().decode('utf-8')

    #return render_template('agent.html', worker_token=worker_token)

    r = make_response(render_template('agent.html', worker_token=worker_token, current_worker_sid=worker_sid))
    r.headers.set('Access-Control-Allow-Origin', "*'")
   
    return r

#from twilio.jwt.taskrouter.capabilities import TaskQueueCapabilityToken
from twilio.jwt.taskrouter.capabilities import WorkspaceCapabilityToken, TaskQueueCapabilityToken

@app.route("/student_create_task", methods=['GET', 'POST'])
#@cross_origin(origin='*')
def generate_view2():
    name = request.args.get('name')
    level = request.args.get('level')
    language = request.args.get('language')

    taskQ = TaskQueueCapabilityToken(account_sid=account_sid, auth_token=auth_token, workspace_sid=workspace_sid, task_queue_sid=task_queue_sid)
    taskQ.allow_fetch_subresources()
    taskQ.allow_update_subresources()
    taskQ_token = taskQ.to_jwt().decode('utf-8')
    print ('**********************************')
    print (taskQ_token)
    print ('**********************************')
    '''
    #worker_capability = WorkerCapabilityToken(account_sid, auth_token, workspace_sid, worker_sid)
    worker_capability = TaskQueueCapabilityToken(account_sid, auth_token, workspace_sid, task_queue_sid)   
    #worker_capability.allow_update_activities()
    #worker_capability.allow_update_reservations()
    worker_capability.allow_fetch_subresources()
    #worker_capability.allow_update_activities()
    #worker_capability.allow_update_reservations()
    worker_capability.allow_fetch_subresources()
    worker_capability.allow_update_subresources()
    worker_capability.allow_delete_subresources()

    #worker_capability.allow_fetch_activities()
    #worker_capability.allow_fetch_worker_reservations()
    worker_capability.allow_web_sockets()
    worker_capability.allow_fetch_self()
    '''
    #worker_capability = WorkerCapabilityToken(account_sid, auth_token, workspace_sid, worker_sid)
    #used to retrieve task assignment stats
    task_capability = WorkspaceCapabilityToken(account_sid=account_sid, auth_token=auth_token, workspace_sid=workspace_sid)    
    task_capability.allow_fetch_subresources()
    task_capability.allow_fetch_subresources()
    task_capability.allow_update_subresources()
    task_capability.allow_delete_subresources()
    task_capability.allow_web_sockets()
    task_capability.allow_fetch_self()

    task_token = task_capability.to_jwt().decode('utf-8')

    #return render_template('agent.html', worker_token=worker_token)

    r = make_response(render_template('student.html', task_token=task_token, name=name, level=level, language=language, taskQ_token=taskQ_token))
    r.headers.set('Access-Control-Allow-Origin', "*'")
   
    return r




@app.route("/health", methods=['GET', 'POST'])
#@cross_origin(origin='*')
def generate_health_check():
    r = make_response(render_template('student.html'))
    r.headers.set('Access-Control-Allow-Origin', "*'")
   
    return r
if __name__ == "__main__":
    #logging.getLogger('flask_cors').level = logging.DEBUG
    app.run(debug=True)