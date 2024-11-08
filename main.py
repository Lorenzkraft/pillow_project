from parse import Parser
import os

if __name__ == "__main__":
    markdown_path = "test.md"
    created_slides_path = "Created_Slides"
    parser = Parser(markdown_path, created_slides_path)
    parser.parse()
