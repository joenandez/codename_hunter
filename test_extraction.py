from hunter.parsers import ContentExtractor

def main():
    with open('temp_sdk_doc.html', 'r') as f:
        html = f.read()
    
    print("HTML length:", len(html))
    
    extractor = ContentExtractor()
    results = extractor.extract_from_html(html)
    
    print(f"\nNumber of extracted results: {len(results)}")
    print('\n=== Extracted Content ===\n')
    for i, result in enumerate(results):
        print(f"\n--- Result {i+1} ({result.content_type}) ---")
        print(result.content)

if __name__ == '__main__':
    main() 