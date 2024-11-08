from bs4 import BeautifulSoup as bs
from BS_extension import MyDivExtension
import markdown
from Generate_slides import HeaderSlideCreator, ListSlideCreator, CodeSlideCreator, ImageSlideCreator
import os
from input_methods import InputMethods, FileNameMethods

class Parser:
    def __init__(self, markdown_path, created_slides_path) -> None:
        self.created_slides_path = created_slides_path
        self.markdown_path = markdown_path
        self.slide_counter = 0
        
        self.input_extractors = {
            'h1': InputMethods.get_input_h1,
            'img': InputMethods.get_input_img,
            'code': InputMethods.get_input_code,
            ('div', 'mydiv'): InputMethods.get_input_list  # Maps div with class 'mydiv' to get_input_list
        }
        self.slide_creators = {
            'h1': HeaderSlideCreator,
            'img': ImageSlideCreator,
            'code': CodeSlideCreator,
            ('div', 'mydiv'): ListSlideCreator
        }
        self.file_name_extractors = {
            'h1': FileNameMethods.get_file_name_h1,
            'img': FileNameMethods.get_file_name_img,
            'code': FileNameMethods.get_file_name_code,
            ('div', 'mydiv'): FileNameMethods.get_file_name_list
        }            
            


    def _create_soup(self):
        with open(self.markdown_path) as f:
            text = f.read()
        html = markdown.markdown(text, extensions=[MyDivExtension()])
        return bs(html, "html.parser")
    
    # Function to get the indices of elements to process
    @staticmethod
    def _get_element_indices(soup):
        def element_filter(tag):
            # Check if tag is 'h1', 'img', or 'code'
            if tag.name in ["h1", "img", "code"]:
                return True
            # Check if tag is 'div' with class 'mydiv'
            if tag.name == "div" and tag.get("class") == ["mydiv"]:
                return True
            return False

        # Return the indices of elements in 'soup' that match the filter
        return [i for i, element in enumerate(soup.find_all()) if element_filter(element)]
    
    def generate_href_html(self):
        html_for_editing = self._create_soup()
        all_elements = list(html_for_editing.find_all())
        element_indices = self._get_element_indices(html_for_editing)

        # Loop over each index and insert a new paragraph with the count
        for count, index in enumerate(element_indices, start=1):
            # Find the corresponding element in 'soup_md'
            corresponding_element = all_elements[index]
            # get filename
            filename = [f for f in os.listdir("created_slides") if f.startswith(f"{count:02}")][0]
            # insert an a tag with the href to the created image
            link_tag = html_for_editing.new_tag("a", href=f"./created_slides/{filename}")
            corresponding_element.append(link_tag)

        return html_for_editing
    
    def _save_slide(self, image, filename):
        # Ensure directory exists
        os.makedirs(self.created_slides_path, exist_ok=True)
        
        # Create full path for saving
        full_path = os.path.join(self.created_slides_path, filename)
        
        # Save the image
        image.save(full_path)
        print(f"Slide saved at {full_path}")
                

    def parse(self):
        soup = self._create_soup()

        for element in soup.find_all():
            # Check if both element name and class match a specific tuple key
            if (element.name, element.get('class')[0] if element.get('class') else None) in self.input_extractors:
                key = (element.name, element.get('class')[0])
            else:
                key = element.name

            try:
                # Extract input for the Slide creation from element
                input = self.input_extractors[key](element)

                # Instantiate the correct SlideCreator class and create the slide
                slide_creator = self.slide_creators[key]()
                if key == 'img' or key == 'h1':
                    slide = slide_creator.create_slide(input)
                elif key == 'code' or key == ('div', 'mydiv'):
                    slide = slide_creator.create_slide(*input)
                self.slide_counter += 1
    	        # Get file name 
                file_name = f"{self.slide_counter:02}_{element.name}_{self.file_name_extractors[key](element)}.png"
                

                # Save the slide
                self._save_slide(slide, file_name)



            except KeyError:
                print(f"Element {element.name} not supported")
                
        pass