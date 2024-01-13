from django.core.mail import send_mail
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
import json
from django.shortcuts import render, redirect
from .models import *
import random
import os
from dotenv import load_dotenv
load_dotenv()
import PyPDF2
import pandas as pd
import json
import docx
import openai
from llama_index import VectorStoreIndex, SimpleDirectoryReader
import random
import shutil
import datetime
from datetime import timezone
import string


class UserFunctions:
    def index(request):
        try:
            # Checking if private key is present or not
            if not 'elara_privatekey' in request.session:
                return redirect('login')
            
            # Checking if user exists or not
            private_key = request.session['elara_privatekey']
            if User.objects.filter(private_key=private_key).exists():
                user = User.objects.get(private_key=private_key)
                name = user.username
                first_name = name.split(" ")[0]
                last_name = name.split(" ")[0][-1]
                if len(name.split(" ")) > 1:
                    last_name = name.split(" ")[1][0]
                name_abbr = first_name[0] + last_name
                name_abbr = name_abbr.upper()
                return render(request, 'chat.html', {'user': user, 'name_abbr': name_abbr})
            else:
                return redirect('login')
        except Exception as e:
            print(e)
            return redirect('login')

    def login(request):
        return render(request, 'login.html')

    def signup(request):
        return render(request, 'signup.html')

    def logout(request):
        del request.session['elara_privatekey']
        return redirect('login')

    def login_user(request):
        try:
            email = request.POST['email']
            password = request.POST['password']
            if User.objects.filter(email=email, password=password).exists():
                user = User.objects.get(email=email, password=password)
                private_key = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
                request.session['elara_privatekey'] = private_key
                user.private_key = private_key
                user.save()
                return redirect('index')
            else:
                return redirect('login')
        except Exception as e:
            print(e)
            return redirect('login')
        
    def signup_user(request):
        try:
            email = request.POST['email']
            password = request.POST['password']
            username = request.POST['name']
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if user.otp_verified:
                    return redirect('login')
                else:
                    otp = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                    user.otp = otp
                    user.save()
                    subject = "OTP for Elara"
                    message = "Your OTP is "+str(otp) + "\n Please do not share with anyone else. \n\n Thanks, \n Ananya Vishnoi"
                    reciever_list = [email]
                    send_mail(subject,message,os.getenv('EMAIL_HOST_USER'),reciever_list)
                    return render(request, 'otp.html', {'email': email})
            else:
                otp = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                user = User(email=email, password=password, username=username, otp = otp)
                user.save()
                subject = "OTP for Elara"
                message = "Your OTP is "+str(otp) + "\n Please do not share with anyone else. \n\n Thanks, \n Ananya Vishnoi"
                reciever_list = [email]
                send_mail(subject,message,os.getenv('EMAIL_HOST_USER'),reciever_list)
                return render(request, 'otp.html', {'email': email})
        except Exception as e:
            print(e)
            return redirect('signup')
    
    def verify_otp(request):
        try:
            email = request.POST['email']
            otp = request.POST['otp']
            if User.objects.filter(email=email, otp=otp).exists():
                user = User.objects.get(email=email, otp=otp)
                user.otp_verified = True
                user.otp = ''
                user.save()
                return redirect('login')
            else:
                return render(request, 'otp.html', {'email': email})
        except Exception as e:
            print(e)
            return render(request, 'otp.html', {'email': email})
        

temp_index_storage = []

class HelperFunctions:
    def read_text_from_docx(docx_path):
        try:
            doc = docx.Document(docx_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return str(e)

    def read_text_from_pdf(pdf_path):
        try:
            pdf_file = open(pdf_path, 'rb')
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            pdf_file.close()
            return text
        except Exception as e:
            return str(e)
        
    def read_text_from_txt(txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8') as txt_file:
                text = txt_file.read()
            return text
        except Exception as e:
            return str(e)

    def read_text_from_csv(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as csv_file:
                text = csv_file.read()
            return text
        except Exception as e:
            return str(e)

    def excel_to_csv(xlsx_path):
        df = pd.read_excel(xlsx_path)
        output_csv_file = os.path.splitext(xlsx_path)[0] + '.csv'
        df.to_csv(output_csv_file, index=False)
        return output_csv_file

    def read_text_from_file(file_path):
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.docx':
            return HelperFunctions.read_text_from_docx(file_path)
        elif file_extension == '.pdf':
            return HelperFunctions.read_text_from_pdf(file_path)
        elif file_extension == '.txt':
            return HelperFunctions.read_text_from_txt(file_path)
        elif file_extension == ".csv":
            return HelperFunctions.read_text_from_csv(file_path)
        elif file_extension == ".xlsx":
            csv_file = HelperFunctions.excel_to_csv(file_path)
            return HelperFunctions.read_text_from_csv(csv_file)
        else:
            return "Unsupported file format"

    def exists_in_cache(index_id):
        for x in temp_index_storage:
            if x["index_id"] == index_id:
                return True
        return False

    
    # This function creates index for a file and stores it in temp_index_storage using langchain
    def create_index_for_file(email,data,index_id,original_name):
        random_folder_name = ''.join(random.choices(string.ascii_lowercase +string.digits, k=15))
        random_file_name = ''.join(random.choices(string.ascii_lowercase +string.digits, k=15))
        random_file_name = random_file_name + ".txt"
        os.mkdir(random_folder_name)
        destination_path = random_folder_name +"/" + random_file_name
        with open(destination_path, 'w') as random_file_name:
            random_file_name.write(data)
        documents= SimpleDirectoryReader(random_folder_name).load_data()
        index = VectorStoreIndex.from_documents(documents)
        temp_jso = {
            "email": email,
            "index": index,
            "index_id": index_id,
            "chat_type" : "file",
            "name" : original_name
        }
        temp_index_storage.append(temp_jso)
        shutil.rmtree(random_folder_name) 

    def create_index_for_folder(email,folder,index_id,original_name):
        if HelperFunctions.exists_in_cache(index_id):
            return
        documents= SimpleDirectoryReader(folder).load_data()
        index = VectorStoreIndex.from_documents(documents)
        temp_jso = {
            "email": email,
            "index": index,
            "index_id": index_id,
            "chat_type" : "folder",
            "name" : original_name
        }
        temp_index_storage.append(temp_jso)

    def chatgpt(prompt):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )

        answer = response['choices'][0]['message']['content']
        return answer

    def search_and_extract_context(long_text, short_text):
        long_text_lines = long_text.split('\n')
        short_text_lines = short_text.split()

        context_lines = []
        for i, line in enumerate(long_text_lines):
            for word in short_text_lines:
                if word in line:
                    start_idx = max(0, i - 2)
                    end_idx = min(len(long_text_lines), i + 3)
                    context = long_text_lines[start_idx:end_idx]
                    context_lines.extend(context)

        return '\n'.join(context_lines)

    def remove_repeating_sentences(text):
        lines = text.split('\n')
        unique_lines = []
        for line in lines:
            if line not in unique_lines:
                unique_lines.append(line)

        return '\n'.join(unique_lines)

    def retriever_2(email,question,index_id):
        print("Deep Check started")
        user = User.objects.get(email=email)
        all_data = Index.objects.get(user=user,index_id=index_id).all_data
        
        all_data = all_data.lower()

        # removing smaller words in the question
        question = question.split()
        new_question = []
        for x in question:
            if len(x) > 2:
                new_question.append(x)

        question = " ".join(new_question)

        # removing smaller words in the data
        all_data = all_data.split()
        new_all_data = []
        for x in all_data:
            if len(x) > 2:
                new_all_data.append(x)

        all_data = " ".join(new_all_data)

        result = HelperFunctions.search_and_extract_context(all_data, question)
        result = HelperFunctions.remove_repeating_sentences(result)
        words_in_result = len(result.split())
        if words_in_result > 1500:
            result = result.split()
            result = result[:1500]
            result = " ".join(result)


        prompt = '''
        Answer the following question based on the context provided. Only follow the context and do not self generate the answer\n
        Context : ''' + result + '''\n
        Question: ''' + question + '''\n
        '''

        return HelperFunctions.chatgpt(prompt)

    def remove_duplicates():
        # remove duplicates from temp_index_storage
        global temp_index_storage
        temp = []
        for x in temp_index_storage:
            # match by email and index_id inside x
            flag = False
            for y in temp:
                if x["email"] == y["email"] and x["index_id"] == y["index_id"]:
                    flag = True
                    break
            if flag == False:
                temp.append(x)
        temp_index_storage = temp


class ChatFunctions:
    @api_view(['GET'])
    def chat_with_document(request):
        # getting all required data from frontend
        if "question" not in request.GET:
            return Response({"error": "No question provided"}, status=status.HTTP_400_BAD_REQUEST)
        if "email" not in request.GET:
            return Response({"error": "No email provided"}, status=status.HTTP_400_BAD_REQUEST)
        if "index_id" not in request.GET:
            return Response({"error": "No index_id provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        question = request.GET["question"]
        email = request.GET["email"]
        index_id = request.GET["index_id"]
        user = User.objects.get(email=email)

        # check if index exists in cache if not then first we try to create it
        index = None
        for x in temp_index_storage:
            if x["index_id"] == index_id:
                index = x["index"]
                break
        
        # Trying to create index if none exists in cache
        if index == None:
            # try recreating all index and rechecking if stil not then say no index found
            
            index_from_database = Index.objects.get(user=user,index_id=index_id)
            if index_from_database.chat_type == "file":
                HelperFunctions.create_index_for_file(email,index_from_database.all_data,index_id,index_from_database.file_folder_name)
            else:
                HelperFunctions.create_index_for_file(email,index_id,index_from_database.file_folder_name)
            for x in temp_index_storage:
                if str(x["index_id"]) == str(index_id):
                    index = x["index"]
                    x["chat_type"] = "folder"
                    break
            if index == None:
                return Response({"error": "No index found"}, status=status.HTTP_400_BAD_REQUEST)
            
        # If index is found then we query it using llama index 
        query_engine = index.as_query_engine()
        answer = query_engine.query(question)
        if "I'm sorry" in str(answer):
            answer = HelperFunctions.retriever_2(email,question,index_id)
        res = {
            "response": str(answer)
        }

        # saving chat history in database
        old_chat = Index.objects.get(user=user,index_id=index_id).chat_history
        if old_chat == None:
            old_chat = [
                {
                    "question": question,
                    "answer": str(answer)
                }
            ]
        else:
            old_chat = json.loads(old_chat)
            old_chat.append(
                {
                    "question": question,
                    "answer": str(answer)
                }
            )

        Index.objects.filter(user=user,index_id=index_id).update(chat_history=json.dumps(old_chat))
        return Response(res, status=status.HTTP_200_OK)
            
    @api_view(['GET'])
    def get_all_files(request):
        email = request.GET["email"]
        return_data = []
        for x in temp_index_storage:
            if x["email"] == email:
                data = x.copy()
                return_data.append(data)
        for x in return_data:
            user = User.objects.get(email=email)
            all_files = Index.objects.get(index_id=x["index_id"],user=user).all_files
            if all_files == None:
                all_files = []
            else:
                all_files = all_files.replace("[","")
                all_files = all_files.replace("]","")
                all_files = all_files.split(",")
            x["all_files"] = all_files
            if not Index.objects.filter(index_id=x["index_id"],user=user).exists():
                # remove this index from temp_index_storage
                temp_index_storage.remove(x)
                continue
            timestamp = Index.objects.get(index_id=x["index_id"],user=user).last_chat_time
            current_time = datetime.datetime.now(timezone.utc)
            difference = current_time - timestamp
            x["index"] = None
            if difference.total_seconds() > 86400:
                x["timestamp"] = timestamp.strftime("%d %b %Y %H:%M:%S")
            else:
                x["timestamp"] = "1d"
        return Response({"data": return_data}, status=status.HTTP_200_OK)

    @api_view(['GET'])
    def get_all_files_in_folder(request):
        
        email = request.GET["email"]
        index_id = request.GET["index_id"]
        user = User.objects.get(email=email)
        index = Index.objects.get(index_id=index_id,user=user)
        all_files = index.all_files
        all_files = all_files.replace("[","")
        all_files = all_files.replace("]","")
        all_files = all_files.split(",")
        return Response({"data": all_files}, status=status.HTTP_200_OK)

    @api_view(['POST'])
    def upload_file(request):
        # check for files and email
        if "email" not in request.POST:
            return Response({"error": "No email provided"}, status=status.HTTP_400_BAD_REQUEST)
        if "file" not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # save file to local
        try:
            # Get file
            email = request.POST["email"]
            file = request.FILES["file"]

            # Get files original name to create index database
            original_file_name = file.name
            destination_path = file.name

            user = User.objects.get(email=email)
            # Check if file already exists if it does do not allow user to upload it
            if Index.objects.filter(user=user,file_folder_name=original_file_name).exists():
                return Response({"error": "File already exists. Please delete file if you need to update it"}, status=status.HTTP_400_BAD_REQUEST)

            # Getting file data
            with open(destination_path, 'wb') as destination_file:
                for chunk in file.chunks():
                        destination_file.write(chunk)
            
            # Reading file data
            file_data = HelperFunctions.read_text_from_file(destination_path)
            file_data = file_data.lower()
            
            # Saving file data to database
            file_data = file_data + "\n\n" + "File Name: " + destination_path

            # removing file from local
            os.remove(destination_path)

            # Creating index
            index_id = ''.join(random.choices(string.ascii_lowercase +string.digits, k=15))
            HelperFunctions.create_index_for_file(email, file_data,index_id,original_file_name)

            # create an entry in database and save index id with it this will be returned with chat list to frontend
            Index.objects.create(index_id=index_id,user=user,file_folder_name = original_file_name,all_data=file_data,chat_type = "file")
            return Response({"message": "File uploaded successfully","index_id":index_id}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"error": "Error saving file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @api_view(['POST'])
    def upload_folder(request):
        if "email" not in request.POST:
            return Response({"error": "No email provided"}, status=status.HTTP_400_BAD_REQUEST)
        if "total_files" not in request.POST:
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)
        if "folder_name" not in request.POST:
            return Response({"error": "No folder name provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # save file to local
        try:
            # Getting all data from frontend
            total_files = int(request.POST["total_files"])
            email = request.POST["email"]
            all_data = ""

            # Get files original name to create index database
            original_folder_name = request.POST["folder_name"]
            random_folder_name = ''.join(random.choices(string.ascii_lowercase +string.digits, k=15))
            os.mkdir(random_folder_name)
            user = User.objects.get(email=email)
            # Check if file already exists if it does do not allow user to upload it
            if Index.objects.filter(user=user,file_folder_name=original_folder_name).exists():
                return Response({"error": "Folder already exists. Please delete folder if you need to update it"}, status=status.HTTP_400_BAD_REQUEST)
            
            list_of_all_files = []
            # Loop through all files and save them one by one
            for x in range(0,total_files):

                # Get the file
                file = request.FILES["folder_"+str(x)]
                list_of_all_files.append(file.name)
                original_Destination_path = original_folder_name+"/"+file.name
                destination_path = random_folder_name+ "/" + file.name
                with open(destination_path, 'wb') as destination_file:
                    for chunk in file.chunks():
                            destination_file.write(chunk)
                    filename = file.name
                    data_temp = "Filename : " + str(filename)
                    destination_file.write(data_temp.encode('utf-8'))
                
                file_data = HelperFunctions.read_text_from_file(destination_path)
                file_data = file_data.lower()
                
                file_data = file_data + "\n\n" + "File Name: " + destination_path
                all_data += file_data

            index_id = ''.join(random.choices(string.ascii_lowercase +string.digits, k=15))
            HelperFunctions.create_index_for_folder(email, random_folder_name,index_id,original_folder_name)
            
            Index.objects.create(index_id=index_id,user=user,file_folder_name = original_folder_name,all_files=str(list_of_all_files),all_data=all_data,chat_type = "folder")
            shutil.rmtree(random_folder_name)
            return Response({"message": "File uploaded successfully",'index_id' : index_id}, status=status.HTTP_200_OK)


        except Exception as e:
            print(e)
            return Response({"error": "Error saving file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @api_view(['POST'])
    def create_index(request):
        '''
        This function creates index that have been lost from cache so that server can be restarted without a problem
        It takes email and is to be called from frontend so that it can be called for all users without too much delay
        '''
        
        if "email" not in request.POST:
            return Response({"error": "No email provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        email = request.POST["email"]
        user = User.objects.get(email=email)
        index = Index.objects.filter(user=user)
        folder_id = []
        for x in index:
            if x.chat_type == "file":
                HelperFunctions.create_index_for_file(email,x.all_data,x.index_id,x.file_folder_name)
            else:
                folder_id.append(x.index_id)    
                HelperFunctions.create_index_for_file(email,x.all_data,x.index_id,x.file_folder_name)
        for x in temp_index_storage:
            if x["index_id"] in folder_id:
                x["chat_type"] = "folder"
        HelperFunctions.remove_duplicates()
        return Response({"message": "Index created successfully"}, status=status.HTTP_200_OK)

    @api_view(['POST'])
    def clear_conversation(request):
        if "index_id" not in request.POST:
            return Response({"error": "No index_id provided"}, status=status.HTTP_400_BAD_REQUEST)
        if "email" not in request.POST:
            return Response({"error": "No email provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        index_id = request.POST["index_id"]
        email = request.POST["email"]
        user = User.objects.get(email=email)
        Index.objects.filter(user=user,index_id=index_id).update(chat_history=None)
        return Response({"message": "Conversation cleared successfully"}, status=status.HTTP_200_OK)

    @api_view(['GET'])
    def get_chat_history(request):
        if "index_id" not in request.GET:
            return Response({"error": "No index_id provided"}, status=status.HTTP_400_BAD_REQUEST)
        if "email" not in request.GET:
            return Response({"error": "No email provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        index_id = request.GET["index_id"]
        email = request.GET["email"]
        user = User.objects.get(email=email)
        chat_history = Index.objects.get(user=user,index_id=index_id).chat_history
        if chat_history == None:
            chat_history = []
        chat_history = json.loads(str(chat_history))
        return Response({"data": chat_history}, status=status.HTTP_200_OK)

