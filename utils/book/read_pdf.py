import fitz  # PyMuPDF

def read_pdf(file_path, page_nums=None):
    combined_text = ''  # Initialize a string to hold the combined text

    # Open the PDF file
    pdf_document = fitz.open(file_path)
    print(f"Number of pages: {pdf_document.page_count}")

    # Set the number of pages to read (all pages if page_nums is None)
    total_pages = pdf_document.page_count if page_nums is None else min(page_nums, pdf_document.page_count)

    # Iterate through each page up to the specified number
    for page_num in range(total_pages):
        page = pdf_document[page_num]
        text = page.get_text("text")  # Extract text from the page
        combined_text += text  # Append the text from each page

    # Close the document
    pdf_document.close()
    return combined_text  # Return the combined text from all pages