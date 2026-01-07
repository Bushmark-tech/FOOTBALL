import codecs

# Read the template content from your request
template_content = r'''TEMPLATE_CONTENT_HERE'''

# Write to file
with codecs.open(r'templates\predictor\result.html', 'w', 'utf-8') as f:
    f.write(template_content)
    
print('File written successfully')
