from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from difflib import SequenceMatcher 
from glob import glob
from uuid import uuid4


def model_form_upload(request):
    if request.method == 'POST' and request.FILES['file_to_check_for']:
        file_to_check_for = request.FILES['file_to_check_for']
        fs = FileSystemStorage()
        file_name = file_to_check_for.name
        file_url = "documents/files_to_check_plagiarism_with/"+ file_name.split(".")[0] + "-"+ str(uuid4())+ "." + file_name.split(".")[1]
        
        plagiarism_check_result = check_plagiarism_score(file_to_check_for, file_url)

        uploaded_file_url = ""
        if request.POST.get('save-or-not') == "SAVE_FILE":
            filename = fs.save(file_url, file_to_check_for)
            uploaded_file_url = fs.url(filename)

        if uploaded_file_url != "" :
            result = {
               'uploaded_file_url': uploaded_file_url,
                'plagiarism_check_result': plagiarism_check_result
            }
        else:
            result = {
               'plagiarism_check_result': plagiarism_check_result
            }

        file_to_check_for.close()
        return render(request, 'checkplagiarism/model_form_upload.html', result)

    return render(request, 'checkplagiarism/model_form_upload.html')


def check_plagiarism_score(file_for_checking, file_name_for_checking):
    file_types_to_check_with = ['txt','xml', 'csv'] #, 'pdf']
    file_names_to_check_with = []
    result = {}

    # with open(file_name_for_checking) as file_for_checking:

    for file_type in file_types_to_check_with:
        for file_name in glob("documents/files_to_check_plagiarism_with/*." + file_type):
            if(file_name != file_name_for_checking):
                file_names_to_check_with.append(file_name)
    
    file_content_for_checking = file_for_checking.read().strip().decode("utf-8")
    # file_content_for_checking = file_content_for_checking.replace("b\'", "").replace("\r\r\n\'", "")
    for file_name_to_check_with in file_names_to_check_with:
        print("Checking with : ", file_name_to_check_with)
        with open(file_name_to_check_with) as file_to_check_with:
            file_contain_to_check_with = file_to_check_with.read().strip()
            file_to_check_with.close()

            print( "file_contain_to_check_with:", file_contain_to_check_with)
            print("file_content_for_checking:", file_content_for_checking )
            similarity_ratio = SequenceMatcher(None, file_contain_to_check_with, file_content_for_checking).ratio()
            similarity_ratio = int(similarity_ratio*100) 
            print("Similarity Ratio: ", similarity_ratio)
            result[file_name_to_check_with.replace("documents/files_to_check_plagiarism_with/","")] = similarity_ratio
                    
    return result


        
