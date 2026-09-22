"""Export the project report to standalone HTML and a Word document (stdlib only)."""
import base64
import html
from pathlib import Path
import re
import struct
import zipfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
source = (ROOT/'PROJECT_REPORT.md').read_text(encoding='utf-8').splitlines()
word = []
web = []
media = []


def clean(text):
    return text.replace('`', '').replace('**', '')


def paragraph(text, style=None):
    prop = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ''
    return f'<w:p>{prop}<w:r><w:t xml:space="preserve">{escape(clean(text))}</w:t></w:r></w:p>'


i = 0
while i < len(source):
    line = source[i]
    if not line.strip():
        i += 1
        continue
    image = re.fullmatch(r'!\[(.*?)\]\((.*?)\)', line)
    if image:
        label, relative = image.groups()
        data = (ROOT/relative).read_bytes()
        width, height = struct.unpack('>II', data[16:24])
        factor = min(6.1/width, 7.0/height)
        cx, cy = int(width*factor*914400), int(height*factor*914400)
        number = len(media)+1
        media.append(data)
        word.append(f'<w:p><w:r><w:drawing><wp:inline><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{number}" name="Screenshot {number}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="{number}" name="Screenshot {number}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="rIdImage{number}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
        web.append(f'<figure><img alt="{html.escape(label)}" src="data:image/png;base64,{base64.b64encode(data).decode()}"><figcaption>{html.escape(label)}</figcaption></figure>')
    elif line.startswith('#'):
        level = len(line)-len(line.lstrip('#'))
        text = line[level:].strip()
        word.append(paragraph(text, 'Title' if level == 1 else 'Heading'+str(level-1)))
        web.append(f'<h{level}>{html.escape(text)}</h{level}>')
    elif line.startswith('|'):
        rows=[]
        while i < len(source) and source[i].startswith('|'):
            cells=[cell.strip() for cell in source[i].strip('|').split('|')]
            if not all(re.fullmatch(r'[-: ]+',cell) for cell in cells): rows.append(cells)
            i+=1
        word.append('<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders>'+''.join(f'<w:{side} w:val="single" w:sz="4" w:color="CCCCCC"/>' for side in ['top','left','bottom','right','insideH','insideV'])+'</w:tblBorders></w:tblPr>'+''.join('<w:tr>'+''.join('<w:tc>'+paragraph(cell)+'</w:tc>' for cell in row)+'</w:tr>' for row in rows)+'</w:tbl>')
        web.append('<table>'+''.join('<tr>'+''.join(f'<{"th" if n==0 else "td"}>{html.escape(clean(cell))}</{"th" if n==0 else "td"}>' for cell in row)+'</tr>' for n,row in enumerate(rows))+'</table>')
        continue
    elif line.startswith('```'):
        code=[];i+=1
        while i < len(source) and not source[i].startswith('```'):
            code.append(source[i]);word.append(paragraph(source[i],'Code'));i+=1
        web.append('<pre>'+html.escape('\n'.join(code))+'</pre>')
    else:
        word.append(paragraph(line))
        web.append('<p>'+html.escape(clean(line))+'</p>')
    i+=1

style='body{font:16px/1.6 Arial,sans-serif;max-width:1000px;margin:50px auto;padding:0 24px;color:#18263a}h1,h2,h3{color:#123e56}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #ccc;padding:10px;text-align:left;vertical-align:top}th{background:#edf4f7}pre{white-space:pre-wrap;background:#edf4f7;padding:16px}figure{text-align:center;page-break-inside:avoid}img{max-width:100%;max-height:900px}figcaption{font-size:13px;color:#536070}@media print{body{margin:0;font-size:11pt}h2,h3{break-after:avoid}img{max-height:8in}pre{font-size:9pt}}'
(ROOT/'Project_3_Report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Project 3 Report</title><style>'+style+'</style><body>'+''.join(web)+'</body></html>',encoding='utf-8')
ns='xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"'
document=f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {ns}><w:body>'+''.join(word)+'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1000" w:bottom="1000" w:left="1000"/></w:sectPr></w:body></w:document>'
styles='<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="140"/></w:pPr></w:pPrDefault></w:docDefaults>'
for name,size in [('Title',36),('Heading1',30),('Heading2',25),('Code',18)]:
    styles+=f'<w:style w:type="paragraph" w:styleId="{name}"><w:name w:val="{name}"/><w:pPr><w:keepNext/></w:pPr><w:rPr><w:sz w:val="{size}"/>'+('<w:b/>' if name!='Code' else '<w:rFonts w:ascii="Consolas"/>')+'</w:rPr></w:style>'
styles+='</w:styles>'
with zipfile.ZipFile(ROOT/'Project_3_Report.docx','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>')
    z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    z.writestr('word/document.xml',document)
    z.writestr('word/styles.xml',styles)
    relationships='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    for number,data in enumerate(media,1):
        z.writestr(f'word/media/image{number}.png',data)
        relationships+=f'<Relationship Id="rIdImage{number}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image{number}.png"/>'
    z.writestr('word/_rels/document.xml.rels',relationships+'</Relationships>')
print('Created Project_3_Report.docx and Project_3_Report.html with',len(media),'screenshots.')
