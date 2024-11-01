from bs4 import BeautifulSoup as bs
from BS_extension import MyDivExtension
import markdown
from Generate_slides import HeaderSlideCreator, ListSlideCreator, CodeSlideCreator, ImageSlideCreator
import os
import re

class Parse_markdown:
    def __init__(self, markdown_file_path, slides_director) -> None:
        self.markdown_file_path = markdown_file_path
        self.slides_directory = slides_director

    def _create_soup_object(self):
        # open markdown file
        with open(self.markdown_file_path, 'r') as f:
            data = f.read()

        # parse markdown into html
        html = markdown.markdown(data, extensions=[MyDivExtension()])

        # parse markdown file
        soup = bs(html, 'html.parser')
        return soup
        
    def _create_header(self, element):
        header_text = element.text
        Creator = HeaderSlideCreator()
        return Creator.create_slide(header_text)
    
    def _get_h1_text(self, element):
        header_text = element.text
        return header_text

    def _create_list(self, element):
        header_text, list_items = self._get_list_header_and_items(element)            
        Creator = ListSlideCreator()
        return Creator.create_slide(header_text, list_items)
    
    def _get_list_header_and_items(self, element):
        for header in element.find_all('h3'):
            header_text = header.text
            
        for ul in element.find_all('ul'):
            list_items = ul.find_all('li')
            list_items = [item.text for item in list_items]
        
        return header_text, list_items

    def _create_code(self, element):
        code_language = self._get_code_language_title_content(element)[0]
        code_snippet = self._get_code_language_title_content(element)[2]

        Creator = CodeSlideCreator()
        return Creator.create_slide(code_snippet, code_language)
    
    def _get_code_language_title_content(self, element):
        All = element.text.split('\n', 1)
        language_and_title = All[0]
        # split the string into the language and the title except in the first line is only one word
        if " " not in language_and_title:
            code_language = language_and_title
            code_title = "no_title"
        else:
            code_language, code_title = re.split(r'\s', All[0], 1)
        
        code_snippet = All[1]
        return code_language, code_title, code_snippet

    def _create_image(self, element):
        image_path = element['src']
        Creator = ImageSlideCreator(image_path)
        return Creator.create_slide(image_path)
    
    def _get_image_alt(self, element):
        image_alt = element['alt']
        return image_alt
    """
    def parse(self):
        soup = self._create_soup_object()

        for i, element in enumerate(soup.find_all()):
            if element.name == 'h1':
                header = self._create_header(element)
                header.save(os.path.join(self.slides_directory, f"header_{i}.png"))
            elif element.name == 'div' and element['class'] == ['mydiv']:
                resulting_list = self._create_list(element)
                resulting_list.save(os.path.join(self.slides_directory, f"list_{i}.png"))
            elif element.name == 'code':
                code = self._create_code(element)
                code.save(os.path.join(self.slides_directory, f"code_{i}.png"))
            elif element.name == 'img':
                image = self._create_image(element)
                image.save(os.path.join(self.slides_directory, f"image_{i}.png"))
            else:
                pass
    """
    
    
    def parse(self):
        soup = self._create_soup_object()
        markdown_lines = self._read_markdown_lines()  # Reads lines from the original Markdown file

        for i, element in enumerate(soup.find_all()):
            file_path = None
            link_text = ""

            # Process each element and generate a file path
            if element.name == 'h1':
                header_text = self._get_h1_text(element)
                header_text_without_spaces = header_text.replace(" ", "_")  
                header_slide= self._create_header(element)
                file_path = os.path.join(self.slides_directory, 
                                         f"{i:02}_header_{header_text_without_spaces}.png")
                header_slide.save(file_path)
                link_text = f"![{i:02}_header_{header_text}]({file_path})"
                
            elif element.name == 'div' and element['class'] == ['mydiv']:
                list_title = self._get_list_header_and_items(element)[0]
                list_title_without_spaces = list_title.replace(" ", "_")
                list_slide = self._create_list(element)
                file_path = os.path.join(self.slides_directory, 
                                         f"{i:02}_list_{list_title_without_spaces}.png")
                list_slide.save(file_path)
                link_text = f"![{i:02}_list_{list_title}]({file_path})"

            elif element.name == 'code':
                code_title = self._get_code_language_title_content(element)[1]
                code_title_without_spaces = code_title.replace(" ", "_")
                code_slide = self._create_code(element)
                file_path = os.path.join(self.slides_directory, 
                                         f"{i:02}_code_{code_title_without_spaces}.png")
                code_slide.save(file_path)
                link_text = f"![{i:02}_code_{code_title}]({file_path})"
            
            elif element.name == 'img':
                image_alt = self._get_image_alt(element)
                image_alt_without_spaces = image_alt.replace(" ", "_")
                image_slide = self._create_image(element)
                file_path = os.path.join(self.slides_directory, 
                                         f"{i:02}_image_{image_alt_without_spaces}.png")
                image_slide.save(file_path)
                link_text = f"![{i:02}_image_{image_alt}]({file_path})"

            # Insert the generated link back into the markdown content at the right position
            if file_path and link_text:
                element_position = self._find_element_position_in_markdown(markdown_lines, element)
                if element_position is not None:
                    markdown_lines.insert(element_position + 1, link_text)  # Inserts the link just after the element
                else:
                    print(f"Warning: Could not find position for element '{element}' in the original Markdown.")

        # Write the modified Markdown content back to the file
        with open(self.markdown_file_path, 'w') as md_file:
            md_file.write("\n".join(markdown_lines))
        print("Markdown file updated with links to generated files.")

    # Helper functions
    def _read_markdown_lines(self):
        with open(self.markdown_file_path, 'r') as md_file:
            return md_file.readlines()
        
    def _find_element_position_in_markdown(self, markdown_lines: list, element) -> int:
        """
        Find the position of a BeautifulSoup element in the original markdown file.
        
        Args:
            markdown_lines (list): List of lines from the original markdown file
            element (bs4.element.Tag): BeautifulSoup element to find
            
        Returns:
            int: Line number (index) where the element was found, or None if not found
        """
        # Convert markdown_lines to a list if it's not already
        if isinstance(markdown_lines, str):
            markdown_lines = markdown_lines.split('\n')
        
        # Remove any trailing newlines from the lines
        markdown_lines = [line.strip() for line in markdown_lines]
        
        # Different elements require different search strategies
        if element.name == 'h1':
            # For headers, look for lines starting with #
            header_text = self._get_h1_text(element)
            for i, line in enumerate(markdown_lines):
                if line.strip().startswith('# ') and header_text in line:
                    return i
        
        elif element.name == 'div' and element.get('class') == ['mydiv']:
            # For lists, find the header first
            header_text, _ = self._get_list_header_and_items(element)
            for i, line in enumerate(markdown_lines):
                if line.strip().startswith('### ') and header_text in line:
                    return i
        
        elif element.name == 'code':
            # For code blocks, look for the language identifier and content
            code_lang, code_title, code_snippet = self._get_code_language_title_content(element)
            code_start = f"```{code_lang}"
            if " " not in code_lang:
                code_start = f"```{code_lang}"
            else:
                code_start = f"```{code_lang} {code_title}"
                
            for i, line in enumerate(markdown_lines):
                if line.strip() == code_start:
                    return i
        
        elif element.name == 'img':
            # For images, look for markdown image syntax
            img_alt = self._get_image_alt(element)
            img_src = element['src']
            img_pattern = f"![{img_alt}]({img_src})"
            
            for i, line in enumerate(markdown_lines):
                if img_pattern in line:
                    return i
        
        # Return None if element not found
        return None
    """ ChatGPT solution v2    
    def _find_element_position_in_markdown(self, markdown_lines, element):
        start_idx = None
        end_idx = None

        if element.name == 'h1':
            # Single-line header
            target_text = f"# {element.get_text().strip()}"
           
            for idx, line in enumerate(markdown_lines):
                if target_text in line:
                    start_idx = end_idx = idx
                    break

        elif element.name == 'div' and element['class'] == ['mydiv']:
            # Multi-line div with list items
            h3_text = f"### {element.find('h3').get_text().strip()}" if element.find('h3') else ""
            list_items_text = "\n".join([f"- {li.get_text().strip()}" for li in element.find_all('li')])
            target_text = f"{h3_text}\n{list_items_text}".strip()
            
            # Find start and end of this block in markdown_lines
            for idx in range(len(markdown_lines)):
                joined_lines = "\n".join(markdown_lines[idx:idx + len(target_text.splitlines())]).strip()
                if target_text in joined_lines:
                    start_idx = idx
                    end_idx = start_idx + len(target_text.splitlines()) - 1
                    break

        elif element.name == 'code':
            # Multi-line code block
            code_lines = element.get_text().strip().split('\n')
            language_line = f"```{code_lines[0]}" if len(code_lines) > 1 and code_lines[0].isalpha() else "```"
            code_content = "\n".join(code_lines[1:]) if len(code_lines) > 1 else element.get_text().strip()
            target_text = f"{language_line}\n{code_content}\n```"
            
            # Find start and end of code block
            for idx in range(len(markdown_lines)):
                joined_lines = "\n".join(markdown_lines[idx:idx + len(target_text.splitlines())]).strip()
                if target_text in joined_lines:
                    start_idx = idx
                    end_idx = start_idx + len(target_text.splitlines()) - 1
                    break

        elif element.name == 'img':
            # Single-line image
            img_alt = element.get('alt', 'image')
            img_src = element['src']
            target_text = f"![{img_alt}]({img_src})"
            
            for idx, line in enumerate(markdown_lines):
                if target_text in line:
                    start_idx = end_idx = idx
                    break

        # Return the end of the element block for multi-line elements
        return end_idx
    """

    """  ChatGPT solution v1
    def _find_element_position_in_markdown(self, markdown_lines, element):
        # Convert HTML elements to approximate Markdown representations
        target_text = ""
        if element.name == 'h1':
            target_text = f"# {element.get_text().strip()}"
        elif element.name == 'div' and element['class'] == ['mydiv']:
            target_text = element.get_text().strip()  # assuming div contents match directly
        elif element.name == 'code':
            target_text = f"```{element.get_text().strip()}```"
        elif element.name == 'img' and element.has_attr('src'):
            target_text = f"![{element.get('alt', 'image')}]({element['src']})"
        else:
            return None  # No matching Markdown pattern

        # Debug: Print target text for verification
        print(f"Searching for: {target_text}")

        # Find the line in markdown_lines that matches the target_text
        for idx, line in enumerate(markdown_lines):
            if target_text in line:
                return idx  # Return the line index where the element was found

        return None  # Element not found
 
    """


if __name__ == "__main__":
    parser = Parse_markdown("test.md", "./Created_Slides")
    parser.parse()