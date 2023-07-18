from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import ExamAir, Exam, Result
from django.shortcuts import redirect

class ExamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.exam_name = self.scope['url_route']['kwargs']['examPK']
        self.user = self.scope['user']
        

        await self.database_handeler(action = 'GET_AIR')
        await self.channel_layer.group_add(
            self.exam_name,
            self.channel_name
        )

        await self.accept()
        await self.channel_layer.group_send(
            self.exam_name,
            {
                'type':'group_handeler',
                'action':'userJoin',
                'username':self.user.username,
                'userPk':self.user.pk
            }
        )
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.exam_name,
            self.channel_name
        )
    async def receive(self, text_data=None):
        DICT_DATA = json.loads(text_data)
        action = DICT_DATA['action']
        print(DICT_DATA)
        
        
        if action == 'initiate':
            await self.database_handeler(action=action,data={
                'startTime': DICT_DATA['startTime'],
                'key':DICT_DATA['key']
            })
            
        elif action == 'updateKey':
            key = DICT_DATA['key']
            await self.database_handeler(action = action, data ={
                'key': key
            })
            
            await self.channel_layer.group_send(
                self.exam_name,
                {
                    'type':'group_handeler',
                    'action':'updateProgress',
                    'key': key,
                    'userPk': self.user.pk
                }
            )
            
        elif action == 'endExam':
            resultPk = await self.database_handeler(action = action, data={
                'spendTime':DICT_DATA['spendTime'],
            })

            await self.channel_layer.group_send(
                self.exam_name,
                {
                    'type':'group_handeler',
                    'action':'endExam',
                    'userPk':self.user.pk,
                    'resultPk':resultPk
                }
            )
        elif action == 'endAllExams':
            ended_data = await self.database_handeler(action= action, data= {
                'timeNow':DICT_DATA['timeNow']
            })

            await self.channel_layer.group_send(
                self.exam_name,
                {
                    'type':'group_handeler',
                    'action':'redirect',
                    'ended_data':ended_data
                }
            )
        elif action == 'startExam':
            await self.database_handeler(action = action, data = {
                'sTime':DICT_DATA['sTime']
            })


    async def group_handeler(self, data):
        action = data['action']
        
        if action == 'endExam':
            if self.admin or self.user.pk == data['userPk']:
                await self.send(json.dumps({
                    'action':'endExam',
                    'userPk':data['userPk'],
                    'resultPk':data['resultPk']
                }))
        elif action == 'updateProgress' and self.admin:
            key = data['key'].split(',')
            answered = 0
            for item in key:
                if item != '0':
                    answered += 1
            progressPercent = answered / len(key) * 100
            await self.send(json.dumps({
                'action':action,
                'userPk':data['userPk'],
                'progressPercent':progressPercent
            }))
        elif action == 'userJoin':

            if self.admin and self.user.pk != data['userPk']:
           
                await self.send(json.dumps({
                    'action':action,
                    'userPk':data['userPk'],
                    'username':data['username']
                }))
        elif action == 'forceEnd':
            await self.send(
                json.dumps()
            )
        elif action == 'redirect' :
            if(self.admin):
                await self.send(json.dumps({
                    'action':'ended_data',
                    'ended_data':data['ended_data']
                }))
            else:
                for item in data['ended_data']:
                    if item['userPk'] == self.user.pk:
                        await self.send(json.dumps({
                            'action':'redirect',
                            'resultPk':item['resultPk']
                        }))
    
    def AIR_TO_RESULT(self,spendTime, AIR):
        key = AIR.key.split(',')

        questions = self.Exam.get_all_questions
        
        corrects = 0
        wrongs = 0
        not_answered = 0
        
        wrongs_pk = ''
        corrects_pk = ''
        not_answered_pk = ''

        result_key = ''
        for index,choice   in enumerate(key):
            question = questions[index]
            answer = question.Answer
            if choice == answer:
                corrects_pk += str(question.pk)+','
                corrects += 1
            elif choice == '0':
                not_answered_pk += str(question.pk)+','
                not_answered += 1
            else:
                wrongs += 1
                wrongs_pk += str(question.pk)+','
            result_key+=choice
        wrongs_pk = wrongs_pk[:-1]
        corrects_pk = corrects_pk[:-1]
        not_answered_pk = not_answered_pk[:-1]
        percent = ((3 * corrects) - (wrongs))/(3*self.Exam.get_q_l)* 100
        percent = round(percent, 2)
        
        spendedTime = float(spendTime)
        if spendedTime < 0:
            spendedTime = 0


        result = Result.objects.create(Answers = result_key,
                                timeSpended = spendedTime,
                                percent = percent,
                                wrongs= wrongs,
                                corrects = corrects,
                                notAnswered = not_answered,
                                Exam_related = AIR.Exam_related,
                                participant = AIR.student_related,
                                wrongs_link = wrongs_pk,
                                corrects_link = corrects_pk,
                                notAnswered_link = not_answered_pk
                                )
        AIR.delete()
        return result.pk
    @database_sync_to_async
    def database_handeler(self,action, data=None):
        if action == 'GET_AIR':
            self.Exam = Exam.objects.get(pk = self.exam_name)
            
            if self.user.groups.filter(name='Admin').count() == 0:
                self.AIR = ExamAir.objects.get(student_related=self.user, Exam_related = self.Exam)
                self.admin = False
            else:
                self.admin = True
        elif action == 'initiate':

            self.AIR.key = data['key']
            self.AIR.startTime = data['startTime']
            self.AIR.save()
        elif action =='updateKey':
            self.AIR.key = data['key']
            self.AIR.save()
        
        elif action == 'endExam':
            return self.AIR_TO_RESULT(data['spendTime'], self.AIR)

        elif action == 'endAllExams':
            airs = ExamAir.objects.filter(Exam_related = self.Exam)
            ended_list = []
            timenow = data ['timeNow']
            for air in airs:
                timeSpend = int(timenow) - int(air.startTime)
                result_pk = self.AIR_TO_RESULT(timeSpend, air)
                ended_list.append({
                    'userPk':air.student_related.pk,
                    'resultPk':result_pk
                })
            self.Exam.endAllExams()
            return ended_list
        elif action == 'startExam':
            self.Exam.status = 'Started'
            self.Exam.Stime = data['sTime']
            self.Exam.save()