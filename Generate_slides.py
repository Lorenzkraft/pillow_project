from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat
from pilmoji import Pilmoji
from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name
import io
import emoji
from typing import Optional

class HeaderSlideCreator:
    def __init__(self, 
                 background_image_path = "./Backgrounds/light_background.png", 
                 logo_path = "./logos/logo_howai_dark_blue.png"):
        self.im = Image.open(background_image_path)
        self.width = self.im.width
        self.height = self.im.height
        self.logo = Image.open(logo_path).convert("RGBA")
        self.font = "arialbd.ttf"

    def _calculate_text_position(self, text : str, font):
        """Calculate the position of the text to be centered"""
        draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (self.width - text_width) // 2
        text_y = (self.height - text_height) // 2
        return text_x, text_y


    def create_slide(self, text : str):
        """Create a slide with the given text"""
        self.im = self.im.filter(ImageFilter.BLUR) # blur the background

        self.logo = self.logo.resize((int(self.logo.width * 0.5), 
                                      int(self.logo.height * 0.5))) # resize the logo
        
        self.im.paste(self.logo, 
                      (0, self.im.height - 200), 
                      self.logo) # paste the logo to the bottom left corner
        
        text_layer = Image.new("RGBA", 
                               (self.im.width, self.im.height), 
                               (0, 0, 0, 0)) # create a transparent layer for the text
        
        draw = ImageDraw.Draw(text_layer)
        font_bd = ImageFont.truetype(self.font, 300)
        draw.text((0, 0), text, font=font_bd, fill=(17, 18, 43, 255))

        text_x, text_y = self._calculate_text_position(text, font_bd)

        y_offset = -self.im.height // 30
       
        self.im.paste(text_layer, (text_x, text_y + y_offset), text_layer)
        return self.im
    

class ListSlideCreator:
    def __init__(
        self,
        Background_path: str = "./Backgrounds/Background_dark.png",
        header_font_path: str = "./fonts/arialbd.ttf",
        body_font_path: str = "./fonts/arial.ttf",
        header_font_size: int = 300,
        body_font_size: int = 250,
        text_color: tuple[int, int, int, int] = (255, 255, 255, 255),
        header_position: tuple[int, int] = (100, 100),
        first_item_position: tuple[int, int] = (300, 600),
        item_spacing: int = 400
    ):
        """
        Initialize the SlideGenerator with customizable parameters.
        
        Args:
            header_font_path: Path to the font file for headers
            body_font_path: Path to the font file for body text
            header_font_size: Font size for headers
            body_font_size: Font size for body text
            text_color: RGBA color tuple for text
            header_position: (x, y) position for header text
            first_item_position: (x, y) position for first list item
            item_spacing: Vertical spacing between list items
        """
        self.background = Image.open(Background_path)
        self.header_font = ImageFont.truetype(header_font_path, header_font_size)
        self.body_font = ImageFont.truetype(body_font_path, body_font_size)
        self.text_color = text_color
        self.header_position = header_position
        self.first_item_position = first_item_position
        self.item_spacing = item_spacing

    def create_slide(
        self,
        #background: Image.Image,
        header_text: str,
        list_items: list,
        custom_text_color: Optional[tuple[int, int, int, int]] = None
    ) -> Image.Image:
        """
        Create a slide with header and list items.
        
        Args:
            background: PIL Image object to use as background
            header_text: Text to display as header
            list_items: List of items to display
            custom_text_color: Optional custom text color for this specific slide
            
        Returns:
            PIL Image object with the generated slide
        """
        # Convert background to RGBA if it isn't already
        background = self.background.convert("RGBA")
        
        # Make a copy to avoid modifying the original
        slide = background.copy()
        
        # Use custom text color if provided, otherwise use default
        text_color = custom_text_color or self.text_color
        
        # Create drawing object
        draw = ImageDraw.Draw(slide)
        
        # Draw header
        draw.text(
            self.header_position,
            header_text,
            font=self.header_font,
            fill=text_color
        )
        
        # Draw list items with emoji support
        for i, item in enumerate(list_items):
            # Convert emoji aliases to Unicode
            item = emoji.emojize(item.strip(), language='alias')
            
            # Calculate position for current item
            x, y = self.first_item_position
            current_y = y + (i * self.item_spacing)
            
            # Draw item with emoji support
            with Pilmoji(slide) as pilmoji:
                pilmoji.text(
                    (x, current_y),
                    item,
                    text_color,
                    self.body_font
                )
        
        return slide

class CodeSlideCreator:
    def __init__(self, 
                 background_image_path = "./Backgrounds/gradient canvas.png", 
                 font_name='Consolas', 
                 font_size=80,
                 min_width=2500,  # Added minimum width parameter
                 padding_left=72,  # Separate padding for each side
                 padding_right=100,
                 padding_top=220,    # More padding on top
                 padding_bottom=100,  # Less padding on bottom
                 border_color=(83, 234, 205), # Neon Light effect
                 border_width=5,
                 corner_radius=20
                 ):
        self.background_image = Image.open(background_image_path)
        self.font_name = font_name
        self.font_size = font_size
        self.min_width = min_width
        self.padding = (padding_left, padding_right, padding_top, padding_bottom)
        self.border_color = (*border_color, 255)
        self.border_width = border_width
        self.corner_radius = corner_radius

    def _create_code_image(self, code : str, language : str = 'python'):
        """Create an image of the highlighted code."""
        buffer = io.BytesIO()
        
        lexer = get_lexer_by_name(language)
        if language == 'typescript':
            font_style = 'github-dark'
        else:
            font_style = 'monokai'
        style = get_style_by_name(font_style)
        
        formatter = ImageFormatter(
            font_name=self.font_name,
            font_size=self.font_size,
            line_numbers=False,
            style=style,
            line_pad=30,
            image_pad=0,
            background_color='transparent'
        )
        
        highlight(code, lexer, formatter, outfile=buffer)
        buffer.seek(0)
        
        code_image = Image.open(buffer).convert('RGBA')
        return code_image

    def _draw_control_buttons(self, draw, x0, y0):
        """Draw the three control buttons (red, yellow, green)."""
        button_positions = [
            ((255, 96, 92), 115),
            ((255, 189, 68), 200),
            ((0, 202, 78), 285)
        ]
        
        for color, x_offset in button_positions:
            draw.circle((x0 + x_offset, y0 + 100), 28, fill=color)

    def create_slide(self, code, language='python'):
        # Create the code image first to get its dimensions
        code_image = self._create_code_image(code, language)
        code_width, code_height = code_image.size
        
        # Calculate rectangle dimensions with padding
        padding_left, padding_right, padding_top, padding_bottom = self.padding
        rect_width = max(self.min_width, code_width + padding_left + padding_right)
        rect_height = code_height + padding_top + padding_bottom

        # Get the right background color for the style
        if language == 'typescript':
            background_color = (13, 17, 23) # Github Dark
        else:
            background_color = (39, 40, 34) # Monokai
        
        # Calculate rectangle position (centered horizontally)
        center_x = self.background_image.width // 2
        center_y = self.background_image.height // 2
        x0 = center_x - rect_width // 2
        y0 = center_y - rect_height // 2
        x1 = x0 + rect_width
        y1 = y0 + rect_height
        
        # Create a copy of the background image
        result = self.background_image.copy().convert('RGBA')
        
        # Create and apply the blurred background
        blurred = Image.new('RGBA', result.size, (0, 0, 0, 0))
        draw_blurred = ImageDraw.Draw(blurred)
        draw_blurred.rounded_rectangle(
            (x0, y0, x1, y1),
            radius=self.corner_radius,
            fill=(*self.border_color[:3], 255)
        )
        blurred = blurred.filter(ImageFilter.GaussianBlur(50))
        result = Image.alpha_composite(result, blurred)
        
        # Create a new layer for the main rectangle
        rectangle_layer = Image.new('RGBA', result.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(rectangle_layer)
        draw.rounded_rectangle(
            (x0, y0, x1, y1),
            radius=self.corner_radius,
            fill=(*background_color, 255),
            outline=self.border_color[:3],
            width=self.border_width
        )

        # Open the logo images
        logo_howai = Image.open("./logos/logo_howai.png")
        logo_howai = logo_howai.resize((int(logo_howai.width * 0.5), int(logo_howai.height * 0.5)))
        logo_lang = Image.open(f"./logos/{language}_logo.png")
        logo_lang = logo_lang.resize((int(logo_lang.width * 0.9), int(logo_lang.height * 0.9)))

        # Composite the rectangle layer
        result = Image.alpha_composite(result, rectangle_layer)
        
        # Calculate position for left-aligned code
        code_x = x0 + padding_left  # Left align with padding
        code_y = y0 + padding_top   # Top align with padding
        
        # Create a new layer for the code
        code_layer = Image.new('RGBA', result.size, (0, 0, 0, 0))
        code_layer.paste(code_image, (code_x, code_y))

        # paste logo_howai and logo_lang
        code_layer.paste(logo_howai,(0 , code_layer.height-200 ))
        if language == 'typescript':
            code_layer.paste(logo_lang,(x0+78, y0+60 ))
        else:
            code_layer.paste(logo_lang,(x0+60, y0+60 ))

        
        # Final composition
        result = Image.alpha_composite(result, code_layer)
        
        return result

class ImageSlideCreator:
    def __init__(self,
                 background_image_path="./Backgrounds/light_background.png",
                 logo_light_path="./logos/logo_howai.png",
                 logo_dark_path="./logos/logo_howai_dark_blue.png"):
        """
        Initialize the slide creator with background and logo images
        
        :param background_image_path: Path to the background image
        :param logo_light_path: Path to the logo for bright backgrounds
        :param logo_dark_path: Path to the logo for dark backgrounds
        """
        self.background = Image.open(background_image_path)
        self.width = self.background.width
        self.height = self.background.height
        
        # Store both logo paths
        self.logo_light_path = logo_light_path
        self.logo_dark_path = logo_dark_path
        
        # Will be set dynamically based on background brightness
        self.logo = None

    def _analyze_bottom_left_brightness(self, image):
        """
        Analyze the brightness of the bottom left corner of the image
        
        :param image: PIL Image to analyze
        :return: Average brightness (0-255)
        """
        # Define the region (bottom left, 10% of image width and height)
        width, height = image.width, image.height
        crop_width = int(width * 0.1)
        crop_height = int(height * 0.1)
        
        # Crop the bottom left corner
        bottom_left_region = image.crop((0, height - crop_height, crop_width, height))
        
        # Convert to grayscale for brightness analysis
        gray_region = bottom_left_region.convert('L')
        
        # Calculate average brightness
        brightness = ImageStat.Stat(gray_region).mean[0]
        return brightness

    def _select_logo(self, image, image_category):
        """
        Select appropriate logo based on bottom left corner brightness
        
        :param image: PIL Image to analyze
        :return: Selected logo image
        """
        # Analyze brightness
        brightness = self._analyze_bottom_left_brightness(image)
        
        # Threshold for determining bright/dark (adjust as needed)
        # Lower values mean darker, higher values mean brighter
        brightness_threshold = 127
        
        # Select and load appropriate logo
        if image_category == "wide" or image_category == "tall":
            logo_path = self.logo_dark_path 
        elif image_category == "normal" and brightness > brightness_threshold:
            logo_path = self.logo_dark_path
        elif image_category == "normal" and brightness <= brightness_threshold:
            logo_path = self.logo_light_path
        
        # Load and convert selected logo
        logo = Image.open(logo_path).convert("RGBA")
        return logo

    def create_slide(self, image_path):
        """
        Create a slide with the given image
        
        :param image_path: Path to the image to be added to the slide
        :return: Processed slide image
        """
        # Apply blur to background (optional)
        self.background = self.background.filter(ImageFilter.BLUR)
        
        # Open and process the new image
        image = Image.open(image_path)
        
        # Scale the image to fit within the slide
        image = self._scale_image(image)

        # Calculate position to center the image
        image_x, image_y = self._calculate_image_position(image)
        
        # Paste the new image onto the background
        self.background.paste(image, (image_x, image_y), image if image.mode == 'RGBA' else None)

        # determine image category
        image_category = self._determine_image_category(image)

        # Get logo position based on image category
        logo_position = self._get_logo_position(image, image_category)
        
        # Select and add logo
        logo = self._select_logo(image, image_category)
        
        # Resize logo (similar to original approach)
        resized_logo = logo.resize((int(logo.width * 0.5),
                                    int(logo.height * 0.5)))
        
        # Paste logo to bottom left corner
        self.background.paste(resized_logo, 
                      logo_position, 
                      resized_logo)
        
        return self.background
    
    def _scale_image(self, image):
        """
        Scale the image so that either width or height is 10% smaller than background
        
        :param image: PIL Image to be scaled
        :return: Scaled image
        """
        # Calculate scaling factors
        width_scale = (self.width * 0.9) / image.width
        height_scale = (self.height * 0.9) / image.height
        
        # Choose the smaller scaling factor to ensure the image fits
        scale_factor = min(width_scale, height_scale)
        
        # Calculate new dimensions
        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)
        
        # Resize the image
        return image.resize((new_width, new_height), Image.LANCZOS)
    
    def _calculate_image_position(self, image):
        """
        Calculate the position to center the image on the background
        
        :param image: PIL Image to be centered
        :return: Tuple of x, y coordinates
        """
        x = (self.width - image.width) // 2
        y = (self.height - image.height) // 2
        return x, y
    
    def _determine_image_category(self, image):
        """
        Determine the category of the image based on its aspect ratio
        
        :param image: PIL Image 
        :return: category
        """
        if image.width / image.height > 2:
            return "wide"
        elif 2 > image.width / image.height > 1:
            return "normal"
        else:
            return "tall"
    
    def _get_logo_position(self, image, image_category):
        """
        Get the position for the logo based on the image category
        
        :param image_category: Category of the image
        :return: Logo position
        """
        # Calculate position of bottom left corner
        x, y = self._calculate_image_position(image)
        if image_category == "wide" or image_category == "tall":
            return (0, self.background.height - 200)
        else:
            return (x, y + image.height - 200)

if __name__ == "__main__":
    creator = HeaderSlideCreator(3840, 2160, vertical_offset=120)  # Added vertical offset
    image = creator.create_slide("howai.works", font_size=300)
    image.show()