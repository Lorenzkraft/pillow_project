import markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from bs4 import BeautifulSoup as bs
import xml.etree.ElementTree as ET

class MyDivExtension(Extension):
    """
    Custom Markdown extension to wrap content in a <div> with the "mydiv" class.
    """
    class MyDivProcessor(BlockProcessor):
        def test(self, parent, block):
            return block.startswith('###mydiv\n')

        def run(self, parent, blocks):
            block = blocks.pop(0)
            div = ET.SubElement(parent, 'div')
            div.set('class', 'mydiv')
            self.parser.parseBlocks(div, [block[8:].strip()])

    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.parser.blockprocessors.register(self.MyDivProcessor(md.parser), 'mydiv', 175)