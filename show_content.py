import json

def show(filepath, label):
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    print(f"\n=== {label} ===")
    if isinstance(data, list) and data and 'slide' in data[0]:
        for s in data:
            title = s['title']
            imgs = [i['file'] for i in s['images']]
            slide_n = s['slide']
            print(f"Slide {slide_n}: [{title}] imgs={imgs}")
            for c in s['content'][:4]:
                print(f"  - {c['text'][:90]}")
    elif isinstance(data, list):
        for p in data[:30]:
            print(f"  [{p.get('style','')}] {p.get('text','')[:90]}")
    elif isinstance(data, dict):
        print("Paragraphs:")
        for p in data.get('paragraphs', [])[:30]:
            print(f"  [{p.get('style','')}] {p.get('text','')[:90]}")
        print("Images:", [i['file'] for i in data.get('images', [])])

show(r'd:\presentation\extracted\main_pptx.json', 'MAIN PPTX')
show(r'd:\presentation\extracted\demo_pptx.json', 'DEMO PPTX')
show(r'd:\presentation\extracted\lecture_docx.json', 'LECTURE DOCX')
show(r'd:\presentation\extracted\tests_docx.json', 'TESTS DOCX')
