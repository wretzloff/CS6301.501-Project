@auth.requires_login()
def index():
    response.title = "Inbox for " + auth.user.email
    return dict()

def compose():
    response.title = "Compose message"
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def memcached():
    memcached = None
    retrieveMemcache = None
    response.title = "Memcache"

    form=FORM('key:', INPUT(_name='key'), 
        TEXTAREA(_name='value'), 
        INPUT(_type='submit', _value="Send"))

    retrieveForm =FORM('key:', INPUT(_name='key'), 
        INPUT(_type='submit', _value="Send"))

    if form.process(formname='form').accepted:
        cache.memcache.set(request.vars.key, request.vars.value)
        memcached = {request.vars.key: cache.memcache.get(request.vars.key)}

    if retrieveForm.process(formname='form_two').accepted:
        retrieveMemcache = cache.memcache.get(request.vars.key)

    return locals()


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

@auth.requires_login()
def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


auth.settings.allow_basic_login = True
@auth.requires_login()
@request.restful()
def api():
    import json
    session.forget()
    def GET(table,message_id='all'):
        if table == 'messages':
            if message_id.lower() == 'all':
                #Build an array of Messages
                user_id = auth.user.id
                message_list = []
                #Get the ID of the logged in user
                loggedInUserQuery = (db.auth_user.id == user_id)
                loggedInUserResults = db(loggedInUserQuery).select()
                user_row_id = loggedInUserResults[0].id
                #Get the messages that were sent to this user
                messageListQuery = (db.messages.to_user == user_row_id)
                messageListResults = db(messageListQuery).select()
                #For each message
                for messageRow in messageListResults:
                    #Get the text of the email
                    messageTxt = messageRow.email_text
                    #Get the email address of the user that this email is from
                    messageFromID = messageRow.from_user
                    fromUserQuery = (db.auth_user.id == messageFromID)
                    fromUserResults = db(fromUserQuery).select()
                    messageFrom = fromUserResults[0].email
                    #Add a row to the list that will be returned to the client
                    addToReturnList = 'From: "%s" Message: "%s"' % (messageFrom, messageTxt)
                    message_list.append(addToReturnList)
                
                #Convert the array to a JSON string and return the JSON string
                json_string = json.dumps(message_list)
                return json_string
            else:
                try:
                    message_id = int(message_id)
                except:
                    return 'FAIL! ID not an integer.'
				
                #Get the specified message
                user_id = auth.user.id
                message = ''
                for user_row in db(db.auth_user.id == user_id).select():
                    for message_row in user_row.messages.select():
                        if message_row.id == message_id:
                            message = message_row.email_text
                
                #If the message was found, convert it to a JSON string and return the JSON string
                if message == '':
                    return 'FAIL! Message id not found.'
                else:
                    messages = []
                    messages.append(message)
                    json_string = json.dumps(messages)
                    return json_string
                    
        elif table == 'contacts':
            #Build an array of Contacts
            contacts = []
            for row in db().select(db.auth_user.email):
                contacts.append(row.email)
            
            #Convert the array to a JSON string and return the JSON string
            json_string = json.dumps(contacts)
            return json_string
    def POST(*args,**vars):
        message = 'DEFAULT'
        target = 'TARGET'
        if len(args) > 0:
            if 'send' == args[0]:
                message = args[1]
                target = args[2]
        elif vars['type'] == 'send':
            message = vars['message']
            target = vars['to']
        if message == '' or message == 'DEFAULT':
            return 'FAIL! Invalid message.'
        else:
            try:
                row = db(db.auth_user.email == target).select(db.auth_user.id)
            except:
                return 'FAIL! Error at getting target user.'
            if len(row) == 0:
                return 'FAIL! Target %s not found.' % target
            else:
                target_id = row[0].id
                user_id = auth.user.id
                db.messages.insert(to_user=target_id, from_user=user_id, email_text=message)
            return 'You have posted to "%s" a message that says: "%s"' % (target, message)
    def PUT(*args,**vars):
        return ''
    def DELETE(table,message_id):
        if table == 'messages':
            try:
                message_id = int(message_id)
            except:
                return 'FAIL! ID not an integer.'
            db(db.messages.id == message_id).delete()
            return 'You have deleted message %s' % message_id
        return 'invalid'
    return locals()




#----- SSL ---------------
def generate_ssl_key():
    import os
    cert_dir, CERT_FILE, KEY_FILE = (os.path.join(request.folder, "private"), 'mysite.crt', 'mysite.key')
    return(dict(cert_dir=cert_dir, CERT_FILE=CERT_FILE, KEY_FILE=KEY_FILE))
