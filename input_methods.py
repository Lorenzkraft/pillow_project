import re

class InputMethods:
    @staticmethod
    def get_input_h1(element):
        header_text = element.text
        return header_text
    
    @staticmethod
    def get_input_img(element):
        img_src = element["src"]
        img_alt = element["alt"].replace(" ", "_")
        return img_src
    
    @staticmethod
    def get_input_code(element):
        All = element.text.split('\n', 1)
        language_and_title = All[0]
        # split the string into the language and the title except in the first line is only one word
        if " " not in language_and_title:
            code_language = language_and_title
            code_title = "no_title"
        else:
            code_language, code_title = re.split(r'\s', All[0], 1)
        
        code_snippet = All[1]
        return code_snippet, code_language#, code_title
    
    @staticmethod
    def get_input_list(element):
        for header in element.find_all('h3'):
            header_text = header.text
            
        for ul in element.find_all('ul'):
            list_items = ul.find_all('li')
            list_items = [item.text for item in list_items]
        
        return header_text, list_items
    
class FileNameMethods:    
    @staticmethod
    def get_file_name_h1(element):
        header_text = element.text.replace(" ", "_") # replace spaces with underscores
        return header_text
    
    @staticmethod
    def get_file_name_img(element):
        img_alt = element["alt"].replace(" ", "_")
        return img_alt
    
    @staticmethod
    def get_file_name_code(element):
        All = element.text.split('\n', 1)
        language_and_title = All[0]
        # split the string into the language and the title except in the first line is only one word
        if " " not in language_and_title:
            code_language = language_and_title
            code_title = "no_title"
        else:
            code_language, code_title = re.split(r'\s', All[0], 1)
        
        code_title = code_title.replace(" ", "_")
        return code_title
    
    @staticmethod
    def get_file_name_list(element):
        for header in element.find_all('h3'):
            header_text = header.text.replace(" ", "_")

        return header_text