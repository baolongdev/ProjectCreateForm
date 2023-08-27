from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools


class GoogleFormGenerator:
    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/forms.body"]
        self.DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
        self.creds = None
        # ========================
        self.store = file.Storage('assets/data/token.json')
        self.client_secret = "assets/data/keyGoogleFrom.json"
        # ========================
        self.form_service = None
        self.form_id = None
        self.description = """
        Form này được tạo bảo blong đẹp trai không được cãi
        Cảm ơn bạn vì đã sử dụng tool của mình
        I <3 U
        ================
        """
                
    def authenticate(self):
        if not self.creds or self.creds.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret, self.SCOPES)
            self.creds = tools.run_flow(flow, self.store)
            self.form_service = discovery.build('forms', 'v1', http=self.creds.authorize(Http()), discoveryServiceUrl=self.DISCOVERY_DOC, static_discovery=False)


    def setting_configure(self, is_quiz = False):
        update = {"requests": [
            {
                "updateSettings": {
                    "settings": {
                        "quizSettings": {
                            "isQuiz": is_quiz
                        },
                    },
                    "updateMask": "quizSettings.isQuiz"
                }
            }
        ]}
        self.update_google_form(update)


    def update_google_form(self, json_data):
        try:
            self.form_service.forms().batchUpdate(formId=self.form_id["formId"], body=json_data).execute()
        except Exception as e:
            print(f"Error updating Google Form: {str(e)}")

    def convert_to_format(self, data, required=True, shuffle=True):
        update = {
            "requests": [{
                "createItem": {
                    "item": {
                        "title": data["title"],
                        "questionItem": {
                            "question": {
                                "required": required,
                                "grading": {
                                    "pointValue": 2,
                                    "correctAnswers": {
                                        "answers": [{"value": option} for option in data["item_right_answer"]],
                                    },
                                    "whenRight": {"text": "You got it!"},
                                    "whenWrong": {"text": "Sorry, that's wrong"}
                                },
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [{"value": option} for option in data["item_answer"]],
                                    'shuffle': shuffle
                                }
                            }
                        }
                    },
                    "location": {
                        "index": data["index"]
                    }         
                }   
            }]
        }
        self.update_google_form(update)
        # return update
    
    
    def read_data_from_json(self, file_data):
        # id=1 | item_title
        # id=2 | item_question
        # id=3 | item_answer
        # id=4 | item_right_answer
        # id=5 | item_ignore
        # model.labels[]
        index = -1
        format_data = {
            "item_title": [],
            "item_answer": [],
            "item_right_answer": [],
            "item_ignore": [],
        }
        for data in file_data["words"]:
            if data["label"] == "item_question":
                if index > -1:
                    self.convert_to_format(format_data)
                index += 1
                format_data = {
                    "index": index,
                    "title": data["value"],
                    "item_title": [],
                    "item_answer": [],
                    "item_right_answer": [],
                    "item_ignore": [],
                }
            elif data["label"] == "item_title":
                format_data[data["label"]].append(data["value"])    
            elif data["label"] == "item_answer":
                format_data[data["label"]].append(data["value"])    
            elif data["label"] == "item_right_answer":
                format_data[data["label"]].append(data["value"])    
            elif data["label"] == "item_ignore":
                format_data[data["label"]].append(data["value"])    

    def create_google_form(self, form_title, form_description, form_documentTitle):
        try:
            form  = {
                "info": {
                    "title": form_title,
                    "documentTitle": form_documentTitle
                }
            }
            self.form_id = self.form_service.forms().create(body=form).execute()
            update = {
                "requests": [
                    {
                        "updateFormInfo": {
                            "info": {
                                "description": self.description + form_description
                            },
                            "updateMask": "description"
                        },
                    },
                ]
            }
            self.update_google_form(update)
        except Exception as e:
            print(f"Error creating Google Form: {str(e)}")
            return None
    def get_link_form(self):
        form_id = self.form_id['formId']
        return f"https://docs.google.com/forms/d/{form_id}"